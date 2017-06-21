ALTER TABLE "public"."domain" ADD CONSTRAINT "xpk_domain" PRIMARY KEY (domain_id);
ALTER TABLE "public"."vocabulary" ADD CONSTRAINT "xpk_vocabulary" PRIMARY KEY (vocabulary_id);
ALTER TABLE "public"."concept_relationship" ADD CONSTRAINT "xpk_concept_relationship" PRIMARY KEY (concept_id_1, concept_id_2, relationship_id);
ALTER TABLE "public"."concept_class" ADD CONSTRAINT "xpk_concept_class" PRIMARY KEY (concept_class_id);
ALTER TABLE "public"."concept_ancestor" ADD CONSTRAINT "xpk_concept_ancestor" PRIMARY KEY (ancestor_concept_id, descendant_concept_id);
ALTER TABLE "public"."concept" ADD CONSTRAINT "xpk_concept" PRIMARY KEY (concept_id);
