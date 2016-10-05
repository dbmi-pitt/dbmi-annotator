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

-- how many claims from amy: 448
select count(*)
from mp_claim_annotation cann, 
oa_target t, oa_selector s
where cann.has_target = t.id
and t.has_selector = s.id
and creator = 'katrina'

-- how many distinct labels that katrina annotated: 32
select count(distinct t.has_source)
from mp_claim_annotation cann, 
oa_target t, oa_selector s
where cann.has_target = t.id
and t.has_selector = s.id
and creator = 'katrina'

-- dose formulation and regimens options
-- Oral, IV, transdermal
SELECT distinct m.value_as_string 
FROM material_field m
WHERE m.material_field_type = 'formulation'

-- Q8, QID, BID, QD, TID, SD, Daily, Q12 
SELECT distinct m.value_as_string 
FROM material_field m
WHERE m.material_field_type = 'regimens'

-- data type and direction options
-- UNK, Percent, Fold
SELECT distinct d.value_as_string 
FROM data_field d
WHERE d.data_field_type = 'type'

-- UNK, Increase, Decrease
SELECT distinct d.value_as_string 
FROM data_field d
WHERE d.data_field_type = 'direction'
