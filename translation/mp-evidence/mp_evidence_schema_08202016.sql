-- Database: mpevidenceCREATE DATABASE mpevidence  WITH OWNER = postgres       ENCODING = 'UTF8'       TABLESPACE = pg_default       LC_COLLATE = 'en_US.UTF-8'       LC_CTYPE = 'en_US.UTF-8'CONNECTION LIMIT = -1;--TABLE: mp_claim_annotation
DROP TABLE IF EXISTS mp_claim_annotation CASCADE;
CREATE TABLE mp_claim_annotation
(
id INTEGER not null PRIMARY KEY,
urn text,
type text,
has_body integer,
has_target integer,
creator text,
date_created date,
date_updated date
);


--TABLE: oa_claim_body
DROP TABLE IF EXISTS oa_claim_body CASCADE;
CREATE TABLE oa_claim_body
(
id INTEGER not null PRIMARY KEY,
urn text,
label text,
claim_text text,
np_assertion_id integer,
is_oa_body_of integer
);


--TABLE: oa_target
DROP TABLE IF EXISTS oa_target CASCADE;
CREATE TABLE oa_target
(
id INTEGER not null PRIMARY KEY,
urn text,
label text,
has_source text,
has_selector integer
);


--TABLE mp_data_annotation
DROP TABLE IF EXISTS mp_data_annotation CASCADE;
CREATE TABLE mp_data_annotation
(
id INTEGER not null PRIMARY KEY,
urn text,
type text,
has_body integer,
has_target integer,
creator text,
mp_claim_id integer,
mp_data_index integer,
ev_supports boolean,
date_created date,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation (id)
);


--TABLE oa_data_body
DROP TABLE IF EXISTS oa_data_body CASCADE;
CREATE TABLE oa_data_body
(
id INTEGER not null PRIMARY KEY,
urn text,
mp_data_annotation_id integer,
data_type text,
vocabulary_id integer,
concept_code text,
is_oa_body_of integer,
FOREIGN KEY (mp_data_annotation_id) REFERENCES mp_data_annotation (id)
);


--TABLE data_field
DROP TABLE IF EXISTS data_field CASCADE;
CREATE TABLE data_field
(
id INTEGER not null PRIMARY KEY,
urn text,
data_body_id integer,
data_field_type text,
value_as_string text,
value_as_number integer,
FOREIGN KEY (data_body_id) REFERENCES oa_data_body(id)
);


--TABLE mp_material_annotation
DROP TABLE IF EXISTS mp_material_annotation CASCADE;
CREATE TABLE mp_material_annotation
(
id INTEGER not null PRIMARY KEY,
urn text,
type text,
has_body integer,
has_target integer,
creator text,
mp_claim_id integer,
mp_data_index integer,
ev_supports boolean,
date_created date,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id)
);


--TABLE oa_material_body
DROP TABLE IF EXISTS oa_material_body CASCADE;
CREATE TABLE oa_material_body
(
id INTEGER not null PRIMARY KEY,
urn text,
mp_material_annotation_id integer,
material_type text,
vocabulary_id integer,
concept_code text,
is_oa_body_of integer,
FOREIGN KEY (mp_material_annotation_id) REFERENCES mp_material_annotation(id)
);


--TABLE material_field
DROP TABLE IF EXISTS material_field CASCADE;
CREATE TABLE material_field
(
id INTEGER not null PRIMARY KEY,
urn text,
material_body_id integer,
material_field_type text,
value_as_string text,
value_as_number integer,
FOREIGN KEY (material_body_id) REFERENCES oa_material_body(id)
);


--TABLE qualifier
DROP TABLE IF EXISTS qualifier CASCADE;
CREATE TABLE qualifier
(
id INTEGER not null PRIMARY KEY,
urn text,
claim_body_id integer,
qvalue text,
subject boolean,
predicate boolean,
object boolean,
concept_code text,
vocabulary_id integer,
FOREIGN KEY (claim_body_id) REFERENCES mp_claim_annotation(id)
);


--TABLE method
DROP TABLE IF EXISTS method CASCADE;
CREATE TABLE method
(
id INTEGER not null PRIMARY KEY,
value text,
mp_claim_id integer,
mp_data_material_id integer,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id),
FOREIGN KEY (mp_data_material_id) REFERENCES mp_material_annotation(id)
);


--TABLE oa_selector
DROP TABLE IF EXISTS oa_selector CASCADE;
CREATE TABLE oa_selector
(
id INTEGER not null PRIMARY KEY,
urn text,
selector_type text,
exact text,
prefix text,
suffix text
);


--TABLE mp_reference
DROP TABLE IF EXISTS mp_reference CASCADE;
CREATE TABLE mp_reference
(
id INTEGER not null PRIMARY KEY,
urn text,
reference text,
author text,
date date
);


--TABLE claim_reference_relationships
DROP TABLE IF EXISTS claim_reference_relationship CASCADE;
CREATE TABLE claim_reference_relationship
(
id INTEGER not null PRIMARY KEY,
mp_claim_id integer,
mp_reference_id integer,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id),
FOREIGN KEY (mp_reference_id) REFERENCES mp_reference(id)
);
