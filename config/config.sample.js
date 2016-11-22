var config = {};
config.store = {};
config.annotator = {};
config.elastico = {};
config.profile = {};
config.apache2 = {};

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://postgres:<password>@localhost:5432/dbmiannotator'; 

// apache2 
config.apache2.host = 'localhost';
config.apache2.port = '80'

// dbmi annotator 
config.annotator.host = 'localhost';
config.annotator.port = '3000';

// annotator store
config.store.host = 'localhost';
config.store.port = '5000';

// elastico
config.elastico.host = 'localhost';
config.elastico.port = '9200';

// user default profile
config.profile.def = 'MP';
config.profile.pluginSetL = [];
config.profile.userProfile = {};

module.exports = config;
