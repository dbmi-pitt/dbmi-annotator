var pg = require('pg');
var LocalStrategy = require('passport-local').Strategy;
//var User = require('./../models/user').User;
var uuid = require('node-uuid');
config = require('./config.js');

// expose this function to our app using module.exports
module.exports = function(passport, User) {

    // passport session setup ==================================================

    passport.serializeUser(function(user, done) {
        //console.log(user);
        var sessionUser = {id: user.id, uid: user.uid, username: user.username, email: user.email}
        //done(null, user.id); 
        done(null, sessionUser);
    });

    passport.deserializeUser(function(sessionUser, done) {
    //passport.deserializeUser(function(id, done) {
	    // User.findById(id).then(function(user){
	    //     done(null,user);
	    // });
        done(null, sessionUser);
    });


    // LOCAL SIGNUP ============================================================

    passport.use('local-signup', new LocalStrategy({
        usernameField : 'email',
        passwordField : 'password',
        profileSetField: 'profile',
        passReqToCallback : true // allows us to pass back the entire request to the callback
    }, function(req, email, password, done) {
	console.log("in passport validation");
        console.log(req.body.profile);
        // User.findOne wont fire unless data is sent back
        process.nextTick(function() {
	    if (!req.repassword)
	    
            User.findOne({where:{'email': email}})
		.then(function(user){
		    
		    if (user) {
			console.log("[INFO] register - user exists");
			return done(null, false, req.flash('signupMessage', 'That email is already taken.'));
		    } else {
			    console.log("[INFO] register - create new user");
                userId = uuid.v1();
			    
			    User.create({
			        uid : userId,
			        username : req.param('username'),
			        admin : 0,
			        manager : 0,
			        email : email,
			        status : 0,
			        last_login_date : new Date(),
			        registered_date : new Date(),
			        activation_id : 0,
			        password : User.generateHash(password)
			    }).then(function (user){
                    // add default user profile MP 
                    pg.connect(config.postgres, function(err, client, done) {
                        client.query('INSERT INTO user_profile(uid, set_id, status, created) values($1, (SELECT id FROM plugin_set WHERE type = $2), $3, now())', [userId, 'MP', true]); 
                    });
			        return done(null, user);
                });    

	        }
		});
	    });
    }));

// LOGIN =============================================================


    passport.use('local-login', new LocalStrategy({
        usernameField : 'email',
        passwordField : 'password',
        passReqToCallback : true // allows to pass back the entire request to the callback
    }, function(req, email, password, done) { 

	User.findOne({where:{'email' : email}})
	    .then(function(user){
		
		if (!user){
		    return done(null, false, req.flash('loginMessage', 'No user found.'));
		}
		else {
		    
		    if (!User.validPassword(password, user.password))
		    	return done(null, false, req.flash('loginMessage', 'Oops! Wrong password.'));
		    else {
			console.log("successfully log in");
			return done(null, user);
		    }
		}
	    });
    }));
    
	

}
