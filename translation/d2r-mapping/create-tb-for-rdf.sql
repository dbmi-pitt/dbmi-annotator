-- AUC fold RDF creation (DDI clinical trial, interact) --------------------------------
-- https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxkZGlrcmFuZGlyfGd4OjIzYTc2YjA4NjRkNTAzZDQ


SET SCHEMA 'ohdsi';

CREATE EXTENSION "uuid-ossp";
CREATE EXTENSION tablefunc;

-- MP Claim and qualifier table: rdf_mp_claim_qualifier -----------------------------
CREATE TABLE rdf_mp_claim_qualifier AS 
SELECT 
mp_claim_id, mp_data_index, method, precipitant, p_concept_code, p_role_concept_code, object, o_concept_code, o_role_concept_code, uuid_generate_v4() as asrt_description_urn, 
uuid_generate_v4() as p_bearer_role_urn, uuid_generate_v4() as o_bearer_role_urn, uuid_generate_v4() as p_drug_role_urn, uuid_generate_v4() as o_drug_role_urn, uuid_generate_v4() as method_urn, 
uuid_generate_v4() as p_scattered_molecular_aggregate_urn, uuid_generate_v4() as p_active_ingredient_urn, uuid_generate_v4() as p_drug_urn, uuid_generate_v4() as p_mass_urn, uuid_generate_v4() as p_milligram_urn, 
uuid_generate_v4() as o_scattered_molecular_aggregate_urn, uuid_generate_v4() as o_active_ingredient_urn, uuid_generate_v4() as o_drug_urn, uuid_generate_v4() as o_mass_urn, uuid_generate_v4() as o_milligram_urn
FROM (
WITH method AS (
SELECT mp_claim_id, mp_data_index, m.entered_value as method from method m),
p AS (
SELECT ca.id, q.qvalue, q.concept_code, q.vocabulary_id, q.qualifier_role_concept_code, cb.label
FROM mp_claim_annotation ca 
JOIN oa_claim_body cb on cb.is_oa_body_of = ca.id
JOIN qualifier q on q.claim_body_id = cb.id
WHERE q.subject = True
AND cb.label LIKE '%interact%with%'),
o AS (
SELECT ca.id, q.qvalue, q.concept_code, q.vocabulary_id, q.qualifier_role_concept_code, cb.label
FROM mp_claim_annotation ca 
JOIN oa_claim_body cb on cb.is_oa_body_of = ca.id
JOIN qualifier q on q.claim_body_id = cb.id
WHERE q.object = True
AND cb.label LIKE '%interact%with%')
SELECT method.mp_claim_id, method.mp_data_index, method.method, p.qvalue as precipitant, p.concept_code as p_concept_code, p.qualifier_role_concept_code as p_role_concept_code, o.qvalue as object, 
o.concept_code as o_concept_code, o.qualifier_role_concept_code as o_role_concept_code
from method
JOIN p ON p.id = method.mp_claim_id
JOIN o ON o.id = method.mp_claim_id
WHERE method.method = 'DDI clinical trial'
) AS tb


-- MP data table: rdf_mp_data -------------------------------------------------------
-- auc, cmax, clearance, halflife
CREATE TABLE rdf_mp_data AS 
(SELECT d.mp_claim_id, d.mp_data_index, d.ev_supports, d.type as datatype, df.type as dftype, df.value, df.direction, uuid_generate_v4() as data_item_urn, uuid_generate_v4() as data_type_urn
FROM crosstab('SELECT df.data_body_id, df.data_field_type, df.value_as_string FROM data_field df ORDER BY 1,2')
AS df(data_body_id INTEGER, direction TEXT, type TEXT, value TEXT)
JOIN oa_data_body db ON df.data_body_id = db.id
JOIN mp_data_annotation d ON db.id = d.has_body
WHERE d.type = 'auc' or d.type = 'cmax' or d.type = 'clearance' or d.type = 'halflife')


-- MP material table: rdf_mp_material -----------------------------------------------
-- precipitant dose, object dose
CREATE TABLE rdf_mp_material AS 
WITH m_field AS (
SELECT material_body_id as body_id, drugname, value, duration, formulation, regimens
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, drugname TEXT, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
WHERE mf.value != ''),
m_ann AS (
SELECT mann.mp_claim_id, mann.has_body, mann.mp_data_index, mann.ev_supports, mbody.material_type
FROM mp_material_annotation mann
JOIN oa_material_body mbody ON mann.has_body = mbody.id 
WHERE material_type = 'precipitant_dose'
OR material_type = 'object_dose')
SELECT m_ann.mp_claim_id, m_ann.mp_data_index, m_ann.ev_supports, m_ann.material_type, m_field.drugname, m_field.value, m_field.duration, m_field.formulation, m_field.regimens
FROM m_ann
JOIN m_field on m_ann.has_body = m_field.body_id

