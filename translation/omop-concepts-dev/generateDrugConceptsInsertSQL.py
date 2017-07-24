import os, sys, csv
from utils import dbOperation as dop
from utils import fileOperation as fop

reload(sys)  
sys.setdefaultencoding('utf8')
# reserve (-7000000, -8000000) for concept names

DRUG_CSV = 'data/drug-list-mapped.csv'
OUTPUT_SQL = 'data/drug-concepts-insert.sql'

# cache file, line: vocabId;conceptName;conceptId
CACHE = 'data/cache-concepts-mapping.txt'


# insert for drug concept into concept table
# input: temp concept_id
# input: sql file
# input: concept id cache mapping file
# return: the next available concept id 
def write_concept_insert_sql(concept_id, f, cacheNameIdDict):
    reader = csv.DictReader(fop.utf_8_encoder(open(DRUG_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    for row in reader:
        drug_name, concept_name = row["name"], row["concept name"]

        # use rxnorm if it's available
        if row["RxNorm"].strip() != "":
            vocabulary_id = "RxNorm"
            concept_code = row["RxNorm"]

        # use ndf-rt code when don't have rxnorm
        elif row["NDFRT"].strip() != "":
            vocabulary_id = "NDFRT"
            concept_code = row["NDFRT"]

        # use mesh code when don't have rxnorm and ndf-rt
        elif row["MESH"].strip() != "":
            vocabulary_id = "MESH"
            concept_code = row["MESH"]

        if row["conceptId"].strip() != "":
            concept_id = row["conceptId"]
        else:
            cpt_key = vocabulary_id + ';' + concept_name
            
            if cpt_key in cacheNameIdDict:
                concept_id = cacheNameIdDict[cpt_key]
            else:
                cacheNameIdDict[cpt_key] = concept_id

        cpt_sql = dop.insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code, cacheNameIdDict)
        f.write(cpt_sql + '\n')
        
        concept_id = int(concept_id) + 1
    return int(concept_id) + 1


# MAIN ###############################################################################
def write_insert_script():

    # dict {'vocabId;conceptName': conceptId}
    cacheNameIdDict = fop.readConceptCache(CACHE) # read cached concepts
    
    with open(OUTPUT_SQL, 'w+') as f:

        # add new terms
        concept_id = -8000000
        concept_id = write_concept_insert_sql(concept_id, f, cacheNameIdDict)

    fop.writeConceptCache(CACHE, cacheNameIdDict) # write cached concepts
        
def main():    
    write_insert_script()

if __name__ == '__main__':
    main()


