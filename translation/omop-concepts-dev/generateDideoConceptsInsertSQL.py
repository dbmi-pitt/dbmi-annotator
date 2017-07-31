import os, sys, csv, copy
from utils import dbOperation as dop
from utils import fileOperation as fop

reload(sys)  
sys.setdefaultencoding('utf8')

DIDEO_CSV = 'data/4bb83833.csv'
OUTPUT_SQL = 'data/dideo-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'cache/cache-concepts-mapping.txt'

# vocabulary table insert for dideo and term URI namespaces
# return: the next available concept id 
def write_vocabulary_insert_sql(temp_concept_id, f, cacheNameIdDict, cacheConceptIds):
    
    cpt_sql = dop.insert_concept_template(-9999000, 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated', cacheNameIdDict)
    vcb_sql = dop.insert_vocabulary_template('DIDEO', 'The Potential Drug-drug Interaction and Potential Drug-drug Interaction Evidence Ontology', 'https://github.com/DIDEO/DIDEO', 'release 2016-10-20', -9999000)
    f.write(cpt_sql + '\n')
    f.write(vcb_sql + '\n')

    vocabL = ['OAE', 'NCBITaxon', 'IDO', 'ERO', 'PR', 'CHMO', 'OBI', 'GO', 'DRON', 'APOLLO_SV', 'UBERON', 'CLO', 'CL', 'GO#GO', 'OGMS', 'EFO', 'STATO', 'FMA', 'CHEBI', 'MOP', 'UO', 'INO', 'PDRO.owl#PDRO']

    for vocab in vocabL:
        concept_id = None        
        cpt_key = 'Vocabulary;'+ vocab # reuse concept_id for vocabulary
        
        if cpt_key in cacheNameIdDict:
            concept_id = int(cacheNameIdDict[cpt_key])
        else:
            while str(temp_concept_id) in cacheConceptIds: # skip used concept id
                temp_concept_id += 1
                
            cacheNameIdDict[cpt_key] = str(temp_concept_id)
            cacheConceptIds.add(str(temp_concept_id))

        if not concept_id:
            concept_id = temp_concept_id
        
        cpt_sql1 = dop.insert_concept_template(concept_id, vocab, 'Metadata', 'Vocabulary', 'Vocabulary', 'OMOP generated', cacheNameIdDict)
        vcb_sql1 = dop.insert_vocabulary_template(vocab, vocab, '', 'release 2016-10-20', concept_id)
        
        f.write(cpt_sql1 + '\n')
        f.write(vcb_sql1 + '\n')

    return temp_concept_id + 1


# concept table insert for dideo terms
# return: the next available concept id 
def write_concept_insert_sql(temp_concept_id, f, cacheNameIdDict, cacheConceptIds):
    reader = csv.DictReader(fop.utf_8_encoder(open(DIDEO_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        uri = row["uri"].split('/')[-1]
        idx = uri.rfind('_')
        vocabulary_id, concept_code = uri[:idx], uri[idx+1:]
        concept_name, synonyms = row["term"], row["alternative term"]
        concept_id = None

        cpt_key = vocabulary_id + ';' + concept_name
        if cpt_key in cacheNameIdDict: # concept id defined
            concept_id = int(cacheNameIdDict[cpt_key])
            
        else:
            while str(temp_concept_id) in cacheConceptIds: # skip used concept id
                temp_concept_id += 1
                
            cacheNameIdDict[cpt_key] = str(temp_concept_id) # add new concept to cache
            cacheConceptIds.add(str(temp_concept_id)) # this concept id is taken

        if not concept_id:
            concept_id = temp_concept_id                

        cpt_sql = dop.insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code, cacheNameIdDict)
        f.write(cpt_sql + '\n')
        
    return temp_concept_id + 1


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
    cacheNameIdDictBefore = fop.readConceptCache(CACHE) # read cached concepts
    cacheNameIdDictAfter = copy.copy(cacheNameIdDictBefore) # for validate
    cacheConceptIds = set(cacheNameIdDictAfter.values()) # get concept ids that are taken

    print "[INFO] Read (%s) cached concepts from (%s)" % (len(cacheNameIdDictBefore), CACHE)
    
    with open(OUTPUT_SQL, 'w+') as f:
    
        # templated inserting statements
        write_domain_insert_sql(f, cacheNameIdDictAfter)
        write_concept_class_insert_sql(f, cacheNameIdDictAfter)


        concept_id = -8000000 # add new terms
        concept_id = write_vocabulary_insert_sql(concept_id, f, cacheNameIdDictAfter, cacheConceptIds)
        concept_id = write_concept_insert_sql(concept_id, f, cacheNameIdDictAfter, cacheConceptIds)

    ## VALIDATE ##
    print "[SUMMARY] Added (%s) new concepts, total (%s) concepts are cached" % (len(cacheNameIdDictAfter)-len(cacheNameIdDictBefore), len(cacheNameIdDictAfter))
    print "[VALIDATE] Check if <1> concept id not unique or not negative, <2> any exists term missing"
    for k, v in cacheNameIdDictBefore.iteritems():            
        if k not in cacheNameIdDictAfter or cacheNameIdDictAfter[k] != v:
            print "[ERROR] concept term (%s) inconsistence" % k

    for k, v in cacheNameIdDictAfter.iteritems():
        if not int(v) < 0:
            print "[ERROR] concept term (%s) is using positive id (%s)" % (k, v)

    if len(cacheNameIdDictAfter) != len(set(cacheNameIdDictAfter.values())):
        print "[ERROR] concept ids are not unique, number of concepts (%s) and number of concept ids (%s)" % (len(cacheNameIdDictAfter), len(set(cacheNameIdDictAfter.values())))
    
    fop.writeConceptCache(CACHE, cacheNameIdDictAfter) # write cached concepts
    print "[INFO] Validation done! insert script is available at (%s)" % OUTPUT_SQL
        
        
def main():    
    write_insert_script()

if __name__ == '__main__':
    main()


