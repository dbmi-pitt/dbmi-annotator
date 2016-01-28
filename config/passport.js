var pg = require('pg');
var LocalStrategy = require('passport-local').Strategy;
//var User = require('./../models/user').User;
var bcrypt   = require('bcrypt-nodejs');
var uuid = require('node-uuid');


// expose this function to our app using module.exports
module.exports = function(passport, User) {

    // passport session setup ==================================================

    passport.serializeUser(function(user, done) {
        done(null, user.id);
    });

    passport.deserializeUser(function(id, done) {
	User.findById(id).then(function(user){
	    done(null,user);
	});
    });


    // LOCAL SIGNUP ============================================================

    passport.use('local-signup', new LocalStrategy({
        usernameField : 'email',
        passwordField : 'password',
        passReqToCallback : true // allows us to pass back the entire request to the callback
    },
    function(req, email, password, done) {

        // User.findOne wont fire unless data is sent back
        process.nextTick(function() {
	    console.log("[DEBUG] register - with email: " + email + " | password: " + password);
            User.findOne({where:{'email': email}})
		.then(function(user){
		    
		    if (user) {
			console.log("[INFO] register - user exists");
			return done(null, false, req.flash('signupMessage', 'That email is already taken.'));
		    } else {
			console.log("[INFO] register - create new user");
			
			User.create({
			    uid : uuid.v1(),
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
