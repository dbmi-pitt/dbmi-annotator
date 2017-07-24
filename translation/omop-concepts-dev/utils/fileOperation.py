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


def writeConceptCache(cache_path, cacheDict):
    with open(cache_path, 'w') as f:
        for cpt_key, concept_id in cacheDict.iteritems():
            f.write(cpt_key+';'+str(concept_id)+'\n')        
