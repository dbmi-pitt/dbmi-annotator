var config = {};
config.store = {};
config.annotator = {};
config.elastico = {};
config.profile = {};
config.apache2 = {};

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://postgres:<password>@<domain name>:5432/dbmiannotator'; 

// apache2 
config.apache2.host = '<domain name>';
config.apache2.port = '80'

// dbmi annotator 
config.annotator.host = '<domain name>';
config.annotator.port = '3000';

// user default profile
config.profile.def = 'MP';
config.profile.pluginSetL = [];
config.profile.userProfile = {};

module.exports = config;
