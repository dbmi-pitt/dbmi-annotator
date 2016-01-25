
var path = require('path');

module.exports = {
    
    validateUser : function(req, res) {
	var pg = require('pg');
	var conString = require('./../config/config.js');

	//console.log("[DEBUG] conStr: " + conString);
	var client = new pg.Client(conString);
	client.connect();
	
	userEmail = req.param('email');
	userPwd = req.param('pwd');

	console.log("[DEBUG] login information, email: " + userEmail + " | pwd: " + userPwd);

	if ((userEmail == null) || (userPwd == null)) {
	    console.log('[INFO] user login fail');
	    res.send("fail");
	} else {

	    var qryStr = "SELECT * FROM \"USER_INFO\" WHERE email = '" + userEmail + "' AND password = '" + userPwd +"'";

	    console.log("[DEBUG] qryStr: " + qryStr);
	    
	    var query = client.query(qryStr);

	    query.on("row", function (row, result) {
		result.addRow(row);
	    });
	
	    query.on("end", function (result) {          
		client.end();
		//res.writeHead(200, {'Content-Type': 'text/plain'});
		//res.write(JSON.stringify(result.rows, null, "    ") + "\n");
		//res.end();
		console.log("[DEBUG] result.rows: " + result.rows);
		if (result.rows != null && result.rows != ""){
		    console.log("[INFO] log in successfully");
		    //req.session.email = userEmail;
		    res.redirect('/');
		} else {
		    console.log("[INFO] log in fail");
		    res.send('bad login');
		}
	    });
	}
    }
};
