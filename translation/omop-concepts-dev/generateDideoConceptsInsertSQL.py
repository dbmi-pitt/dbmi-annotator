import sys, csv

reload(sys)  
sys.setdefaultencoding('utf8')

DIDEO_CSV = 'data/4bb83833.csv'
OUTPUT_SQL = 'data/dideo-concepts-insert.sql'

# encode data as utf-8
def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
	yield line.encode('utf-8')


def insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code):
    
    return "INSERT INTO public.concept (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept, concept_code, valid_start_date, valid_end_date, invalid_reason) VALUES (%s, '%s', '%s', '%s', '%s', '', '%s', '2000-01-01', '2099-02-22', '');" % (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code)
        

def delete_concept_by_id():
    return "DELETE * FROM public.concept WHERE concept_id BETWEEN -8000000 AND -7000000"


def main():
    reader = csv.DictReader(utf_8_encoder(open(DIDEO_CSV, 'r')))
    next(reader, None) # skip the header

    domain_id = "Metadata"; concept_class_id = "Domain"
    concept_id = -8000000

    for row in reader:
        uri = row["uri"].split('/')[-1]
        idx = uri.rfind('_')
        vocabulary_id, concept_code = uri[:idx], uri[idx+1:]
        concept_name, synonyms = row["term"], row["alternative term"]

        print insert_concept_template(concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, concept_code)        
        concept_id += 1
    

if __name__ == '__main__':
    main()
