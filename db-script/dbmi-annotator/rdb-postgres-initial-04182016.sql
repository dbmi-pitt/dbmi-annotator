-- ADD PLUGINS
-- PLUGIN 1: drug mention
INSERT INTO plugin(name, description, status, created) VALUES
	('Drug Mention Plugin', 'highlight drug entity as drug mention annotation', TRUE, now());

-- PLUGIN 2: drug drug interaction
INSERT INTO plugin(name, description, status, created) VALUES
	('Drug Drug Interaction Plugin', 'identify drug drug interaction from sentences', TRUE, now());

-- PLUGIN 3: micropublication
INSERT INTO plugin(name, description, status, created) VALUES
	('Micropublication Plugin', 'identify claim and data from document based on micropublication model', TRUE, now());

-- ADD PLUGIN SETS
-- SET 1: drug mention and drug drug interaction
INSERT INTO plugin_set(set_id, plugin_id, status, created) VALUES
	(1, 1, TRUE, now());
INSERT INTO plugin_set(set_id, plugin_id, status, created) VALUES
	(1, 2, TRUE, now());

-- SET 2: micropublication
INSERT INTO plugin_set(set_id, plugin_id, status, created) VALUES
	(2, 1, TRUE, now());
INSERT INTO plugin_set(set_id, plugin_id, status, created) VALUES
	(2, 3, TRUE, now());
