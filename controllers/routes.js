config = require('./../config/config.js');
var request = require("request");
var tidy = require('htmltidy').tidy;
var pg = require('pg');

module.exports = function(app, passport) {

    // INDEX PAGE ===============================
    app.get('/dbmiannotator', function(req, res) {
	    if (req.isAuthenticated()){
            res.redirect('/dbmiannotator/main');
	    } else {
	        res.render('index.ejs', { message: req.flash('loginMessage') });
	    }
    });
    
    // LOGIN ===============================
    app.get('/dbmiannotator/login', function(req, res) {
        // render the page and pass in any flash data if it exists
        res.render('login.ejs', { message: req.flash('loginMessage') }); 
    });

    app.post('/dbmiannotator/login', passport.authenticate('local-login', {
        successRedirect : '/dbmiannotator/main', 
        failureRedirect : '/dbmiannotator/login', 
        failureFlash : true 
    }));    

    // SIGNUP ==============================
    app.get('/dbmiannotator/register', function(req, res) {
        res.render('register.ejs', { message: req.flash('signupMessage') });
    });

    app.post('/dbmiannotator/register', isRegisterFormValid, passport.authenticate('local-signup', {
	    successRedirect : '/dbmiannotator/main', 
	    failureRedirect : '/dbmiannotator/register', 
	    failureFlash : true
    })
	        );
    
    // MAIN ==============================
    app.get('/dbmiannotator/main', isLoggedIn, initPluginProfile, function(req, res) {
        if (config.profile.userProfile != null) {
            annotationType = config.profile.userProfile.type;
        } else {
            annotationType = config.profile.def;
        }

        console.log("plugin init main.ejs: " + annotationType);
        
	    // fetch all DDI annotations for current user
	    var url = "http://" + config.store.host +":" + config.store.port + "/search?email=" + req.user.email + "&annotationType=" + annotationType;

	    
	    request({url: url, json: true}, function(error,response,body){
	        if (!error && response.statusCode === 200) {
		        
		        res.render('main.ejs', {
		            user : req.user,
		            annotations : body,
		            exportMessage : req.flash('exportMessage'),
		            loadMessage : req.flash('loadMessage'),
		            host : config.annotator.host,
		        });
		        
	        } else {
		        res.render('main.ejs', {
		            user : req.user,
		            annotations : {'total':0},
		            exportMessage: req.flash('exportMessage'),
		            loadMessage: req.flash('loadMessage'),
		            host: config.annotator.host,
		        });
	        }
	    });
    });
    
    // LOGOUT ==============================
    app.get('/dbmiannotator/logout', function(req, res) {
        config.profile.pluginSetL = [];
        config.profile.userProfile = {};
        req.logout();
        res.redirect('/dbmiannotator');
    });

    // DISPLAY ==============================
    app.get('/dbmiannotator/displayWebPage', isLoggedIn, praseWebContents, function(req, res) {
	
	    var sourceUrl = req.query.sourceURL.trim();
	    var email = req.query.email;
	    var validUrl = require('valid-url');

	    if (validUrl.isUri(sourceUrl)){
           
            if (sourceUrl.match(/.pdf/g)){ // local pdf resouces
		        res.redirect("/dbmiannotator/viewer.html?file=" + sourceUrl+"&email=" + email);
            } else { // local or external html resouces

                console.log("routes - displayWebPage");
                console.log(config);

                res.render('displayWebPage.ejs', {
                    htmlsource: req.htmlsource,
                    pluginSetL: config.profile.pluginSetL,
                    userProfile: config.profile.userProfile
                });   
	        }
        }
        else {
	        req.flash('loadMessage', 'The url you just entered is not valid!');
	        res.redirect('/dbmiannotator/main');
	    }
	    
    });
    

    // PLUGIN PROFILE ==============================
    app.post('/dbmiannotator/savePluginProfile', function(req, res) {
        console.log(req.body.pluginset);
        console.log(req.user.email);

        pg.connect(config.postgres, function(err, client, done) {
            
            if(err) {
                done();
                console.log(err);
                return res.status(500).json({ success: false, data: err});
            }

            if (config.profile.userProfile == null){  // no user profile, then insert
                console.log("[ERROR] user profile not avaliable!");
	            res.redirect('/dbmiannotator/main');

            } else {   // get user profile
                resultsL = []
                var queryUserProfile = client.query('SELECT u.uid, up.set_id FROM "user" u, user_profile up where u.uid = up.uid and u.email = $1 and up.status = $2', [req.user.email, true]);    
                queryUserProfile.on('row', function(row) {
                    resultsL.push(row);
                });
                
                queryUserProfile.on('end', function() { // user profile changed, then update           
                    if (resultsL[0].set_id != req.body.pluginset){ 
                        console.log("update user plugin profile");
                        client.query('UPDATE "user_profile" SET set_id = $1, created = now() FROM (SELECT * FROM "user" u where u.email = $2) AS u, "user_profile" up WHERE up.uid = u.uid AND up.status = true', [req.body.pluginset, req.user.email]);    
                        done();
	                    res.redirect('/dbmiannotator/main');
                    }
                    else {
                        console.log("user profile not need to update");
                        done();
	                    res.redirect('/dbmiannotator/main');
                    }
                }, function(){
                    res.redirect('/dbmiannotator/main');
                });
            }
                
        });
    });
    
    
    // EXPORT TO JSON ==============================
    app.get('/dbmiannotator/exportjson', isLoggedIn, function(req, res){
	
	    var url = "http://" + config.store.host + ":" + config.store.port + "/search?email=" + req.query.email + "&annotationType=" + config.profile.def;
	    
	    request({url: url, json: true}, function(error,response,body){
	        if (!error && response.statusCode === 200) {
                
                var annsJsonRes = JSON.stringify(body.rows);
                res.attachment('annotations-'+req.query.email+'.json');
		        res.setHeader('Content-Type', 'application/json');
		        res.end(annsJsonRes);		       		        
	        } else {
		        //req.flash('exportMessage', 'exported failed, annotation fetch exception, please see logs or contact Yifan at yin2@pitt.edu!');
		        res.redirect('/dbmiannotator/main');		        
	        }	
	    });	    	    
    });        

    // EXPORT TO CSV ==============================
    app.get('/dbmiannotator/exportcsv', isLoggedIn, function(req, res){
	
	    var url = "http://" + config.store.host + ":" + config.store.port + "/search?email=" + req.query.email + "&annotationType=" + config.profile.def;
	    
	    request({url: url, json: true}, function(error,response,body){
	        if (!error && response.statusCode === 200) {
                
                var jsonObjs = body.rows;
                res.attachment('annotations-'+req.query.email+'.csv');
		        res.setHeader('Content-Type', 'text/csv');
                var csvTxt = ""; 

                for (var i = 0; i < jsonObjs.length; i++) {
                    jsonObj = jsonObjs[i];
                    claim = jsonObj.argues;
                    dataL = claim.supportsBy;                   

                    for (var j = 0; j < dataL.length; j ++) {
                        data = dataL[j];
                        method = data.supportsBy;
                        material = method.supportsBy;

                        var line = '"' + claim.label + '","' + claim.hasTarget.hasSelector.exact + '","' + material.participants.value + '","' + data.auc.value + '"';
                        csvTxt += line + "\n";
                    }
                }

		        res.attachment('annotations-'+req.query.email+'.csv');
		        res.setHeader('Content-Type', 'text/csv');
		        res.end(csvTxt);                    
		        
		        // var json2csv = require('json2csv');
		        // //json2csv({data: body.rows, fields: ['email', 'rawurl', 'annotationType', 'assertion_type', 'quote', 'relationship', 'Drug1', 'Type1', 'Role1', 'Drug2', 'Type2', 'Role2', 'enzyme', 'Modality', 'Evidence_modality','Number_participants','FormulationP','FormulationO','DoseMG_precipitant','DoseMG_object','Duration_precipitant','Duration_object','RegimentsP','RegimentsO','Aucval','AucType','AucDirection','Clval','ClType','ClDirection','cmaxval','cmaxType','cmaxDirection','cminval','cminType','cminDirection','t12','t12Type','t12Direction','Comment']}, function(err, csv) {

                // json2csv({data: jsonObjs, fields: [
                //     {label: 'email', 
                //      value: function (row) {
                //          return row.email;
                //      }, default: 'UNK'}, 
                //     {label: 'auc', 
                //      value: function(row) {
                //          return row.argues.supportsBy[0].auc.value;
                //      }, default: 'UNK'}
                // ]}, function(err, csv) {
		    
		        //     if (err) console.log(err);
		            
		        //     res.attachment('annotations-'+req.query.email+'.csv');
		        //     res.setHeader('Content-Type', 'text/csv');
		        //     res.end(csv);                    
		        //     //req.flash('exportMessage', 'successfully downloaded!');
		        //     //res.redirect('/dbmiannotator/main');		    
		        // });
		        
	        } else {
		        //req.flash('exportMessage', 'exported failed, annotation fetch exception, please see logs or contact Yifan at yin2@pitt.edu!');
		        res.redirect('/dbmiannotator/main');
		        
	        }	
	    });	    	    
    });        
};


