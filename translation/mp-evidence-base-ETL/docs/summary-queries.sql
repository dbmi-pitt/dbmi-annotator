-- AnnotationPress Elasticsearch to PostgreSQL ############################

-- Get qualifiers that don't have concept code mapped
SELECT DISTINCT qvalue from qualifier q WHERE q.predicate = False and qvalue != '' and concept_code is NULL;


-- domeo ETL csv to PostgreSQL ############################################
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
