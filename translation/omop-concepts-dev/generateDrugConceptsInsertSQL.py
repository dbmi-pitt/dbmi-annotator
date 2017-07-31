import os, sys, csv, copy
from utils import dbOperation as dop
from utils import fileOperation as fop

reload(sys)  
sys.setdefaultencoding('utf8')

DRUG_CSV = 'data/drug-list-mapped.csv'
OUTPUT_SQL = 'data/drug-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'cache/cache-concepts-mapping.txt'

# insert for drug concept into concept table
# input: temp concept_id, sql file, cached mapping of concept and id, used set of concept id 
# return: the next available concept id 
def write_concept_insert_sql(temp_concept_id, f, cacheNameIdDict, cacheConceptIds):
    reader = csv.DictReader(fop.utf_8_encoder(open(DRUG_CSV, 'r')))
    next(reader, None) # skip the header
    uniqConcepts = set() # keep unique concepts by concept name and vocabulary id

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        drug_name, concept_name = row["name"], row["concept name"]
        if drug_name == "" or concept_name == "":
            continue

        # use rxnorm if it's available, RxNorm concept id: 44819104
        if row["RxNorm"].strip() != "":
            vocabulary_id = "RxNorm"
            concept_code = row["RxNorm"]

        # use ndf-rt code when don't have rxnorm, NDFRT: 44819103
        elif row["NDFRT"].strip() != "":
            vocabulary_id = "NDFRT"
            concept_code = row["NDFRT"]

        # use mesh code when don't have rxnorm and ndf-rt, MESH: 44819136
        elif row["MESH"].strip() != "":
            vocabulary_id = "MESH"
            concept_code = row["MESH"]

        cpt_key = vocabulary_id + ';' + concept_name
        
        if cpt_key not in uniqConcepts and row["conceptId"].strip() == "": # concept not in vocab and not duplication, add new
            concept_id = None
            if cpt_key in cacheNameIdDict: # concept id defined
                concept_id = int(cacheNameIdDict[cpt_key])
                    
            else: # get next temp concept id
                while str(temp_concept_id) in cacheConceptIds: # skip used concept id
                    temp_concept_id += 1

                cacheNameIdDict[cpt_key] = str(temp_concept_id) # add new concept to cache
                cacheConceptIds.add(str(temp_concept_id))

            if not concept_id:
                concept_id = temp_concept_id
                    
            cpt_sql = dop.insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code, cacheNameIdDict)
            f.write(cpt_sql + '\n')            
            uniqConcepts.add(cpt_key)
            
    return temp_concept_id + 1


# MAIN ###############################################################################
def write_insert_script():

    # dict {'vocabId;conceptName': conceptId}
    cacheNameIdDictBefore = fop.readConceptCache(CACHE) # read cached concepts
    cacheNameIdDictAfter = copy.copy(cacheNameIdDictBefore) # for validate
    cacheConceptIds = set(cacheNameIdDictAfter.values()) # get concept ids that are taken

    print "[INFO] Read (%s) cached concepts from (%s)" % (len(cacheNameIdDictBefore), CACHE)
    
    with open(OUTPUT_SQL, 'w+') as f:
        concept_id = -8000000 # add new terms
        concept_id = write_concept_insert_sql(concept_id, f, cacheNameIdDictAfter, cacheConceptIds)

    ## VALIDATE ##
    print "[SUMMARY] Added (%s) new concepts, total (%s) concepts are cached" % (len(cacheNameIdDictAfter)-len(cacheNameIdDictBefore), len(cacheNameIdDictAfter))
    print "[VALIDATE] Check if (1) concept id not unique or not negative, (2) any existing term miss in cache file"
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


