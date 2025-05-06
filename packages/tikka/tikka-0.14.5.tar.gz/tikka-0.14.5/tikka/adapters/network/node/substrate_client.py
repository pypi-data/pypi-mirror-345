# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import json
import logging
import os
from dataclasses import dataclass
from hashlib import blake2b
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import xxhash
from scalecodec import GenericCall, GenericExtrinsic, ScaleBytes, ScaleType, ss58_decode
from scalecodec.base import RuntimeConfigurationObject, ScaleDecoder
from scalecodec.type_registry import load_type_registry_preset
from urllib3.util import parse_url
from websocket import WebSocket, create_connection

from tikka.libs.keypair import Keypair


@dataclass
class ExtrinsicReceipt:
    """
    ExtrinsicReceipt class
    """

    extrinsic_hash: str
    block_hash: Optional[str] = None
    finalized: bool = False
    is_success: bool = False


class SubstrateClient:
    """
    SubstrateClient class
    """

    METADATA_FILE_BASENAME = "substrate_client_metadata_"
    CONNECTIONS_POOL_SIZE = 5

    def __init__(
        self,
        url: str,
        websocket_options: Optional[dict] = None,
        metadata_dir: str = "~/.substrate_client",
    ):
        """
        Init SubstrateClient instance

        :param url:
        """
        # static variables
        self.url: str = url
        self.metadata_dir = metadata_dir
        self.connections_pool: Queue = Queue(self.CONNECTIONS_POOL_SIZE)
        # Websocket connection options
        self.websocket_options = websocket_options or {}

        # variables per connection
        self._request_id: Dict[int, int] = {}
        self._rpc_message_queue: Dict[int, list] = {}

        supported_schemes = ("ws", "wss")
        url_scheme = parse_url(self.url).scheme
        if url_scheme not in supported_schemes:
            raise Exception(f"Scheme {url_scheme} not supported")

        if not os.path.exists(Path(metadata_dir).expanduser()):
            os.mkdir(Path(metadata_dir).expanduser())

        # create pool of connections
        logging.debug("Connecting to {} ...".format(self.url))
        for i in range(self.CONNECTIONS_POOL_SIZE):
            connection: WebSocket = create_connection(
                self.url, **self.websocket_options
            )
            self.connections_pool.put(connection)
            self._request_id[connection.fileno()] = 0
            self._rpc_message_queue[connection.fileno()] = []

        runtime_info = self.get_runtime_info()
        if runtime_info is None:
            raise Exception("No runtime info found")
        self.transaction_version = runtime_info["transactionVersion"]
        self.runtime_version = runtime_info["specVersion"]
        logging.debug(f"runtime version: {self.runtime_version}")
        logging.debug(f"transaction version: {self.transaction_version}")

        self.runtime_config: RuntimeConfigurationObject = RuntimeConfigurationObject()

        # This types are all hardcoded types needed to decode metadata types
        self.runtime_config.update_type_registry(load_type_registry_preset(name="core"))

        self.metadata: ScaleType = self.get_metadata()

        # Check if PortableRegistry is present in metadata (V14+), otherwise fall back on legacy type registry (<V14)
        if self.implements_scaleinfo():
            self.runtime_config.add_portable_registry(self.metadata)

        # Set active runtime version
        self.runtime_config.set_active_spec_version_id(self.runtime_version)
        self.runtime_config.ss58_format = self.get_constant("System", "SS58Prefix")

        # Set runtime compatibility flags
        try:
            _ = self.runtime_config.create_scale_object("sp_weights::weight_v2::Weight")
            self.runtime_config.update_type_registry_types(
                {"Weight": "sp_weights::weight_v2::Weight"}
            )
        except NotImplementedError:
            self.runtime_config.update_type_registry_types({"Weight": "WeightV1"})

    def close(self):
        """
        Close websocket connections in pool

        :return:
        """
        while not self.connections_pool.not_empty:
            connection: WebSocket = self.connections_pool.get()
            connection.close()
            connection_id = connection.fileno()
            del self._request_id[connection_id]
            del self._rpc_message_queue[connection_id]

        logging.debug("SubstrateClient connection closed.")

    def get_constant(self, module_name, constant_name) -> Optional[ScaleType]:
        """
        Returns the decoded `ScaleType` object of the constant for given module name, call function name

        :param module_name: Module name
        :param constant_name: Parameter name

        :return:
        """
        constant = None
        for module_idx, module in enumerate(self.metadata.pallets):

            if module_name == module.name and module.constants:

                for _constant in module.constants:
                    if constant_name == _constant.value["name"]:
                        constant = _constant

                if constant:

                    obj = self.runtime_config.create_scale_object(
                        type_string=constant.type,
                        data=ScaleBytes(constant.constant_value),
                        metadata=self.metadata,
                    )

                    obj.decode(check_remaining=True)

                    constant = obj.value

        return constant

    def rpc_request(
        self,
        method: str,
        params: Optional[list] = None,
        result_handler: Optional[Callable] = None,
    ) -> dict:
        """
        Send JSON-RPC request to server

        :param method: Method name
        :param params: list of parameters
        :param result_handler: Function to call to handle result

        :return:
        """
        # get a connection from pool
        connection: WebSocket = self.connections_pool.get()
        connection_id = connection.fileno()

        self._request_id[connection_id] += 1
        request_id = self._request_id[connection_id]

        params = params or []
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id,
        }

        logging.debug('RPC request #{}: "{}"'.format(request_id, method))

        connection.send(json.dumps(request))

        update_nr = 0
        json_body = None
        subscription_id = None

        while json_body is None:
            # Search for subscriptions
            for message, remove_message in list_remove_iter(
                self._rpc_message_queue[connection_id]
            ):

                # Check if result message is matching request ID
                if "id" in message and message["id"] == request_id:

                    remove_message()

                    # Check if response has error
                    if "error" in message:
                        self.connections_pool.put(
                            connection
                        )  # Return connection back to the pool
                        raise Exception(message["error"])

                    # If result handler is set, pass result through and loop until handler return value is set
                    if callable(result_handler):

                        # Set subscription ID and only listen to messages containing this ID
                        subscription_id = message["result"]
                        logging.debug(
                            f"Websocket subscription [{subscription_id}] created"
                        )

                    else:
                        json_body = message

            # Process subscription updates
            for message, remove_message in list_remove_iter(
                self._rpc_message_queue[connection_id]
            ):
                # Check if message is meant for this subscription
                if (
                    callable(result_handler)
                    and "params" in message
                    and message["params"]["subscription"] == subscription_id
                ):

                    remove_message()

                    logging.debug(
                        f"Websocket result [{subscription_id} #{update_nr}]: {message}"
                    )

                    # Call result_handler with message for processing
                    callback_result = result_handler(
                        message, update_nr, subscription_id
                    )
                    if callback_result is not None:
                        json_body = callback_result

                    update_nr += 1

            # Read one more message to queue
            if json_body is None:
                self._rpc_message_queue[connection_id].append(
                    json.loads(connection.recv())
                )

        self.connections_pool.put(connection)  # Return connection back to the pool

        return json_body

    def get_runtime_info(self) -> Optional[Any]:
        """
        Return runtime info from server for metadata caching

        :return:
        """
        response = self.rpc_request("state_getRuntimeVersion")
        if "error" in response:
            raise Exception(response["error"]["message"])

        return response.get("result")

    def get_metadata(self) -> ScaleType:
        """
        Return metadata json from server

        :return:
        """
        metadata_filepath = (
            Path(self.metadata_dir)
            .joinpath(self.METADATA_FILE_BASENAME + str(self.runtime_version) + ".json")
            .expanduser()
        )

        if not os.path.exists(metadata_filepath):
            response = self.rpc_request("state_getMetadata")
            metadata_scale_encoded = response.get("result")
            with open(metadata_filepath, "w") as file:
                json.dump(metadata_scale_encoded, file)
            logging.debug(f"metadata saved to {metadata_filepath}")
        else:
            with open(metadata_filepath, "r") as file:
                metadata_scale_encoded = json.load(file)
            logging.debug(f"metadata loaded from {metadata_filepath}")

        # Decode retrieved metadata from the RPC
        metadata = self.runtime_config.create_scale_object(
            "MetadataVersioned", data=ScaleBytes(metadata_scale_encoded)
        )
        metadata.decode()

        return metadata

    def query(
        self, module: str, storage_function: str, params: Optional[list] = None
    ) -> Any:
        """
        Return a ScaleType instance of the response of the query

        :param module: Module name
        :param storage_function: Storage function name
        :param params: List of parameters

        :return:
        """
        if self.metadata is None:
            raise Exception("Metadata empty")

        # Search storage call in metadata
        metadata_pallet = self.metadata.get_metadata_pallet(module)

        if not metadata_pallet:
            raise Exception(f'Pallet "{module}" not found')

        storage_item = metadata_pallet.get_storage_function(storage_function)

        if not metadata_pallet or not storage_item:
            raise Exception(f'Storage function "{module}.{storage_function}" not found')

        params = params or []
        _scale_type = self.get_scale_type(module, storage_function, params)
        _storage_key = _scale_type.storage_hash

        # SCALE type string of value
        param_types = storage_item.get_params_type_string()
        # value_scale_type = storage_item.get_value_type_string()

        if len(params) != len(param_types):
            raise ValueError(
                f"Storage function requires {len(param_types)} parameters, {len(params)} given"
            )

        response = self.rpc_request("state_getStorage", [_storage_key])

        if "error" in response:
            raise Exception(response["error"]["message"])

        scale_data = response["result"]
        if scale_data is None:
            return None
        #
        # if 'error' in response:
        #     raise Exception(response['error']['message'])
        #
        # if 'result' in response:
        #     if value_scale_type:
        #
        #         if response.get('result') is not None:
        #             query_value = response.get('result')
        #         elif storage_item.value['modifier'] == 'Default':
        #             # Fallback to default value of storage function if no result
        #             query_value = storage_item.value_object['default'].value_object
        #         else:
        #             # No result is interpreted as an Option<...> result
        #             value_scale_type = f'Option<{value_scale_type}>'
        #             query_value = storage_item.value_object['default'].value_object
        #
        #         obj = self.runtime_config.create_scale_object(
        #             type_string=value_scale_type,
        #             data=ScaleBytes(query_value),
        #             metadata=self.metadata
        #         )
        #         obj.decode(check_remaining=True)
        #         obj.meta_info = {'result_found': response.get('result') is not None}
        #
        #         return obj

        return _scale_type.decode(ScaleBytes(scale_data))

    def query_multi(
        self,
        storage_functions: List[Tuple[str, str, list]],
    ) -> list:
        """
        Query multiple storage keys in one request.

        ```
        storage_functions = [
            "System", "Account", ["F4xQKRUagnSGjFqafyhajLs94e7Vvzvr8ebwYJceKpr8R7T"],
            "System", "Account", ["GSEX8kR4Kz5UZGhvRUCJG93D5hhTAoVZ5tAe6Zne7V42DSi"]
        ]

        result = substrate.query_multi(storage_keys)
        ```

        :param storage_functions: List of Storage function as tuples (module, function, [params,...])

        :return:
        """
        if self.metadata is None:
            raise Exception("Metadata empty")

        storage_keys = []
        scale_types: Dict[str, ScaleType] = {}
        for module, storage_function, params in storage_functions:
            # Search storage call in metadata
            metadata_pallet = self.metadata.get_metadata_pallet(module)

            if not metadata_pallet:
                raise Exception(f'Pallet "{module}" not found')

            storage_item = metadata_pallet.get_storage_function(storage_function)

            if not metadata_pallet or not storage_item:
                raise Exception(
                    f'Storage function "{module}.{storage_function}" not found'
                )

            _scale_type = self.get_scale_type(module, storage_function, params)
            _storage_key = _scale_type.storage_hash
            storage_keys.append(_storage_key)
            scale_types[_storage_key] = _scale_type

        # Retrieve corresponding value
        response = self.rpc_request("state_queryStorageAt", [storage_keys])

        if "error" in response:
            raise Exception(response["error"]["message"])
        result = []

        storage_key_map = {"0x" + s: s for s in storage_keys}
        for result_group in response["result"]:
            for change_storage_key, change_data in result_group["changes"]:
                # Decode result for specified storage_key
                storage_key = storage_key_map[change_storage_key]
                if change_data is not None:
                    change_data = ScaleBytes(change_data)
                    result.append(scale_types[storage_key].decode(change_data))
                else:
                    result.append(None)

        return result

    def compose_call(
        self, call_module: str, call_function: str, call_params: Optional[dict] = None
    ) -> GenericCall:
        """
        Composes a call payload which can be used in an extrinsic.

        :param call_module: Name of the runtime module e.g. Balances
        :param call_function: Name of the call function e.g. transfer
        :param call_params: This is a dict containing the params of the call.
                             e.g. `{'dest': 'EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk', 'value': 1000000000000}`

        :return:
        """

        if call_params is None:
            call_params = {}

        call = self.runtime_config.create_scale_object(
            type_string="Call", metadata=self.metadata
        )

        call.encode(
            {
                "call_module": call_module,
                "call_function": call_function,
                "call_args": call_params,
            }
        )

        return call

    def submit_extrinsic(
        self,
        extrinsic: GenericExtrinsic,
        wait_for_inclusion: bool = False,
        wait_for_finalization: bool = False,
    ) -> "ExtrinsicReceipt":
        """
        Submit an extrinsic to the connected node, with the possibility to wait until the extrinsic is included
         in a block and/or the block is finalized. The receipt returned provided information about the block and
         triggered events

        :param extrinsic: Extrinsic The extrinsic to be sent to the network
        :param wait_for_inclusion: wait until extrinsic is included in a block (only works for websocket connections)
        :param wait_for_finalization: wait until extrinsic is finalized (only works for websocket connections)

        :return:
        """

        # Check requirements
        if not isinstance(extrinsic, GenericExtrinsic):
            raise TypeError("'extrinsic' must be of type Extrinsics")

        def result_handler(message: dict, update_nr: int, subscription_id: int):
            """
            Parse subscription message filtered by subscription_id
            and unsubscribe when included or finalized

            :param message: Message dict
            :param update_nr: Update number
            :param subscription_id: Subscription ID number

            :return:
            """
            # Check if extrinsic is included and finalized
            if "params" in message and type(message["params"]["result"]) is dict:

                # Convert result enum to lower for backwards compatibility
                message_result = {
                    k.lower(): v for k, v in message["params"]["result"].items()
                }

                if "finalized" in message_result and wait_for_finalization:
                    self.rpc_request("author_unwatchExtrinsic", [subscription_id])
                    return {
                        "block_hash": message_result["finalized"],
                        "extrinsic_hash": "0x{}".format(extrinsic.extrinsic_hash.hex()),
                        "finalized": True,
                    }
                elif (
                    "inblock" in message_result
                    and wait_for_inclusion
                    and not wait_for_finalization
                ):
                    self.rpc_request("author_unwatchExtrinsic", [subscription_id])
                    return {
                        "block_hash": message_result["inblock"],
                        "extrinsic_hash": "0x{}".format(extrinsic.extrinsic_hash.hex()),
                        "finalized": False,
                    }

        if wait_for_inclusion or wait_for_finalization:
            response = self.rpc_request(
                "author_submitAndWatchExtrinsic",
                [str(extrinsic.data)],
                result_handler=result_handler,
            )

            result = ExtrinsicReceipt(
                extrinsic_hash=response["extrinsic_hash"],
                block_hash=response["block_hash"],
                finalized=response["finalized"],
                is_success=True,
            )
        else:
            response = self.rpc_request("author_submitExtrinsic", [str(extrinsic.data)])

            if "result" not in response:
                raise Exception(response.get("error"))

            result = ExtrinsicReceipt(
                extrinsic_hash=response["result"], is_success=True
            )

        return result

    def get_payment_info(self, call: GenericCall, keypair: Keypair):
        """
        Retrieves fee estimation via RPC for given extrinsic

        Return Dict with payment info:

        {'class': 'normal', 'partialFee': 151000000, 'weight': {'ref_time': 143322000}}

        :param call: Call object to estimate fees for
        :param keypair: Keypair of the sender,
                        does not have to include private key because no valid signature is required

        :return:
        """

        # Check requirements
        if not isinstance(call, GenericCall):
            raise TypeError("'call' must be of type Call")

        if not isinstance(keypair, Keypair):
            raise TypeError("'keypair' must be of type Keypair")

        # No valid signature is required for fee estimation
        signature = "0x" + "00" * 64

        # Create extrinsic
        extrinsic = self.create_signed_extrinsic(
            call=call, keypair=keypair, signature=signature
        )

        # if self.supports_rpc_method('state_call'):
        #     extrinsic_len = self.runtime_config.create_scale_object('u32')
        #     extrinsic_len.encode(len(extrinsic.data))
        #
        #     result = self.runtime_call("TransactionPaymentApi", "query_info", [extrinsic, extrinsic_len])
        #
        #     return result.value
        # else:
        # Backwards compatibility; deprecated RPC method
        payment_info = self.rpc_request("payment_queryInfo", [str(extrinsic.data)])

        # convert partialFee to int
        if "result" in payment_info:
            payment_info["result"]["partialFee"] = int(
                payment_info["result"]["partialFee"]
            )

            if type(payment_info["result"]["weight"]) is int:
                # Transform format to WeightV2 if applicable as per https://github.com/paritytech/substrate/pull/12633
                try:
                    weight_obj = self.runtime_config.create_scale_object(
                        "sp_weights::weight_v2::Weight"
                    )
                    if weight_obj is not None:
                        payment_info["result"]["weight"] = {
                            "ref_time": payment_info["result"]["weight"],
                            "proof_size": 0,
                        }
                except NotImplementedError:
                    pass

            return payment_info["result"]
        else:
            raise Exception(payment_info["error"]["message"])

    ###########################################
    def get_chain_finalised_head(self) -> Optional[Any]:
        """
        A pass-though to existing JSONRPC method `chain_getFinalizedHead`

        :return:
        """
        response = self.rpc_request("chain_getFinalizedHead", [])

        if response is not None:
            if "error" in response:
                raise Exception(response["error"]["message"])

            return response.get("result")

    def get_block_number(self, block_hash: str) -> int:
        """
        A convenience method to get the block number for given block_hash

        :param block_hash: Hash of block

        :return:
        """
        response = self.rpc_request("chain_getHeader", [block_hash])

        if "error" in response:
            raise Exception(response["error"]["message"])

        elif "result" in response:

            if response["result"]:
                return int(response["result"]["number"], 16)

        raise Exception(f"get_block_number error: {response['result']}")

    def get_block_hash(self, block_id: Optional[int] = None) -> Optional[Any]:
        """
        A pass-though to existing JSONRPC method `chain_getBlockHash`

        :param block_id: Block number

        :return:
        """
        response = self.rpc_request("chain_getBlockHash", [block_id])

        if "error" in response:
            raise Exception(response["error"]["message"])
        else:
            return response.get("result")

    def generate_signature_payload(
        self,
        call: GenericCall,
        era: Optional[Union[str, dict]] = None,
        nonce: int = 0,
        tip: int = 0,
        tip_asset_id: Optional[int] = None,
        include_call_length: bool = False,
    ) -> ScaleBytes:
        """
        Generate signature payload for extrinsic call

        :param call: GenericCall instance
        :param era: Dict of Era
        :param nonce: Signer account Nonce
        :param tip: Tip amount
        :param tip_asset_id: Tip asset ID
        :param include_call_length: True to include call length

        :return:
        """
        if self.metadata is None:
            raise Exception("Metadata empty")

        # Retrieve genesis hash
        genesis_hash = self.get_block_hash(0)

        if not era:
            era = "00"

        if era == "00":
            # Immortal extrinsic
            block_hash = genesis_hash
        else:
            # Determine mortality of extrinsic
            era_obj = self.runtime_config.create_scale_object("Era")

            if isinstance(era, dict) and "current" not in era and "phase" not in era:
                raise ValueError(
                    'The era dict must contain either "current" or "phase" element to encode a valid era'
                )

            era_obj.encode(era)
            block_hash = self.get_block_hash(block_id=era_obj.birth(era.get("current")))  # type: ignore

        # Create signature payload
        signature_payload = self.runtime_config.create_scale_object(
            "ExtrinsicPayloadValue"
        )

        # Process signed extensions in metadata
        if "signed_extensions" in self.metadata[1][1]["extrinsic"]:

            # Base signature payload
            signature_payload.type_mapping = [["call", "CallBytes"]]

            # Add signed extensions to payload
            signed_extensions = self.metadata.get_signed_extensions()

            if "CheckMortality" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["era", signed_extensions["CheckMortality"]["extrinsic"]]
                )

            if "CheckEra" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["era", signed_extensions["CheckEra"]["extrinsic"]]
                )

            if "CheckNonce" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["nonce", signed_extensions["CheckNonce"]["extrinsic"]]
                )

            if "ChargeTransactionPayment" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["tip", signed_extensions["ChargeTransactionPayment"]["extrinsic"]]
                )

            if "ChargeAssetTxPayment" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["asset_id", signed_extensions["ChargeAssetTxPayment"]["extrinsic"]]
                )

            if "CheckMetadataHash" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["mode", signed_extensions["CheckMetadataHash"]["extrinsic"]]
                )

            if "CheckSpecVersion" in signed_extensions:
                signature_payload.type_mapping.append(
                    [
                        "spec_version",
                        signed_extensions["CheckSpecVersion"]["additional_signed"],
                    ]
                )

            if "CheckTxVersion" in signed_extensions:
                signature_payload.type_mapping.append(
                    [
                        "transaction_version",
                        signed_extensions["CheckTxVersion"]["additional_signed"],
                    ]
                )

            if "CheckGenesis" in signed_extensions:
                signature_payload.type_mapping.append(
                    [
                        "genesis_hash",
                        signed_extensions["CheckGenesis"]["additional_signed"],
                    ]
                )

            if "CheckMortality" in signed_extensions:
                signature_payload.type_mapping.append(
                    [
                        "block_hash",
                        signed_extensions["CheckMortality"]["additional_signed"],
                    ]
                )

            if "CheckEra" in signed_extensions:
                signature_payload.type_mapping.append(
                    ["block_hash", signed_extensions["CheckEra"]["additional_signed"]]
                )

            if "CheckMetadataHash" in signed_extensions:
                signature_payload.type_mapping.append(
                    [
                        "metadata_hash",
                        signed_extensions["CheckMetadataHash"]["additional_signed"],
                    ]
                )

        if include_call_length:

            length_obj = self.runtime_config.create_scale_object("Bytes")
            call_data = str(length_obj.encode(str(call.data)))

        else:
            call_data = str(call.data)

        payload_dict = {
            "call": call_data,
            "era": era,
            "nonce": nonce,
            "tip": tip,
            "spec_version": self.runtime_version,
            "genesis_hash": genesis_hash,
            "block_hash": block_hash,
            "transaction_version": self.transaction_version,
            "asset_id": {"tip": tip, "asset_id": tip_asset_id},
            "metadata_hash": None,
            "mode": "Disabled",
        }

        signature_payload.encode(payload_dict)

        if signature_payload.data.length > 256:
            return ScaleBytes(
                data=blake2b(signature_payload.data.data, digest_size=32).digest()
            )

        return signature_payload.data

    def create_signed_extrinsic(
        self,
        call: GenericCall,
        keypair: Keypair,
        era: Optional[Union[str, dict]] = None,
        nonce: Optional[int] = None,
        tip: int = 0,
        tip_asset_id: Optional[int] = None,
        signature: Optional[Union[bytes, str]] = None,
    ) -> GenericExtrinsic:
        """
        Creates an extrinsic signed by given account details

        :param call: GenericCall to create extrinsic for
        :param keypair: Keypair used to sign the extrinsic
        :param era: Specify mortality in blocks in follow format: {'period': [amount_blocks]}
             If omitted the extrinsic is immortal
        :param nonce: nonce to include in extrinsics, if omitted the current nonce is retrieved on-chain
        :param tip: The tip for the block author to gain priority during network congestion
        :param tip_asset_id: Optional asset ID with which to pay the tip
        :param signature: Optionally provide signature if externally signed

        :return:
        """
        if self.metadata is None:
            raise Exception("Metadata empty")

        # Check requirements
        if not isinstance(call, GenericCall):
            raise TypeError("'call' must be of type Call")

        # Check if extrinsic version is supported
        if self.metadata[1][1]["extrinsic"]["version"].value != 4:
            raise NotImplementedError(
                f"Extrinsic version {self.metadata[1][1]['extrinsic']['version']} not supported"
            )

        # Retrieve nonce
        if nonce is None:
            response = self.rpc_request(
                "system_accountNextIndex", [keypair.ss58_address]
            )
            nonce = response.get("result") or 0

        # Process era
        if era is None:
            era = "00"
        else:
            if isinstance(era, dict) and "current" not in era and "phase" not in era:
                # Retrieve current block id
                era["current"] = self.get_block_number(self.get_chain_finalised_head())  # type: ignore

        if signature is not None:

            if type(signature) is str and signature[0:2] == "0x":
                signature = bytes.fromhex(signature[2:])  # type: ignore

            # Check if signature is a MultiSignature and contains signature version
            if len(signature) == 65:
                signature_version = signature[0]
                signature = signature[1:]
            else:
                signature_version = keypair.crypto_type

        else:
            # Create signature payload
            signature_payload = self.generate_signature_payload(
                call=call, era=era, nonce=nonce, tip=tip, tip_asset_id=tip_asset_id
            )

            # Set Signature version to crypto type of keypair
            signature_version = keypair.crypto_type

            # Sign payload
            signature = keypair.sign(signature_payload)

        # Create extrinsic
        extrinsic = self.runtime_config.create_scale_object(
            type_string="Extrinsic", metadata=self.metadata
        )

        value = {
            "account_id": f"0x{keypair.public_key.hex()}",
            "signature": f"0x{signature.hex()}",  # type: ignore
            "call_function": call.value["call_function"],
            "call_module": call.value["call_module"],
            "call_args": call.value["call_args"],
            "nonce": nonce,
            "era": era,
            "tip": tip,
            "asset_id": {"tip": tip, "asset_id": tip_asset_id},
            "mode": "Disabled",
        }

        # Check if ExtrinsicSignature is MultiSignature, otherwise omit signature_version
        signature_cls = self.runtime_config.get_decoder_class("ExtrinsicSignature")
        if issubclass(signature_cls, self.runtime_config.get_decoder_class("Enum")):
            value["signature_version"] = signature_version

        extrinsic.encode(value)

        return extrinsic

    #############################################################
    def implements_scaleinfo(self) -> Optional[bool]:
        """
        Returns True if current runtime implementation a `PortableRegistry` (`MetadataV14` and higher)

        Returns
        -------
        bool
        """
        if self.metadata:
            return self.metadata.portable_registry is not None
        return None

    def get_scale_type(
        self, module: str, module_function: str, params: list
    ) -> ScaleType:
        """
        Return scale type

        :param module: Module name
        :param module_function: Module function name
        :param params: List of parameters

        :return:
        """
        if self.metadata is None:
            raise Exception("Metadata empty")

        # # Add the embedded type registry to the runtime config
        # self.runtime_config.add_portable_registry(self.metadata)

        metadata_pallet = self.metadata.get_metadata_pallet(module)
        metadata_storage_function = metadata_pallet.get_storage_function(
            module_function
        )

        # Process specific type of storage function
        value_scale_type = metadata_storage_function.get_value_type_string()
        param_types = metadata_storage_function.get_params_type_string()
        storage_hash = xxh128(
            metadata_pallet.value["storage"]["prefix"].encode()
        ) + xxh128(module_function.encode())

        hashers = metadata_storage_function.get_param_hashers()

        hasher_functions = {
            "Blake2_256": blake2_256,
            "Blake2_128": blake2_128,
            "Blake2_128Concat": blake2_128_concat,
            "Twox128": xxh128,
            "Twox64Concat": two_x64_concat,
            "Identity": lambda x: x,
        }

        # Encode parameters
        params_encoded = []
        if params:
            for idx, param in enumerate(params):
                if type(param) is ScaleBytes:
                    # Already encoded
                    params_encoded.append(param)
                else:
                    param = convert_storage_parameter(
                        self.runtime_config, param_types[idx], param
                    )
                    param_obj = self.runtime_config.create_scale_object(
                        type_string=param_types[idx]
                    )
                    params_encoded.append(param_obj.encode(param))

            for idx, param in enumerate(params_encoded):
                # Get hasher assiociated with param
                try:
                    param_hasher = hashers[idx]
                except IndexError:
                    raise ValueError(f"No hasher found for param #{idx + 1}")

                params_key = bytes()

                # Convert param to bytes
                if type(param) is str:
                    params_key += binascii.unhexlify(param)
                elif type(param) is ScaleBytes:
                    params_key += param.data
                elif isinstance(param, ScaleDecoder):
                    params_key += param.data.data

                if not param_hasher:
                    param_hasher = "Twox128"

                if param_hasher in hasher_functions:
                    storage_hash += hasher_functions[param_hasher](params_key)
                else:
                    raise ValueError('Unknown storage hasher "{}"'.format(param_hasher))

        scale_object = self.runtime_config.create_scale_object(
            value_scale_type, metadata=self.metadata
        )
        scale_object.storage_hash = storage_hash.hex()
        return scale_object


