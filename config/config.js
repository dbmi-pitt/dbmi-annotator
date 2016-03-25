var config = {};
config.store = {};
config.annotator = {};

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://wen:dbmi@localhost:5432/dbmiannotator'; 

// dbmi annotator 
config.annotator.host = 'localhost';
config.annotator.port = '3000';


// annotator store
config.store.host = 'localhost';
config.store.port = '5000';


module.exports = config;
