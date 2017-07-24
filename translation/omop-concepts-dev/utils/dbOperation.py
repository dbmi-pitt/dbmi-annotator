# INSERT QUERY TEMPLATES #############################################################
def insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code):
    cpt_key = vocabulary_id + ';' + str(concept_name)
    # reuse concept id
    if cpt_key in cacheNameId:
        concept_id = cacheNameId[cpt_key]
    else:
        cacheNameId[cpt_key] = concept_id
    
    return "INSERT INTO public.concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (%s, '%s', '%s', '%s', '%s', '', '%s', '2000-01-01', '2099-02-22', '');" % (concept_id, concept_name.replace("'", "''"), domain_id, vocabulary_id, concept_class_id, concept_code)


def insert_concept_class_template(concept_class_id, concept_class_name, concept_class_concept_id):
    
    return "INSERT INTO public.concept_class (concept_class_id, concept_class_name, concept_class_concept_id) VALUES ('%s', '%s', %s);" % (concept_class_id, concept_class_name, concept_class_concept_id)


def insert_vocabulary_template(vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id):    
    return "INSERT INTO public.vocabulary (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id) VALUES ('%s', '%s', '%s', '%s', %s);" % (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id)


def insert_domain_template(domain_id, domain_name, domain_concept_id):
    return "INSERT INTO public.domain (domain_id, domain_name, domain_concept_id) VALUES ('%s', '%s', %s);" % (domain_id, domain_name, domain_concept_id)
