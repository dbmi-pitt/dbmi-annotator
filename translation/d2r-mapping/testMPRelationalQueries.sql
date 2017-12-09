-- find a claim mentioning desvenlafaxine and midazolam in the claim text
select * 
from ohdsi.mp_claim_annotation ca 
  inner join ohdsi.oa_claim_body cb on ca.has_body = cb.id
  inner join ohdsi.qualifier q on q.claim_body_id = cb.id
where claim_text like '%desven%midazolam%';

-- We want to create an MP that argues for each distinct claim. How many distinct claims do we have?
select * 
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
order by qsubj.qvalue, qpred.qvalue, qobj.qvalue
;    

-- how any distinct predicates
select distinct qpred.qvalue 
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
;

-- currently (12/9/17) there are 877 claim records total
select count(*) from (
select  qsubj.qvalue, qpred.qvalue, qobj.qvalue, qsubj.concept_code, qobj.concept_code
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
order by qsubj.qvalue, qpred.qvalue, qobj.qvalue
) t1
;    

-- currently (12/9/17) there are 677 unique claims based on coded subject, predicate, object triples. This includes NULL coded values 
-- which are indicitive of non-mapped enties in the subject and object fields
select qsc, qpv, qoc, count(claimid) 
from (
select qsubj.claim_body_id claimid, qsubj.qvalue qsv, qpred.qvalue qpv, qobj.qvalue qov, qsubj.concept_code qsc, qobj.concept_code qoc
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
order by qsubj.qvalue, qpred.qvalue, qobj.qvalue
) t1
group by qsc, qpv, qoc
order by qsc, qpv, qoc
;

-- human readable list of distinct claims with counts of related statements (supporting and challenging) as of 12/9/2017 with null 
-- subject and object concepts removed : count = 561.
-- NOTE: Enhancement - The vocabulary IDs that we are using in the qualifier tables should be the string IDs used by concept records, not the vocabulary concept_ids.
--                     Changing this in the tables will simplify the query below.       
select qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id, count(claimid) 
from (
select qsubj.claim_body_id claimid, 
       qsubj.qvalue qsv, 
       qpred.qvalue qpv, 
       qobj.qvalue qov, 
       qsubj.concept_code qsc, 
       qobj.concept_code qoc, 
       qsubj.vocabulary_id qsvid, 
       qobj.vocabulary_id qovid
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
) t1 inner join public.concept qsc_c on qsc = qsc_c.concept_code
     inner join public.vocabulary qsvv on qsc_c.vocabulary_id = qsvv.vocabulary_id
     inner join public.concept qoc_c on qoc = qoc_c.concept_code
     inner join public.vocabulary qovv on qoc_c.vocabulary_id = qovv.vocabulary_id
  where qsvid = qsvv.vocabulary_concept_id
    and qovid = qovv.vocabulary_concept_id
group by qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id
order by qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id
;

-- (12/10/17) further refining counts so that rejected claims are removed and its clear what is a negated claim
---- first, just learning about the structure and content of the tables
select *
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
    inner join ohdsi.oa_claim_body cb on cb.id = qsubj.claim_body_id
    inner join ohdsi.mp_claim_annotation on cb.is_oa_body_of = ohdsi.mp_claim_annotation.id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
;

----- seeing how many rejected and negated claim annotationsthere are
--- Rejected claim annotation (actually, a rejection of the evidence support for the claim) : currently 0
select count(*)
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
    inner join ohdsi.oa_claim_body cb on cb.id = qsubj.claim_body_id
    inner join ohdsi.mp_claim_annotation on cb.is_oa_body_of = ohdsi.mp_claim_annotation.id
where rejected_statement = True
  and qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
;

