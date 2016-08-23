var config = {};
config.store = {};
config.annotator = {};
config.elastico = {};
config.profile = {};

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://postgres:!Yr5402874@localhost:5432/dbmiannotator'; 

// dbmi annotator 
config.annotator.host = 'localhost';
config.annotator.port = '3000';


// annotator store
config.store.host = 'localhost';
config.store.port = '5000';

// elastico
config.elastico.host = 'localhost';
config.elastico.port = '9250';

// user default profile
config.profile.def = 'MP';
config.profile.pluginSetL = [];
config.profile.userProfile = {};

module.exports = config;