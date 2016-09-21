-- ADD PLUGINS
-- PLUGIN 1: drug mention
INSERT INTO plugin(id, name, type, description, status, created) VALUES
	(1, 'Drug Mention Plugin', 'DrugMention', 'highlight drug entity as drug mention annotation.', TRUE, now());

-- PLUGIN 2: drug drug interaction
INSERT INTO plugin(id, name, type, description, status, created) VALUES
	(2, 'Drug Drug Interaction Plugin', 'DDI', 'identify drug drug interaction from sentences.', TRUE, now());

-- PLUGIN 3: micropublication
INSERT INTO plugin(id, name, type, description, status, created) VALUES
	(3, 'Micropublication Plugin', 'MP', 'identify claim and data from document based on micropublication model.', TRUE, now());


-- ADD PLUGIN SETS
-- PLUGIN SET 1: drug mention + drug drug interaction
INSERT INTO plugin_set(id, name, type, description, status, created) VALUES
	(1, 'Drug Mention and Drug Drug Interaction Plugin', 'DDI', 'identify drug drug interaction from sentences with assist of drug highlights.', TRUE, now());

-- PLUGIN SET 2: drug mention + micropublication
INSERT INTO plugin_set(id, name, type, description, status, created) VALUES
	(2, 'Drug Mention and Micropublication Plugin', 'MP', 'with the assist of drug highlights, identify claim and data from document based on micropublication model.', TRUE, now());


-- ADD PLUGIN REPLATIONSHIPS
-- SET 1: drug mention and drug drug interaction
INSERT INTO plugin_relationship(set_id, plugin_id) VALUES
	(1, 1);
INSERT INTO plugin_relationship(set_id, plugin_id) VALUES
	(1, 2);

-- SET 2: drug mention and micropublication
INSERT INTO plugin_relationship(set_id, plugin_id) VALUES
	(2, 1);
INSERT INTO plugin_relationship(set_id, plugin_id) VALUES
	(2, 3);