def blake2_256(data):
    """
    Helper function to calculate a 32 bytes Blake2b hash for provided data, used as key for Substrate storage items

    :param data: Data to encode

    :return:
    """
    return blake2b(data, digest_size=32).digest()


def blake2_128(data):
    """
    Helper function to calculate a 16 bytes Blake2b hash for provided data, used as key for Substrate storage items

    :param data: Data to encode

    :return:
    """
    return blake2b(data, digest_size=16).digest()


def blake2_128_concat(data):
    """
    Helper function to calculate a 16 bytes Blake2b hash for provided data, concatenated with data, used as key
    for Substrate storage items

    :param data: Data to encode

    :return:
    """
    return blake2b(data, digest_size=16).digest() + data


def two_x64_concat(data):
    """
    Helper function to calculate a xxh64 hash with concatenated data for provided data,
    used as key for several Substrate

    :param data: Data to encode

    :return:
    """
    storage_key = bytearray(xxhash.xxh64(data, seed=0).digest())
    storage_key.reverse()

    return storage_key + data


def xxh128(data):
    """
    Helper function to calculate a 2 concatenated xxh64 hash for provided data, used as key for several Substrate

    :param data: Data to encode

    :return:
    """
    storage_key1 = bytearray(xxhash.xxh64(data, seed=0).digest())
    storage_key1.reverse()

    storage_key2 = bytearray(xxhash.xxh64(data, seed=1).digest())
    storage_key2.reverse()

    return storage_key1 + storage_key2


