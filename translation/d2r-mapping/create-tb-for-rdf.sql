-- AUC fold RDF creation (DDI clinical trial, interact)
-- https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxkZGlrcmFuZGlyfGd4OjIzYTc2YjA4NjRkNTAzZDQ
SET SCHEMA 'ohdsi';

CREATE EXTENSION "uuid-ossp";
CREATE EXTENSION tablefunc;

CREATE TABLE ct_iw_auc_fold AS SELECT 
method, precipitant, precipitant_code, object, object_code, ratio, ratio_type, value, direction, uuid_generate_v4() as auc_urn, uuid_generate_v4() as fold_urn, uuid_generate_v4() as description_urn, uuid_generate_v4() as bearer_pt_urn, uuid_generate_v4() AS bearer_obj_urn, uuid_generate_v4() as pt_urn, uuid_generate_v4() as obj_urn, uuid_generate_v4() as method_urn
FROM (
WITH auc_fold AS (
SELECT d.mp_claim_id, d.mp_data_index, d.type as datatype, df.type as dftype, df.value, df.direction
FROM crosstab('SELECT df.data_body_id, df.data_field_type, df.value_as_string FROM data_field df ORDER BY 1,2')
AS df(data_body_id INTEGER, direction TEXT, type TEXT, value TEXT)
JOIN oa_data_body db ON df.data_body_id = db.id
JOIN mp_data_annotation d ON db.id = d.has_body
WHERE df.type = 'Fold'
AND mp_claim_id = '1'
AND d.creator = 'annotat2@gmail.com'
AND db.data_type = 'auc'),
method AS (
SELECT mp_claim_id, mp_data_index, m.entered_value as method from method m
WHERE m.mp_claim_id = '1'),
p AS (
SELECT ca.id, q.qvalue, q.qualifier_role_concept_code, cb.label
FROM mp_claim_annotation ca 
JOIN oa_claim_body cb on cb.is_oa_body_of = ca.id
JOIN qualifier q on q.claim_body_id = cb.id
WHERE q.subject = True
AND cb.label LIKE '%interact with%'
AND ca.id = '1'),
o AS (
SELECT ca.id, q.qvalue, q.qualifier_role_concept_code, cb.label
FROM mp_claim_annotation ca 
JOIN oa_claim_body cb on cb.is_oa_body_of = ca.id
JOIN qualifier q on q.claim_body_id = cb.id
WHERE q.object = True
AND cb.label LIKE '%interact with%'
AND ca.id = '1')
SELECT method.method, p.qvalue as precipitant, p.qualifier_role_concept_code as precipitant_code, o.qvalue as object, 
o.qualifier_role_concept_code as object_code, auc_fold.datatype as ratio, auc_fold.dftype as ratio_type, auc_fold.value, auc_fold.direction 
from auc_fold
JOIN method ON method.mp_claim_id = auc_fold.mp_claim_id
JOIN p ON p.id = auc_fold.mp_claim_id
JOIN o ON o.id = auc_fold.mp_claim_id
WHERE auc_fold.mp_data_index = method.mp_data_index
) AS CT_IW_AUC_FOLD

