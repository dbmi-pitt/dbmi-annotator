-- Database: mpevidence
-- CREATE DATABASE mpevidence
--   WITH OWNER = postgres
--        ENCODING = 'UTF8'
--        TABLESPACE = pg_default
--        LC_COLLATE = 'en_US.UTF-8'
--        LC_CTYPE = 'en_US.UTF-8'
-- CONNECTION LIMIT = -1;


DROP SCHEMA IF EXISTS ohdsi CASCADE;
CREATE SCHEMA ohdsi;
SET SCHEMA 'ohdsi';

-- MP Claim ------------------------------------
--TABLE: mp_claim_annotation
DROP TABLE IF EXISTS mp_claim_annotation CASCADE;
CREATE TABLE mp_claim_annotation
(
id INTEGER not null PRIMARY KEY,
urn text,
has_body integer,
has_target integer,
creator text,
date_created timestamp,
date_updated timestamp,
negation boolean,
rejected_statement boolean,
rejected_statement_reason text,
rejected_statement_comment text
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


-- MP Data ------------------------------------
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
date_created timestamp,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation (id)
);


--TABLEoa_data_body
DROP TABLE IF EXISTS oa_data_body CASCADE;
CREATE TABLE oa_data_body
(
id INTEGER not null PRIMARY KEY,
urn text,
data_type text,
vocabulary_id integer,
concept_code text,
is_oa_body_of integer,
FOREIGN KEY (is_oa_body_of) REFERENCES mp_data_annotation (id)
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
value_as_number numeric(10,2),
value_as_concept_id integer,
FOREIGN KEY (data_body_id) REFERENCES oa_data_body(id)
);

-- MP Material ------------------------------------
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
date_created timestamp,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id)
);


--TABLE oa_material_body
DROP TABLE IF EXISTS oa_material_body CASCADE;
CREATE TABLE oa_material_body
(
id INTEGER not null PRIMARY KEY,
urn text,
material_type text,
vocabulary_id integer,
concept_code text,
is_oa_body_of integer,
FOREIGN KEY (is_oa_body_of) REFERENCES mp_material_annotation(id)
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
value_as_number numeric(10,2),
value_as_concept_id integer,
FOREIGN KEY (material_body_id) REFERENCES oa_material_body(id)
);


--TABLE qualifier
DROP TABLE IF EXISTS qualifier CASCADE;
CREATE TABLE qualifier
(
id INTEGER not null PRIMARY KEY,
urn text,
claim_body_id integer,
subject boolean DEFAULT FALSE,
predicate boolean DEFAULT FALSE,
object boolean DEFAULT FALSE,
qvalue text,
concept_code text,
vocabulary_id integer,
qualifier_type_concept_code text,
qualifier_type_vocabulary_id integer,
qualifier_role_concept_code text,
qualifier_role_vocabulary_id integer,
enantiomer boolean DEFAULT False,
metabolite boolean DEFAULT False,
FOREIGN KEY (claim_body_id) REFERENCES oa_claim_body(id)
);

-- MP Method -------------------------------------
--TABLE method
DROP TABLE IF EXISTS method CASCADE;
CREATE TABLE method
(
id INTEGER not null PRIMARY KEY,
entered_value text,
inferred_value text,
mp_claim_id integer,
mp_data_index integer,
inferred_concept_code text,
inferred_vocabulary_id integer,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id)
);

-- Evidence type question -------------------------------------
--TABLE evidence_question
DROP TABLE IF EXISTS evidence_question CASCADE;
CREATE TABLE evidence_question
(
id INTEGER not null PRIMARY KEY,
method_id integer,
question text,
value_as_string text,
value_as_number integer,
value_as_boolean boolean,
concept_code text,
vocabulary_id integer,
FOREIGN KEY (method_id) REFERENCES method(id)
);