def convert_storage_parameter(
    runtime_config: RuntimeConfigurationObject, scale_type: str, value: Any
):
    """


    :param runtime_config: RuntimeConfigurationObject instance
    :param scale_type: Scale type string
    :param value: Parameter value

    :return:
    """
    if type(value) is bytes:
        value = f"0x{value.hex()}"

    if scale_type == "AccountId":
        if value[0:2] != "0x":
            return "0x{}".format(ss58_decode(value, runtime_config.ss58_format))

    return value


def list_remove_iter(xs: list):
    """
    List remover

    :param xs: List to handle

    :return:
    """
    removed = False

    def remove():
        nonlocal removed
        removed = True

    i = 0
    while i < len(xs):
        removed = False
        yield xs[i], remove
        if removed:
            xs.pop(i)
        else:
            i += 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    _client = SubstrateClient("ws://localhost:9944")

    alice_address = "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
    bob_address = "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty"
    alice_keypair = Keypair.create_from_uri(
        "bottom drive obey lake curtain smoke basket hold race lonely fit walk//Alice"
    )

    # response = client.query("System", "Account", [alice_address])
    # print(response)

    # _response = _client.query_multi(
    #     [("System", "Account", [alice_address]), ("System", "Account", [bob_address])]
    # )
    # print(_response)
    #
    # _params = {"" "dest": bob_address, "value": 1100}
    #
    # _call = _client.compose_call(
    #     call_module="Balances",
    #     call_function="transfer_keep_alive",
    #     call_params=_params,
    # )
    #
    # _extrinsic = _client.create_signed_extrinsic(call=_call, keypair=alice_keypair)
    #
    # _receipt = _client.submit_extrinsic(
    #     _extrinsic,
    #     wait_for_inclusion=True,
    #     wait_for_finalization=False,
    # )
    # logging.debug(
    #     "Extrinsic '%s' sent and included in block '%s'",
    #     _receipt.extrinsic_hash,
    #     _receipt.block_hash,
    # )
    #
    # _response = _client.query_multi(
    #     [("System", "Account", [alice_address]), ("System", "Account", [bob_address])]
    # )
    # print(_response)

    result = _client.query("Identity", "Identities", [1])
    print(result)

    _client.close()
