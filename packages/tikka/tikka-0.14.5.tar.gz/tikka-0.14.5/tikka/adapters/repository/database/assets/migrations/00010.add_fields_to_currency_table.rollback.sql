ALTER TABLE currency ADD COLUMN certification_number_to_be_member integer;
ALTER TABLE currency ADD COLUMN minimum_delay_between_two_membership_renewals integer;
ALTER TABLE currency ADD COLUMN validity_duration_of_membership integer;
ALTER TABLE currency ADD COLUMN minimum_certifications_received_to_be_certifier integer;
ALTER TABLE currency ADD COLUMN validity_duration_of_certification integer;
ALTER TABLE currency ADD COLUMN minimum_delay_between_two_certifications integer;
ALTER TABLE currency ADD COLUMN maximum_number_of_certifications_per_member integer;
ALTER TABLE currency ADD COLUMN maximum_distance_in_step integer;
ALTER TABLE currency ADD COLUMN minimum_percentage_of_remote_referral_members_to_be_member integer;
ALTER TABLE currency ADD COLUMN identity_automatic_revocation_period integer;
ALTER TABLE currency ADD COLUMN minimum_delay_between_changing_identity_owner integer;
ALTER TABLE currency ADD COLUMN confirm_identity_period integer;
ALTER TABLE currency ADD COLUMN identity_deletion_after_revocation integer;
ALTER TABLE currency ADD COLUMN minimum_delay_between_identity_creation integer;
ALTER TABLE currency ADD COLUMN identity_validation_period integer;
ALTER TABLE currency ADD COLUMN maximum_certifications_per_smith integer;
ALTER TABLE currency ADD COLUMN number_of_certifications_to_become_smith integer;
ALTER TABLE currency ADD COLUMN maximum_inactivity_duration_allowed_for_smith integer;

-------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE currency RENAME TO currency_old;

-- Step 2: Create the new table
create table currency(
    code_name varchar(255) unique primary key not null,
    name varchar(255),
    ss58_format integer,
    token_decimals integer default null,
    token_symbol varchar(255) default null,
    universal_dividend integer default null,
    monetary_mass integer default null,
    members_count integer default null,
    block_duration integer default 6000,
    epoch_duration integer default 3600000
);

-- Step 3: Copy data from the old table
INSERT INTO currency (
    code_name,
    name,
    ss58_format,
    token_decimals,
    token_symbol,
    universal_dividend,
    monetary_mass,
    members_count,
    block_duration,
    epoch_duration
)
SELECT
    code_name,
    name,
    ss58_format,
    token_decimals,
    token_symbol,
    universal_dividend,
    monetary_mass,
    members_count,
    block_duration,
    epoch_duration
FROM currency_old;

-- Step 4: Drop the old table
DROP TABLE currency_old;

---------------------------------------
