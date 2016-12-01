-- validate context 
select cann.id, cann.has_target, dann.has_target, mann.has_target
from mp_claim_annotation cann, mp_data_annotation dann, mp_material_annotation mann
where cann.id = dann.mp_claim_id and cann.id = mann.mp_claim_id;

-- validate claim
select cann.id, t.has_source, cann.creator, cann.date_created, cann.has_target, s.exact
from mp_claim_annotation cann, mp_data_annotation dann, mp_material_annotation mann, 
oa_target t, oa_selector s
where cann.id = dann.mp_claim_id 
and cann.id = mann.mp_claim_id
and cann.has_target = t.id
and t.has_selector = s.id;

-- query mp claim
select cann.id, t.has_source, cann.creator, cann.date_created, s.exact, s.prefix, s.suffix, cbody.label, qvalue, q.subject, q.predicate, q.object 
from mp_claim_annotation cann, oa_claim_body cbody, oa_target t, oa_selector s, qualifier q
where cann.has_body = cbody.id
and cann.has_target = t.id
and t.has_selector = s.id
and cbody.id = q.claim_body_id

-- query mp data
select dann.type, df.data_field_type, df.value_as_string, df.value_as_number, s.exact, s.prefix, s.suffix, mp_data_index
from mp_data_annotation dann,oa_data_body dbody, data_field df, oa_target t, oa_selector s
where dann.mp_claim_id = 6
and dann.has_body = dbody.id
and df.data_body_id = dbody.id
and dann.has_target = t.id
and t.has_selector = s.id

-- query mp material
select mann.type, mf.material_field_type, mf.value_as_string, mf.value_as_number, s.exact, s.prefix, s.suffix, mp_data_index
from mp_material_annotation mann,oa_material_body mbody, material_field mf, oa_target t, oa_selector s
where mann.mp_claim_id = 6
and mann.has_body = mbody.id
and mf.material_body_id = mbody.id
and mann.has_target = t.id
and t.has_selector = s.id

-- query highlight annotation
SELECT h.id, t.has_source, s.exact
FROM highlight_annotation h, oa_target t, oa_selector s
WHERE h.has_target = t.id
AND t.has_selector = s.id;


-- create tablefunc
-- psql -U postgre
-- \c mpevidence
CREATE EXTENSION tablefunc; 

-- Get fold increase from data_field table - pivot table data_field
SELECT * FROM crosstab('SELECT df.data_body_id, df.data_field_type, df.value_as_string FROM data_field df ORDER BY 1,2')
AS results(data_body_id INTEGER, direction TEXT, type TEXT, value TEXT)
WHERE type = 'Fold';


-- Get Dose information - pivot table material_field
SELECT *
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
WHERE mf.value != ''


-- Get fold increase data with claim id
SELECT md.mp_claim_id, md.creator, md.ev_supports, md.type, df.type, df.value, df.direction
FROM crosstab('SELECT df.data_body_id, df.data_field_type, df.value_as_string FROM data_field df ORDER BY 1,2')
AS df(data_body_id INTEGER, direction TEXT, type TEXT, value TEXT)
JOIN oa_data_body db ON df.data_body_id = db.id
JOIN mp_data_annotation md on db.id = md.has_body
WHERE df.type = 'Fold'
AND db.data_type = 'auc';


-- Get object dose and precipitant dose information with claim id
SELECT mm.mp_claim_id, mb.material_type, mf.duration, mf.formulation, mf.regimens, mf.value
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
JOIN oa_material_body mb ON mf.material_body_id = mb.id
JOIN mp_material_annotation mm ON mb.is_oa_body_of = mm.id
WHERE mf.value != ''


-- FUNCTIONS

CREATE OR REPLACE FUNCTION qualifierRole(boolean, boolean, boolean) 
RETURNS TEXT AS
$BODY$
BEGIN
IF $1 THEN RETURN 'subject';
ELSIF $2 THEN RETURN 'predicate';
ELSIF $3 THEN RETURN 'object';
ELSE RETURN 'error';
END IF;
END;
$BODY$ language plpgsql;

-- query mp claim
select cann.id, t.has_source, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue 
from mp_claim_annotation cann, oa_claim_body cbody, oa_target t, oa_selector s, qualifier q
where cann.has_body = cbody.id
and cann.has_target = t.id
and t.has_selector = s.id
and cbody.id = q.claim_body_id

mc.id, mc.predicate, mc.object, mc.subject


-- Claim - subject - predicate - object - pivot material_field table
SELECT *
FROM crosstab('select mc.id, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue
FROM mp_claim_annotation mc, oa_claim_body cb, oa_target t, oa_selector s, qualifier q
WHERE mc.has_body = cb.id
AND mc.has_target = t.id
AND t.has_selector = s.id
AND cb.id = q.claim_body_id ORDER BY 1,2')
AS mc(id INTEGER, predicate TEXT, object TEXT,  subject TEXT) 
