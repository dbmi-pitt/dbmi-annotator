SET SCHEMA 'ohdsi';

-- Get Mp claim information 
select distinct cann.id, cann.urn, t.has_source, cbody.label, met.entered_value, cann.creator, cann.date_created, s.prefix, s.exact, s.suffix, cann.rejected_statement, cann.rejected_statement_reason, cann.rejected_statement_comment, cann.negation from mp_claim_annotation cann 
join oa_claim_body cbody on cann.has_body = cbody.id 
left join method met on cann.id = met.mp_claim_id 
join oa_target t on cann.has_target = t.id 
join oa_selector s on t.has_selector = s.id;


-- Get Mp data by claim id
select dann.type, df.data_field_type, df.value_as_string, df.value_as_number, s.exact, s.prefix, s.suffix, dann.mp_data_index, dann.ev_supports, dann.rejected, dann.rejected_reason, dann.rejected_comment
from mp_data_annotation dann 
join oa_data_body dbody on dann.has_body = dbody.id 
join data_field df on df.data_body_id = dbody.id 
left join oa_target t on dann.has_target = t.id
left join oa_selector s on t.has_selector = s.id
where dann.mp_claim_id = '1';


-- Get MP Material information by claimId
select mann.type, mf.material_field_type, mf.value_as_string, mf.value_as_number, s.exact, s.prefix, s.suffix, mann.mp_data_index, mann.ev_supports
from mp_material_annotation mann join oa_material_body mbody on mann.has_body = mbody.id
join material_field mf on mf.material_body_id = mbody.id
left join oa_target t on mann.has_target = t.id
left join oa_selector s on t.has_selector = s.id
where mann.mp_claim_id = '1';


-- how many claims from amy: 336
select count(*)
from mp_claim_annotation cann, 
oa_target t, oa_selector s
where cann.has_target = t.id
and t.has_selector = s.id
and creator = 'amy'


-- how many distinct labels that amy annotated: 34
select count(distinct t.has_source)
from mp_claim_annotation cann, 
oa_target t, oa_selector s
where cann.has_target = t.id
and t.has_selector = s.id
and creator = 'amy'

-- query dideo concept codes
select * from public.concept c where c.vocabulary_id = 'DIDEO' and c.domain_id = 'PDDI' and c.concept_class_id = 'DIKB'; 


-- query all qualifiers with source and context information
select distinct q.qvalue as drug, t.has_source as source, s.exact as sentence
from qualifier q join mp_claim_annotation cann on q.claim_body_id = cann.has_body
left join oa_target t on cann.has_target = t.id
left join oa_selector s on t.has_selector = s.id
where q.subject = True or q.object = True


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

-- handle qualifier role
CREATE OR REPLACE FUNCTION qualifierRole(boolean, boolean, boolean) 
RETURNS TEXT AS
$BODY$
BEGIN
IF $1 THEN RETURN 'subject';
ELSIF $2 THEN RETURN 'predicate';
ELSIF $3 THEN RETURN 'object';
ELSE RETURN 'enzyme';
END IF;
END;
$BODY$ language plpgsql;

-- Claim - subject - predicate - object - pivot material_field table
SELECT *
FROM crosstab('select mc.id, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue
FROM mp_claim_annotation mc, oa_claim_body cb, oa_target t, oa_selector s, qualifier q
WHERE mc.has_body = cb.id
AND mc.has_target = t.id
AND t.has_selector = s.id
AND cb.id = q.claim_body_id ORDER BY 1,2')
AS mc(id INTEGER, predicate TEXT, object TEXT,  subject TEXT) 

------------------------ CREATE VIEWS -----------------------------------
-- Claim - subject - predicate - object - pivot material_field table
CREATE VIEW claim_qualifier_view AS SELECT *
FROM crosstab('select mc.id, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue
FROM mp_claim_annotation mc, oa_claim_body cb, oa_target t, oa_selector s, qualifier q
WHERE mc.has_body = cb.id
AND mc.has_target = t.id
AND t.has_selector = s.id
AND cb.id = q.claim_body_id ORDER BY 1,2')
AS mc(id INTEGER, object TEXT, predicate TEXT, subject TEXT) 


-- Get object dose and precipitant dose information with claim id
CREATE VIEW material_dose_view AS SELECT * FROM
(SELECT mm.mp_claim_id, mb.material_type, mf.duration, mf.formulation, mf.regimens, mf.value
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
JOIN oa_material_body mb ON mf.material_body_id = mb.id
JOIN mp_material_annotation mm ON mb.is_oa_body_of = mm.id
WHERE mf.value != '') AS md



-- precipitant and object dose with auc fold
WITH auc_fold AS (
SELECT d.mp_claim_id, d.creator, d.ev_supports, d.type as datatype, df.type as dftype, df.value, df.direction
FROM crosstab('SELECT df.data_body_id, df.data_field_type, df.value_as_string FROM data_field df ORDER BY 1,2')
AS df(data_body_id INTEGER, direction TEXT, type TEXT, value TEXT)
JOIN oa_data_body db ON df.data_body_id = db.id
JOIN mp_data_annotation d ON db.id = d.has_body
WHERE df.type = 'Fold'
AND mp_claim_id = '783'
AND d.creator = 'annotat2@gmail.com'
AND db.data_type = 'auc'),
p_dose AS (
SELECT m.mp_claim_id, mb.material_type, mf.drugname, mf.duration, mf.formulation, mf.regimens, mf.value
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, drugname TEXT, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
JOIN oa_material_body mb ON mf.material_body_id = mb.id
JOIN mp_material_annotation m ON mb.is_oa_body_of = m.id
WHERE m.type = 'precipitant_dose'
AND m.mp_claim_id = '783'
AND mf.value != ''),
o_dose AS (
SELECT m.mp_claim_id, mb.material_type, mf.drugname, mf.duration, mf.formulation, mf.regimens, mf.value
FROM crosstab('SELECT mf.material_body_id, mf.material_field_type, mf.value_as_string FROM material_field mf ORDER BY 1,2')
AS mf(material_body_id INTEGER, drugname TEXT, duration TEXT, formulation TEXT, regimens TEXT, value TEXT)
JOIN oa_material_body mb ON mf.material_body_id = mb.id
JOIN mp_material_annotation m ON mb.is_oa_body_of = m.id
WHERE mf.value != ''
AND m.type = 'object_dose'
AND m.mp_claim_id = '783')
SELECT * from p_dose 
join auc_fold on p_dose.mp_claim_id = auc_fold.mp_claim_id
join o_dose on o_dose.mp_claim_id = auc_fold.mp_claim_id;
