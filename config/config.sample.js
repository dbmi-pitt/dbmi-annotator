var config = {};
config.annotator = {};
config.profile = {};
config.apache2 = {};
config.store = {};
config.protocal = 'http' // options: http or https

// postgres db
config.postgres = process.env.DATABASE_URL || 'postgres://postgres:<password>@<domain name>:5432/dbmiannotator'; 

// apache2 
config.apache2.host = '<host name>';
config.apache2.port = '80'  // 443 for https

// dbmi annotator 
config.annotator.host = '<host name>';
config.annotator.port = '3000';

// annotator store
config.store.host = '<host name>';
config.store.port = '5000';

// user default profile
config.profile.def = 'MP';
config.profile.pluginSetL = [];
config.profile.userProfile = {};

//article list
//vlan
config.article = ['dailymed','pmc','wiley','elsevier','springer','sage','taylor','wolters','future','test-experiment','test-pdf'];
//public
//config.article = ['dailymed','pmc';

module.exports = config;
