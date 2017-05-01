START TRANSACTION;
SET standard_conforming_strings=off;
SET escape_string_warning=off;
SET CONSTRAINTS ALL DEFERRED;

-- Table: concept
DROP TABLE IF EXISTS concept;
create table concept 
   (concept_id INTEGER not null PRIMARY KEY, 
	concept_name text not null, 
	concept_level INTEGER, 
	concept_class text, 
	vocabulary_id INTEGER, 
	concept_code text, 
	valid_start_date date, 
	valid_end_date date default '31-dec-2099', 
	invalid_reason text
    )
WITH (
  OIDS=FALSE
);
ALTER TABLE concept
  OWNER TO postgres;

-- Table: oa_selector
DROP TABLE IF EXISTS oa_selector;
CREATE TABLE oa_selector (
    selector_uid serial,
    selector_type text,
    exact text,
    prefix text,
    suffix text,
    PRIMARY KEY (selector_uid)
);


-- Table: oa_target
DROP TABLE IF EXISTS oa_target;
CREATE TABLE oa_target (
    target_uid integer,
    has_source text,
    has_selector integer,
    PRIMARY KEY (target_uid),
    FOREIGN KEY (has_selector) REFERENCES oa_selector (selector_uid)
);


-- Table: mp_claim
DROP TABLE IF EXISTS mp_claim;
CREATE TABLE mp_claim
(
  claim_id INTEGER not null PRIMARY KEY,
  concept_id INTEGER,
  label text,
  type text,
  uri text,
  np_id INTEGER,
  qualified_by integer,
  has_oa_target integer
);


-- Table: mp_data
DROP TABLE IF EXISTS mp_data;
CREATE TABLE mp_data
(
  data_id INTEGER not null PRIMARY KEY,
  claim_id INTEGER not null,
  method_id INTEGER,
  concept_id INTEGER,
  FOREIGN KEY (claim_id) REFERENCES mp_claim (claim_id)
);


-- Table: mp_data_field
DROP TABLE IF EXISTS mp_data_field;
CREATE TABLE mp_data_field
(
  data_field_id INTEGER not null PRIMARY KEY,
  data_id INTEGER not null,
  type text,
  value_as_number INTEGER,
  value_as_string text,
  value_as_concept_id INTEGER,
  has_oa_target INTEGER not null,
  FOREIGN KEY (data_id) REFERENCES mp_data (data_id), 
  FOREIGN KEY (has_oa_target) REFERENCES oa_target (target_uid) 
);


-- Table: mp_method
DROP TABLE IF EXISTS mp_method;
CREATE TABLE mp_method
(
  method_id INTEGER PRIMARY KEY,
  data_id INTEGER not null,
  material_id INTEGER,
  concept_id INTEGER,
  type text,
  FOREIGN KEY (data_id) REFERENCES mp_data (data_id)
);


-- Table: mp_material
DROP TABLE IF EXISTS mp_material;
CREATE TABLE mp_material
(
  material_id INTEGER PRIMARY KEY,
  method_id INTEGER,
  concept_id INTEGER,
  type text,
  FOREIGN KEY (method_id) REFERENCES mp_method (method_id)
);

-- Table: mp_material_field
DROP TABLE IF EXISTS mp_material_field;
CREATE TABLE mp_material_field
(
  material_field_id INTEGER PRIMARY KEY,
  material_id INTEGER,
  type text,
  value_as_number INTEGER,
  value_as_string text,
  value_as_concept_id INTEGER,
  has_oa_target INTEGER,
  FOREIGN KEY (material_id) REFERENCES mp_material (material_id),
  FOREIGN KEY (has_oa_target) REFERENCES oa_target (target_uid) 
);


-- Table: mp_reference
--DROP TABLE IF EXISTS mp_reference;
CREATE TABLE mp_reference
(
  reference_id INTEGER PRIMARY KEY,
  concept_id INTEGER,
  type text,
  reference text,
  uri text
);

-- Table: mp_claim_reference_relationship
DROP TABLE IF EXISTS mp_claim_reference_relationship;
CREATE TABLE mp_claim_reference_relationship
(
  Id serial PRIMARY KEY,
  concept_id INTEGER,
  claim_id INTEGER,
  reference_id INTEGER,
  FOREIGN KEY (claim_id) REFERENCES mp_claim (claim_id),
  FOREIGN KEY (reference_id) REFERENCES mp_reference (reference_id)
);


-- Table: qualifier
--DROP TABLE IF EXISTS qualifier;
CREATE TABLE qualifier
(
  qualifier_id INTEGER PRIMARY KEY,
  concept_id INTEGER,
  subject text,
  predicate text,
  object text
);

-- Table: mp_claim_qualifier_relationship
DROP TABLE IF EXISTS mp_claim_qualifier_relationship;
CREATE TABLE mp_claim_qualifier_relationship
(
  Id serial PRIMARY KEY,
  concept_id INTEGER,
  claim_id INTEGER,
  qualifier_id INTEGER,
  FOREIGN KEY (claim_id) REFERENCES mp_claim (claim_id),
  FOREIGN KEY (qualifier_id) REFERENCES qualifier (qualifier_id)
);

