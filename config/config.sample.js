var config = {};
config.store = {};
config.annotator = {};
config.elastico = {};
config.profile = {};

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://<username>:<password>@<hostname/ip addresss>:<port>/<schema name>'; 

// dbmi annotator 
config.annotator.host = 'host name or ip address';
config.annotator.port = 'port';


// annotator store
config.store.host = 'host name or ip address';
config.store.port = 'port';

// elastico
config.elastico.host = 'host name or ip address';
config.elastico.port = 'port';

// user default profile
config.profile.def = 'MP';
config.profile.pluginSetL = [];
config.profile.userProfile = {};

module.exports = config;
