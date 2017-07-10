
SET SCHEMA 'public';

--
-- Name: attribute_definition; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE attribute_definition (
    attribute_definition_id integer NOT NULL,
    attribute_name character varying(255) NOT NULL,
    attribute_description text,
    attribute_type_concept_id integer NOT NULL,
    attribute_syntax text
);


ALTER TABLE attribute_definition OWNER TO dbmiannotator;


--
-- Name: cohort; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE cohort (
    cohort_definition_id integer NOT NULL,
    subject_id integer NOT NULL,
    cohort_start_date date NOT NULL,
    cohort_end_date date NOT NULL
);


ALTER TABLE cohort OWNER TO dbmiannotator;

--
-- Name: cohort_attribute; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE cohort_attribute (
    cohort_definition_id integer NOT NULL,
    cohort_start_date date NOT NULL,
    cohort_end_date date NOT NULL,
    subject_id integer NOT NULL,
    attribute_definition_id integer NOT NULL,
    value_as_number numeric,
    value_as_concept_id integer
);


ALTER TABLE cohort_attribute OWNER TO dbmiannotator;

--
-- Name: cohort_definition; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE cohort_definition (
    cohort_definition_id integer NOT NULL,
    cohort_definition_name character varying(255) NOT NULL,
    cohort_definition_description text,
    definition_type_concept_id integer NOT NULL,
    cohort_definition_syntax text,
    subject_concept_id integer NOT NULL,
    cohort_initiation_date date
);


ALTER TABLE cohort_definition OWNER TO dbmiannotator;

--
-- Name: domain; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE domain (
    domain_id character varying(20) NOT NULL,
    domain_name character varying(255) NOT NULL,
    domain_concept_id integer NOT NULL
);

ALTER TABLE domain OWNER TO dbmiannotator;

--
-- Name: drug_strength; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE drug_strength (
    drug_concept_id integer NOT NULL,
    ingredient_concept_id integer NOT NULL,
    amount_value numeric,
    amount_unit_concept_id integer,
    numerator_value numeric,
    numerator_unit_concept_id integer,
    denominator_unit_concept_id integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    invalid_reason character varying(1)
);


ALTER TABLE drug_strength OWNER TO dbmiannotator;

--
-- Name: concept; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE negative_concept (
    concept_id integer NOT NULL,
    concept_name character varying(255) NOT NULL,
    domain_id character varying(20) NOT NULL,
    vocabulary_id character varying(20) NOT NULL,
    concept_class_id character varying(20) NOT NULL,
    standard_concept character varying(1),
    concept_code character varying(50) NOT NULL,
);


ALTER TABLE concept OWNER TO dbmiannotator;

--
-- Name: concept_ancestor; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE concept_ancestor (
    ancestor_concept_id integer NOT NULL,
    descendant_concept_id integer NOT NULL,
    min_levels_of_separation integer NOT NULL,
    max_levels_of_separation integer NOT NULL
);


ALTER TABLE concept_ancestor OWNER TO dbmiannotator;

--
-- Name: concept_class; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE concept_class (
    concept_class_id character varying(20) NOT NULL,
    concept_class_name character varying(255) NOT NULL,
    concept_class_concept_id integer NOT NULL
);


ALTER TABLE concept_class OWNER TO dbmiannotator;

--
-- Name: concept_relationship; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE concept_relationship (
    concept_id_1 integer NOT NULL,
    concept_id_2 integer NOT NULL,
    relationship_id character varying(20) NOT NULL,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    invalid_reason character varying(1)
);


ALTER TABLE concept_relationship OWNER TO dbmiannotator;

--
-- Name: concept_synonym; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE concept_synonym (
    concept_id integer NOT NULL,
    concept_synonym_name character varying(1000) NOT NULL,
    language_concept_id integer NOT NULL
);


ALTER TABLE concept_synonym OWNER TO dbmiannotator;

--
-- Name: relationship; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE relationship (
    relationship_id character varying(20) NOT NULL,
    relationship_name character varying(255) NOT NULL,
    is_hierarchical character varying(1) NOT NULL,
    defines_ancestry character varying(1) NOT NULL,
    reverse_relationship_id character varying(20) NOT NULL,
    relationship_concept_id integer NOT NULL
);


ALTER TABLE relationship OWNER TO dbmiannotator;

--
-- Name: source_to_concept_map; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE source_to_concept_map (
    source_code character varying(50) NOT NULL,
    source_concept_id integer NOT NULL,
    source_vocabulary_id character varying(20) NOT NULL,
    source_code_description character varying(255),
    target_concept_id integer NOT NULL,
    target_vocabulary_id character varying(20) NOT NULL,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    invalid_reason character varying(1)
);


ALTER TABLE source_to_concept_map OWNER TO dbmiannotator;

--
-- Name: vocabulary; Type: TABLE; Schema: public; Owner: dbmiannotator; Tablespace: 
--

CREATE TABLE vocabulary (
    vocabulary_id character varying(20) NOT NULL,
    vocabulary_name character varying(255) NOT NULL,
    vocabulary_reference character varying(255),
    vocabulary_version character varying(255),
    vocabulary_concept_id integer NOT NULL
);


ALTER TABLE vocabulary OWNER TO dbmiannotator;

--
-- PostgreSQL database dump complete
--

