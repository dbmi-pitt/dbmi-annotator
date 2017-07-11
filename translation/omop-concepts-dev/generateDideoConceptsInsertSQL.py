import os, sys, csv

reload(sys)  
sys.setdefaultencoding('utf8')

# create sql script for inserting new concepts
# reserve (-9999999, -8000000) for concept names

DIDEO_CSV = 'data/4bb83833.csv'
OUTPUT_SQL = 'data/dideo-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'data/cache-concepts-mapping.txt'

# global dict {vocabId;conceptName: conceptId}
cacheNameId = {} 

# UTILS ##############################################################################
# encode data as utf-8
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
	yield line.encode('utf-8')


# read cache concept map into global dict
def readConceptCache(cache_path):
    if os.path.isfile(cache_path):
        with open(cache_path) as f:
            lines = f.readlines()
            for line in lines:
                [vocab_id, concept_name, concept_id] = line.strip().split(';')
                cacheNameId[vocab_id + ';' + concept_name] = concept_id


def writeConceptCache(cache_path):
    with open(cache_path, 'w') as f:
        for cpt_key, concept_id in cacheNameId.iteritems():
            f.write(cpt_key+';'+str(concept_id)+'\n')
    
        
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


# PRINT SQL ##########################################################################
# vocabulary table insert for dideo and term URI namespaces
# return: the next available concept id 
def write_vocabulary_insert_sql(concept_id, f):
    
    cpt_sql = insert_concept_template(-9999000, 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated')
    vcb_sql = insert_vocabulary_template('DIDEO', 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'https://github.com/DIDEO/DIDEO', 'release 2016-10-20', -9999000)
    f.write(cpt_sql + '\n')
    f.write(vcb_sql + '\n')

    vocabL = ['OAE', 'NCBITaxon', 'IDO', 'ERO', 'PR', 'CHMO', 'OBI', 'GO', 'DRON', 'APOLLO_SV', 'UBERON', 'CLO', 'CL', 'GO#GO', 'OGMS', 'EFO', 'STATO', 'FMA', 'CHEBI', 'MOP', 'UO', 'INO', 'PDRO.owl#PDRO']

    for vocab in vocabL:
        
        cpt_key = 'Vocabulary;'+ vocab # reuse concept_id for vocabulary
        if cpt_key in cacheNameId:
            concept_id = cacheNameId[cpt_key]
        else:
            cacheNameId[cpt_key] = concept_id
        
        cpt_sql1 = insert_concept_template(concept_id, vocab, 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated')
        vcb_sql1 = insert_vocabulary_template(vocab, vocab, '', 'release 2016-10-20', concept_id)
        concept_id = int(concept_id) + 1
        
        f.write(cpt_sql1 + '\n')
        f.write(vcb_sql1 + '\n')

    return int(concept_id) + 1


# concept table insert for dideo terms
# return: the next available concept id 
def write_concept_insert_sql(concept_id, f):
    reader = csv.DictReader(utf_8_encoder(open(DIDEO_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        uri = row["uri"].split('/')[-1]
        idx = uri.rfind('_')
        vocabulary_id, concept_code = uri[:idx], uri[idx+1:]
        concept_name, synonyms = row["term"], row["alternative term"]

        cpt_key = vocabulary_id + ';' + concept_name
        if cpt_key in cacheNameId:
            concept_id = cacheNameId[cpt_key]
        else:
            cacheNameId[cpt_key] = concept_id

        cpt_sql = insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code)
        f.write(cpt_sql + '\n')
        
        concept_id = int(concept_id) + 1
    return int(concept_id) + 1


# domain table insert
# return: the next available concept id 
def write_domain_insert_sql(f):
    cpt_sql = insert_concept_template(-9900000, 'Potential drug interactions of natural product drug interactions', 'Metadata', 'Domain', 'Domain', 'OMOP generated')
    dm_sql = insert_domain_template('PDDI or NPDI', 'PDDI or NPDI',  -9900000)
    f.write(cpt_sql + '\n')
    f.write(dm_sql + '\n')
    

# concept class insert
def write_concept_class_insert_sql(f):
    cpt_sql = insert_concept_template(-9990000, 'PDDI or NPDI Test Class', 'Metadata', 'Concept Class', 'Concept Class', 'OMOP generated')    
    class_sql = insert_concept_class_template('PDDI or NPDI Class', 'PDDI or NPDI Test Class', -9990000)
    f.write(cpt_sql + '\n')
    f.write(class_sql + '\n')
    

# MAIN ###############################################################################
def write_insert_script():

    readConceptCache(CACHE) # read cached concepts
        
    with open(OUTPUT_SQL, 'w+') as f:
    
        # templated inserting statements
        write_domain_insert_sql(f)
        write_concept_class_insert_sql(f)

        # add new terms
        concept_id = -8000000
        concept_id = write_vocabulary_insert_sql(concept_id, f)
        concept_id = write_concept_insert_sql(concept_id, f)

    writeConceptCache(CACHE) # write cached concepts
    
    
def main():    
    write_insert_script()

if __name__ == '__main__':
    main()


