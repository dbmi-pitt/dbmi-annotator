import sys, csv

reload(sys)  
sys.setdefaultencoding('utf8')

# create sql script for inserting dideo concepts
# reserve (-9999999, -7000000) for concept names

DIDEO_CSV = 'data/4bb83833.csv'
OUTPUT_SQL = 'data/dideo-concepts-insert.sql'

# UTILS ##############################################################################
# encode data as utf-8
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
	yield line.encode('utf-8')

        
# INSERT QUERY TEMPLATES #############################################################
def insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code):
    return "INSERT INTO public.concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (%s, '%s', '%s', '%s', '%s', '', '%s', '2000-01-01', '2099-02-22', '');" % (concept_id, concept_name.replace("'", "''"), domain_id, vocabulary_id, concept_class_id, concept_code)

def insert_concept_class_template(concept_class_id, concept_class_name, concept_class_concept_id):
    return "INSERT INTO public.concept_class (concept_class_id, concept_class_name, concept_class_concept_id) VALUES ('%s', '%s', %s);" % (concept_class_id, concept_class_name, concept_class_concept_id)


def insert_vocabulary_template(vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id):
    return "INSERT INTO public.vocabulary (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id) VALUES ('%s', '%s', '%s', '%s', %s);" % (vocabulary_id, vocabulary_name, vocabulary_reference, vocabulary_version, vocabulary_concept_id)


def insert_domain_template(domain_id, domain_name, domain_concept_id):
    return "INSERT INTO public.domain (domain_id, domain_name, domain_concept_id) VALUES ('%s', '%s', %s);" % (domain_id, domain_name, domain_concept_id)


# DELETE #############################################################################
def delete_concept_by_id():
    return "DELETE FROM public.concept WHERE concept_id BETWEEN -9999999 AND -7000000;"


def delete_concept_class_by_id():
    return "DELETE FROM public.concept_class WHERE concept_class_concept_id BETWEEN -9999999 AND -7000000;"


def delete_vocabulary_by_concept_id():
    return "DELETE FROM public.vocabulary WHERE vocabulary_concept_id BETWEEN -9999999 AND -7000000;"


def delete_domain_by_concept_id():
    return "DELETE FROM public.domain WHERE domain_concept_id BETWEEN -9999999 AND -7000000;"


# PRINT SQL ##########################################################################
# vocabulary table insert for dideo and term URI namespaces
# return: the next available concept id 
def print_vocabulary_insert_sql(concept_id):
    
    print insert_concept_template(-9999000, 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated')    
    print insert_vocabulary_template('DIDEO', 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'https://github.com/DIDEO/DIDEO', 'release 2016-10-20', -9999000)

    vocabL = ['OAE', 'NCBITaxon', 'IDO', 'ERO', 'PR', 'CHMO', 'OBI', 'GO', 'DRON', 'APOLLO_SV', 'UBERON', 'CLO', 'CL', 'GO#GO', 'OGMS', 'EFO', 'STATO', 'FMA', 'CHEBI', 'MOP', 'UO', 'INO', 'PDRO.owl#PDRO']

    for vocab in vocabL:
        print insert_concept_template(concept_id, vocab, 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated')
        print insert_vocabulary_template(vocab, vocab, '', 'release 2016-10-20', concept_id)
        concept_id += 1
    return concept_id + 1


# concept table insert for dideo terms
# return: the next available concept id 
def print_concept_insert_sql(concept_id):
    reader = csv.DictReader(utf_8_encoder(open(DIDEO_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        uri = row["uri"].split('/')[-1]
        idx = uri.rfind('_')
        vocabulary_id, concept_code = uri[:idx], uri[idx+1:]
        concept_name, synonyms = row["term"], row["alternative term"]

        print insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code)
        concept_id += 1
    return concept_id + 1


# domain table insert
# return: the next available concept id 
def print_domain_insert_sql():
    print insert_concept_template(-9900000, 'Potential drug interactions of natural product drug interactions', 'Metadata', 'Domain', 'Domain', 'OMOP generated')
    print insert_domain_template('PDDI or NPDI', 'PDDI or NPDI',  -9900000)


# concept class insert
def print_concept_class_insert_sql():
    print insert_concept_template(-9990000, 'PDDI or NPDI Test Class', 'Metadata', 'Concept Class', 'Concept Class', 'OMOP generated')    
    print insert_concept_class_template('PDDI or NPDI Class', 'PDDI or NPDI Test Class', -9990000)
    

# MAIN ###############################################################################
def print_insert_script():
    # templated inserting statements
    print_domain_insert_sql()
    print_concept_class_insert_sql()

    # dideo terms
    concept_id = -8000000
    concept_id = print_vocabulary_insert_sql(concept_id)
    concept_id = print_concept_insert_sql(concept_id)

    
def print_delete_script():
    print delete_concept_by_id()
    print delete_vocabulary_by_concept_id()
    print delete_domain_by_concept_id()
    print delete_concept_class_by_id()

    
def main():    
    print_insert_script()
    # print_delete_script()

if __name__ == '__main__':
    main()


