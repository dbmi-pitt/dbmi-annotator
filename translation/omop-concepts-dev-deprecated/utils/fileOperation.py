import os

# encode data as utf-8
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
	yield line.encode('utf-8')


# read local cache concept mapping file
# input: cache file path
# return dict {vocabId;conceptName: conceptId}
def readConceptCache(cache_path):
    cacheDict = {}
    if os.path.isfile(cache_path):
        with open(cache_path) as f:
            lines = f.readlines()
            for line in lines:
                if ';' in line:
                    [vocab_id, concept_name, concept_id] = line.strip().split(';')
                    cacheDict[vocab_id + ';' + concept_name] = concept_id

    return cacheDict


# update local cache concept mapping
# input: cache file path
# input: dict {vocabId;conceptName: conceptId}
def writeConceptCache(cache_path, cacheDict):
    with open(cache_path, 'w') as f:
        for cpt_key, concept_id in sorted(cacheDict.iteritems()):
            f.write(cpt_key+';'+str(concept_id)+'\n')        
