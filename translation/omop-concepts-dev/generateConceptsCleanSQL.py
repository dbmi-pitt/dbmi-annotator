import sys, csv

reload(sys)  
sys.setdefaultencoding('utf8')


def delete_concept_by_id():
    return "DELETE FROM public.concept WHERE concept_id BETWEEN -9999999 AND -7000000;"


def delete_concept_class_by_id():
    return "DELETE FROM public.concept_class WHERE concept_class_concept_id BETWEEN -9999999 AND -7000000;"


def delete_vocabulary_by_concept_id():
    return "DELETE FROM public.vocabulary WHERE vocabulary_concept_id BETWEEN -9999999 AND -7000000;"


def delete_domain_by_concept_id():
    return "DELETE FROM public.domain WHERE domain_concept_id BETWEEN -9999999 AND -7000000;"


def print_delete_script():
    print delete_concept_by_id()
    print delete_vocabulary_by_concept_id()
    print delete_domain_by_concept_id()
    print delete_concept_class_by_id()


def main():    
    print_delete_script()

if __name__ == '__main__':
    main()
