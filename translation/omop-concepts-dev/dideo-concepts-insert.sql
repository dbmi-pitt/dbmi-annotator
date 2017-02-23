-- DIDEO CONCEPTS --

-- TABLE DOMAIN
INSERT INTO domain (domain_id, domain_name, domain_concept_id) VALUES ('PDDI', 'PDDI', 99);

-- TABLE CONCEPT_CLASS
INSERT INTO concept_class (concept_class_id, concept_class_name, concept_class_concept_id) VALUES ('DIKB', 'Drug Interaction Knowledge Base', -9999999);

-- TABLE VOCABULARY
INSERT INTO vocabulary (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id) VALUES ('DIDEO', 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'https://github.com/DIDEO/DIDEO', 'release 2016-10-20', -9999998);

-- TABLE CONCEPT

-- interact_with
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900001, 'metabolic potential drug-drug interaction', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000015', '2017-02-22', '2099-02-22', '');

-- drug product and active ingredient
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900002, 'drug product', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000005', '2017-02-22', '2099-02-22', '');

-- enzyme
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900003, 'enzyme', 'PDDI', 'DIDEO', 'DIKB', '', 'OBI_0000427', '2017-02-22', '2099-02-22', '');

-- precipitant role
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900004, 'precipitant drug role', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000013', '2017-02-22', '2099-02-22', '');

-- object role
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900005, 'object drug role', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000012', '2017-02-22', '2099-02-22', '');

-- auc ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900006, 'area under the curve ratio', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000093', '2017-02-22', '2099-02-22', '');

-- cmax ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900007, 'drug maximum concentration ratio', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000099', '2017-02-22', '2099-02-22', '');

-- clearance ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900008, 'hepatic clearance ratio', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000101', '2017-02-22', '2099-02-22', '');

-- halflife ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900009, 'half-life ratio', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000100', '2017-02-22', '2099-02-22', '');

-- phenotype ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900010, 'evidence information from phenotyped pharmacokinetic trial', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000103', '2017-02-22', '2099-02-22', '');

-- genotype ratio
INSERT INTO concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept , concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (-9900011, 'evidence information from genotyped pharmacokinetic trial', 'PDDI', 'DIDEO', 'DIKB', '', 'DIDEO_00000076', '2017-02-22', '2099-02-22', '');