-- Open annotation target & selector --------------
--TABLE: oa_target
DROP TABLE IF EXISTS oa_target CASCADE;
CREATE TABLE oa_target
(
id INTEGER not null PRIMARY KEY,
urn text,
has_source text,
has_selector integer
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

-- MP Reference ------------------------------------
--TABLE mp_reference
DROP TABLE IF EXISTS mp_reference CASCADE;
CREATE TABLE mp_reference
(
id INTEGER not null PRIMARY KEY,
urn text,
reference text,
author text,
reference_date timestamp
);


--TABLE claim_reference_relationship
DROP TABLE IF EXISTS claim_reference_relationship CASCADE;
CREATE TABLE claim_reference_relationship
(
id INTEGER not null PRIMARY KEY,
mp_claim_id integer,
mp_reference_id integer,
FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation(id),
FOREIGN KEY (mp_reference_id) REFERENCES mp_reference(id)
);


CREATE SEQUENCE mp_claim_annotation_id_seq;
ALTER TABLE mp_claim_annotation alter id set default nextval('mp_claim_annotation_id_seq');

CREATE SEQUENCE oa_selector_id_seq;
ALTER TABLE oa_selector alter id set default nextval('oa_selector_id_seq');

CREATE SEQUENCE oa_target_id_seq;
ALTER TABLE oa_target alter id set default nextval('oa_target_id_seq');

CREATE SEQUENCE oa_claim_body_id_seq;
ALTER TABLE oa_claim_body alter id set default nextval('oa_claim_body_id_seq');

CREATE SEQUENCE qualifier_id_seq;
ALTER TABLE qualifier alter id set default nextval('qualifier_id_seq');

CREATE SEQUENCE mp_data_annotation_id_seq;
ALTER TABLE mp_data_annotation alter id set default nextval('mp_data_annotation_id_seq');

CREATE SEQUENCE oa_data_body_id_seq;
ALTER TABLE oa_data_body alter id set default nextval('oa_data_body_id_seq');

CREATE SEQUENCE data_field_id_seq;
ALTER TABLE data_field alter id set default nextval('data_field_id_seq');

CREATE SEQUENCE mp_material_annotation_id_seq;
ALTER TABLE mp_material_annotation alter id set default nextval('mp_material_annotation_id_seq');

CREATE SEQUENCE oa_material_body_id_seq;
ALTER TABLE oa_material_body alter id set default nextval('oa_material_body_id_seq');

CREATE SEQUENCE material_field_id_seq;
ALTER TABLE material_field alter id set default nextval('material_field_id_seq');

CREATE SEQUENCE method_id_seq;
ALTER TABLE method alter id set default nextval('method_id_seq');

CREATE SEQUENCE evidence_question_id_seq;
ALTER TABLE evidence_question alter id set default nextval('evidence_question_id_seq');

CREATE SEQUENCE claim_reference_relationship_id_seq;
ALTER TABLE claim_reference_relationship alter id set default nextval('claim_reference_relationship_id_seq');

CREATE SEQUENCE mp_reference_id_seq;
ALTER TABLE mp_reference alter id set default nextval('mp_reference_id_seq');


-- Highlight annotation ----------------------------------
--TABLE: highlight_annotation
DROP TABLE IF EXISTS highlight_annotation CASCADE;
CREATE TABLE highlight_annotation
(
id INTEGER not null PRIMARY KEY,
urn text,
type text,
has_body integer,
has_target integer,
creator text,
date_created timestamp,
date_updated timestamp,
article_highlight boolean,
mp_claim_id integer
);


--TABLE: oa_highlight_body
DROP TABLE IF EXISTS oa_highlight_body CASCADE;
CREATE TABLE oa_highlight_body
(
id INTEGER not null PRIMARY KEY,
urn text,
drugname text,
uri text,
vocabulary_id integer,
concept_code text,
is_oa_body_of integer,
FOREIGN KEY (is_oa_body_of) REFERENCES highlight_annotation (id)
);

CREATE SEQUENCE highlight_annotation_id_seq;
ALTER TABLE highlight_annotation alter id set default nextval('highlight_annotation_id_seq');

CREATE SEQUENCE oa_highlight_body_id_seq;
ALTER TABLE oa_highlight_body alter id set default nextval('oa_highlight_body_id_seq');

DROP EXTENSION IF EXISTS tablefunc;
CREATE EXTENSION tablefunc WITH SCHEMA ohdsi; 

-- FUNCTIONS 
-- handle qualifier role
CREATE OR REPLACE FUNCTION ohdsi.qualifierRole(boolean, boolean, boolean) 
RETURNS TEXT AS
$BODY$
BEGIN
IF $1 THEN RETURN 'subject';
ELSIF $2 THEN RETURN 'predicate';
ELSIF $3 THEN RETURN 'object';
ELSE RETURN 'qualifier';
END IF;
END;
$BODY$ language plpgsql;
