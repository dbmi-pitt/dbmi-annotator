module.exports = function(sequelize, Sequelize) {
    var Plugin = sequelize.define('plugin', {
	    id: {type: Sequelize.INTEGER, unique: true, primaryKey: true, autoIncrement: true} ,
	    name: Sequelize.TEXT,
	    type: Sequelize.TEXT,
	    description: Sequelize.TEXT,
        status: Sequelize.BOOLEAN,
	    created: Sequelize.DATE,
    });
    return Plugin;
}




