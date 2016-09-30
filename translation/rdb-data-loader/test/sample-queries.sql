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
