import os, sys, csv
from utils import dbOperation as dop
from utils import fileOperation as fop

reload(sys)  
sys.setdefaultencoding('utf8')
# reserve (-7000000, -8000000) for concept names

DRUG_CSV = 'data/drug-list-mapped.csv'
OUTPUT_SQL = 'data/drug-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'cache/cache-concepts-mapping.txt'

# insert for drug concept into concept table
# input: temp concept_id
# input: sql file
# input: concept id cache mapping file
# return: the next available concept id 
def write_concept_insert_sql(concept_id, f, cacheNameIdDict, cacheConceptIds):
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

        key = concept_name + vocabulary_id
        
        if key not in uniqConcepts:
        
            if row["conceptId"].strip() != "": # concept in vocab already
                concept_id = row["conceptId"]
            else: # add new concept
                cpt_key = vocabulary_id + ';' + concept_name
            
                if cpt_key in cacheNameIdDict:
                    concept_id = cacheNameIdDict[cpt_key]
                else:
                    while str(concept_id) in cacheConceptIds: # skip used concept id
                        concept_id += 1
                    
                    cacheNameIdDict[cpt_key] = concept_id # add new concept to cache
                    cacheConceptIds.add(concept_id)

                cpt_sql = dop.insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code, cacheNameIdDict)
            f.write(cpt_sql + '\n')

            uniqConcepts.add(key)
            concept_id = int(concept_id) + 1            
            
    return int(concept_id) + 1


# MAIN ###############################################################################
def write_insert_script():

    # dict {'vocabId;conceptName': conceptId}
    cacheNameIdDict = fop.readConceptCache(CACHE) # read cached concepts
    cacheConceptIds = set(cacheNameIdDict.values()) # get concept ids that are taken

    numBefore = len(cacheNameIdDict)
    print "[INFO] read (%s) cached concepts from (%s)" % (numBefore, CACHE)
    
    with open(OUTPUT_SQL, 'w+') as f:

        # add new terms
        concept_id = -8000000
        concept_id = write_concept_insert_sql(concept_id, f, cacheNameIdDict, cacheConceptIds)

    numAfter = len(cacheNameIdDict)
    print "[INFO] added (%s) new concepts, total (%s) concepts are cached" % (numAfter-numBefore, numAfter)
    fop.writeConceptCache(CACHE, cacheNameIdDict) # write cached concepts
        
def main():    
    write_insert_script()

if __name__ == '__main__':
    main()


