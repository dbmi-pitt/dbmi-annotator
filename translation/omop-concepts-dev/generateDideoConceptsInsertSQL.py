import os, sys, csv
from utils import dbOperation as dop
from utils import fileOperation as fop

reload(sys)  
sys.setdefaultencoding('utf8')
# reserve (-7000000, -8000000) for concept names

DIDEO_CSV = 'data/4bb83833.csv'
OUTPUT_SQL = 'data/dideo-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'data/cache-concepts-mapping.txt'

# vocabulary table insert for dideo and term URI namespaces
# return: the next available concept id 
def write_vocabulary_insert_sql(concept_id, f, cacheNameIdDict):
    
    cpt_sql = dop.insert_concept_template(-9999000, 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated', cacheNameIdDict)
    vcb_sql = dop.insert_vocabulary_template('DIDEO', 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'https://github.com/DIDEO/DIDEO', 'release 2016-10-20', -9999000)
    f.write(cpt_sql + '\n')
    f.write(vcb_sql + '\n')

    vocabL = ['OAE', 'NCBITaxon', 'IDO', 'ERO', 'PR', 'CHMO', 'OBI', 'GO', 'DRON', 'APOLLO_SV', 'UBERON', 'CLO', 'CL', 'GO#GO', 'OGMS', 'EFO', 'STATO', 'FMA', 'CHEBI', 'MOP', 'UO', 'INO', 'PDRO.owl#PDRO']

    for vocab in vocabL:
        
        cpt_key = 'Vocabulary;'+ vocab # reuse concept_id for vocabulary
        if cpt_key in cacheNameIdDict:
            concept_id = cacheNameIdDict[cpt_key]
        else:
            cacheNameIdDict[cpt_key] = concept_id
        
        cpt_sql1 = dop.insert_concept_template(concept_id, vocab, 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated', cacheNameIdDict)
        vcb_sql1 = dop.insert_vocabulary_template(vocab, vocab, '', 'release 2016-10-20', concept_id)
        concept_id = int(concept_id) + 1
        
        f.write(cpt_sql1 + '\n')
        f.write(vcb_sql1 + '\n')

    return int(concept_id) + 1


# concept table insert for dideo terms
# return: the next available concept id 
def write_concept_insert_sql(concept_id, f, cacheNameIdDict):
    reader = csv.DictReader(fop.utf_8_encoder(open(DIDEO_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        uri = row["uri"].split('/')[-1]
        idx = uri.rfind('_')
        vocabulary_id, concept_code = uri[:idx], uri[idx+1:]
        concept_name, synonyms = row["term"], row["alternative term"]

        cpt_key = vocabulary_id + ';' + concept_name
        if cpt_key in cacheNameIdDict:
            concept_id = cacheNameIdDict[cpt_key]
        else:
            cacheNameIdDict[cpt_key] = concept_id

        cpt_sql = dop.insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code, cacheNameIdDict)
        f.write(cpt_sql + '\n')
        
        concept_id = int(concept_id) + 1
    return int(concept_id) + 1


# domain table insert
# return: the next available concept id 
def write_domain_insert_sql(f, cacheNameIdDict):
    cpt_sql = dop.insert_concept_template(-9900000, 'Potential drug interactions of natural product drug interactions', 'Metadata', 'Domain', 'Domain', 'OMOP generated', cacheNameIdDict)
    dm_sql = dop.insert_domain_template('PDDI or NPDI', 'PDDI or NPDI',  -9900000)
    f.write(cpt_sql + '\n')
    f.write(dm_sql + '\n')
    

# concept class insert
def write_concept_class_insert_sql(f, cacheNameIdDict):
    cpt_sql = dop.insert_concept_template(-9990000, 'PDDI or NPDI Test Class', 'Metadata', 'Concept Class', 'Concept Class', 'OMOP generated', cacheNameIdDict)    
    class_sql = dop.insert_concept_class_template('PDDI or NPDI Class', 'PDDI or NPDI Test Class', -9990000)
    f.write(cpt_sql + '\n')
    f.write(class_sql + '\n')
    

# MAIN ###############################################################################
def write_insert_script():

    # dict {'vocabId;conceptName': conceptId}
    cacheNameIdDict = fop.readConceptCache(CACHE) # read cached concepts
    
    with open(OUTPUT_SQL, 'w+') as f:
    
        # templated inserting statements
        write_domain_insert_sql(f, cacheNameIdDict)
        write_concept_class_insert_sql(f, cacheNameIdDict)

        # add new terms
        concept_id = -8000000
        concept_id = write_vocabulary_insert_sql(concept_id, f, cacheNameIdDict)
        concept_id = write_concept_insert_sql(concept_id, f, cacheNameIdDict)

    fop.writeConceptCache(CACHE, cacheNameIdDict) # write cached concepts
        
def main():    
    write_insert_script()

if __name__ == '__main__':
    main()


