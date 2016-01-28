var bcrypt   = require('bcrypt-nodejs');
 
module.exports = function(sequelize, Sequelize) {
    var User = sequelize.define('user', {
	id: {type: Sequelize.INTEGER, unique: true, primaryKey: true, autoIncrement: true} ,
	uid: Sequelize.TEXT,
	username: Sequelize.TEXT,
	admin: Sequelize.BOOLEAN,
	manager: Sequelize.BOOLEAN,
	email: Sequelize.TEXT,
	status: Sequelize.INTEGER,
	last_login_date: Sequelize.DATE,
	registered_date: Sequelize.DATE,
	activation_id: Sequelize.INTEGER,
	password: Sequelize.TEXT
    },
				{classMethods:
				 {
				     validPassword: function(password1, password2){
			    		 return bcrypt.compareSync(password1, password2);
				     },
				     generateHash: function(password){
			    		 return bcrypt.hashSync(password, bcrypt.genSaltSync(8), null);
				     }
				 }
				}			     
				
			       );
    
    return User;
}