--- Negated statements - currently 141 -- These will be MP:Statements that MP:Challenges an MP:Claim
--- NOTE: not able to pull in references at this time - No data in the refereces table!
-- select count(*)
select *
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
    inner join ohdsi.oa_claim_body cb on cb.id = qsubj.claim_body_id
    inner join ohdsi.mp_claim_annotation on cb.is_oa_body_of = ohdsi.mp_claim_annotation.id
    -- left outer join ohdsi.claim_reference_relationship crr on ohdsi.mp_claim_annotation.id = crr.mp_claim_id 
    -- inner join ohdsi.mp_reference mpr on crr.mp_reference_id = mpr.id
where negation = True
  and qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
;

--- Positive statements - currently 664 -- These will be MP:Statements that MP:Supports an MP:Claim
--- NOTE: not able to pull in references at this time - No data in the refereces table!
select count(*)
-- select *
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
    inner join ohdsi.oa_claim_body cb on cb.id = qsubj.claim_body_id
    inner join ohdsi.mp_claim_annotation on cb.is_oa_body_of = ohdsi.mp_claim_annotation.id
    -- left outer join ohdsi.claim_reference_relationship crr on ohdsi.mp_claim_annotation.id = crr.mp_claim_id 
    -- inner join ohdsi.mp_reference mpr on crr.mp_reference_id = mpr.id
where negation = False
  and qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
;

--------------------------------------------------------------------
-- Create a new table to hold the individual qualified claims. This will be used in the D2R mapper to 
-- create a single MP and MP:Claim for each record using the MP:Argues predicate. Then, each statement will be related to 
-- the relevant MP:Claim using MP:Supports and MP:Challenges as is appropriate
DROP TABLE IF EXISTS ohdsi.mp_micropublication;
CREATE TABLE ohdsi.mp_micropublication(
 id SERIAL PRIMARY KEY,
 subj_concept_name varchar(255),
 subj_concept_id integer, 
 subj_vocabulary_id varchar(255), 
 predicate text,
 obj_concept_name varchar(255),
 obj_concept_id integer, 
 obj_vocabulary_id varchar(255),
 attribution_as_author varchar(255),
 attribution_as_editor varchar(255),
 attribution_as_publisher varchar(255),
 attribution_as_curator varchar(255)
);

INSERT INTO ohdsi.mp_micropublication 
   (subj_concept_name, subj_concept_id, subj_vocabulary_id, predicate, obj_concept_name, obj_concept_id, obj_vocabulary_id,
   attribution_as_author, attribution_as_editor, attribution_as_publisher, attribution_as_curator)
SELECT qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id,
      'https://orcid.org/0000-0002-2993-2085', 'https://orcid.org/0000-0002-2993-2085','https://orcid.org/0000-0002-2993-2085','https://orcid.org/0000-0002-2993-2085' 
FROM (
select qsubj.claim_body_id claimid, 
       qsubj.qvalue qsv, 
       qpred.qvalue qpv, 
       qobj.qvalue qov, 
       qsubj.concept_code qsc, 
       qobj.concept_code qoc, 
       qsubj.vocabulary_id qsvid, 
       qobj.vocabulary_id qovid
from 
ohdsi.qualifier qsubj inner join ohdsi.qualifier qpred on qsubj.claim_body_id = qpred.claim_body_id
    inner join ohdsi.qualifier qobj on qsubj.claim_body_id = qobj.claim_body_id
where qsubj.subject = True 
  and qpred.predicate = True
  and qobj.object = True
  and qsubj.concept_code is not null
  and qobj.concept_code is not null
) t1 inner join public.concept qsc_c on qsc = qsc_c.concept_code
     inner join public.vocabulary qsvv on qsc_c.vocabulary_id = qsvv.vocabulary_id
     inner join public.concept qoc_c on qoc = qoc_c.concept_code
     inner join public.vocabulary qovv on qoc_c.vocabulary_id = qovv.vocabulary_id
  where qsvid = qsvv.vocabulary_concept_id
    and qovid = qovv.vocabulary_concept_id
group by qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id
order by qsc_c.concept_name, qsc_c.concept_id, qsc_c.vocabulary_id, qpv, qoc_c.concept_name, qoc_c.concept_id, qoc_c.vocabulary_id
;