// MIDDLE WARE FUNCTIONS ==============================

// parse web contents from url
function praseWebContents(req, res, next){
    var sourceUrl = req.query.sourceURL.trim();

    if(sourceUrl.match(/localhost.*pdf/g)){
        next();
    } else {
        
        // var options = {
        //     host: sourceUrl,
        //     method: 'POST'            
        // }
        var cheerio = require("cheerio");

        request(sourceUrl, function(err, res, body){

            labelDecode = body.replace(/&amp;/g,'&').replace(/&nbsp;/g,' ');   
            //var $ = cheerio.load(labelDecode);
            //var cntBody = $("body").html();

            //console.log(cntBody);

            // normalize html source
            tidy(labelDecode, function(err, html) {
                if (err){
                    console.log(err);
                }
                req.htmlsource = html;
                next();
            });
            
        });
    }
}


// get plugin profile
function initPluginProfile(req, res, next){
    var pluginSetL = [];
    var userProfileL = [];

    var data = {text: req.body.text, complete: false};
    
    pg.connect(config.postgres, function(err, client, done) {

        if(err) {
            done();
            console.log(err);
            return res.status(500).json({ success: false, data: err});
        }
        // get all available plugin sets 
        var queryPlugins = client.query("SELECT ps.id, ps.name, ps.type, ps.description FROM plugin_set ps WHERE ps.status = True ORDER BY ps.id ASC;");

        queryPlugins.on('row', function(row) {
            pluginSetL.push(row);
        });
        
        queryPlugins.on('end', function() {
            config.profile.pluginSetL = pluginSetL;
        });
        // get plugin set from user setting
        var queryUserProfile = client.query('SELECT u.uid, up.set_id, ps.name, ps.type FROM "user" u, "user_profile" up, "plugin_set" ps where u.uid = up.uid and up.set_id = ps.id and u.email = $1 and up.status = True', [req.user.email]);

        queryUserProfile.on('row', function(row) {
            userProfileL.push(row);
        });
        queryUserProfile.on('end', function() { 
            if (userProfileL.length > 0){
                config.profile.userProfile = userProfileL[0];
                console.log("init pluginProfile - get user profile");
                console.log(config.profile.userProfile)
            }
            next();
            client.end();
        });


    });
}


// get annotation list
// function getAnnotationList(req, res, next){
// 	// fetch annotations for current document
// 	var url = "http://" + config.store.host +":" + config.store.port + "/search?email=" + req.user.email + "&annotationType=" + config.profile.userProfile.type;
	
// 	request({url: url, json: true}, function(error,response,body){
// 	    if (!error && response.statusCode === 200) {
//             req.annotations = body;
//             next();
//         }
//     });
// }

    
// route middleware to make sure a user is logged in
function isLoggedIn(req, res, next) {

    // if user is authenticated in the session, carry on 
    if (req.isAuthenticated())
        return next();

    // if they aren't redirect them to the home page
    res.redirect('/dbmiannotator');
}

// validate inputs in register form
function isRegisterFormValid(req, res, next){

    req.assert('email', 'Email is not valid').isEmail();
    req.assert('username', 'Username must be at least 4 characters long').len(4);
    req.assert('password', 'Password must be at least 6 characters long').len(6);
    req.assert('repassword', 'Passwords do not match').equals(req.body.password);
    
    var errors = req.validationErrors();
    
    if (errors) {
	
	res.render('register', { 
	    title: 'Register Form Validation',
	    message: '',
	    errors: errors
        });
	
    } else {
	return next();
    } 

}

