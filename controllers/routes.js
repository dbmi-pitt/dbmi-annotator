/* Copyright 2016-2017 University of Pittsburgh

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http:www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License. */


config = require('./../config/config.js');
utilcsv = require('./../utils/objtocsv.js');
var request = require("request");
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
        // disable register for public release
        // res.render('index.ejs', { message: req.flash('signupMessage') });
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
        
	    // fetch all DDI annotations for current user
	    var url = config.protocal + "://" + config.apache2.host +":" + config.apache2.port + "/annotatorstore/search?email=" + req.user.email + "&annotationType=" + annotationType;

        //loading csv file
        var content = loadArticleList();

		res.render('main.ejs', {
		    user : req.user,
		    annotations : [],
            article: content,
		    exportMessage : req.flash('exportMessage'),
		    loadMessage : req.flash('loadMessage'),
		    host : config.annotator.host
		});

	    // request({url: url, json: true}, function(error,response,body){
	    //     if (!error && response.statusCode === 200) {
		        
		//         res.render('main.ejs', {
		//             user : req.user,
		//             annotations : body,
		//             exportMessage : req.flash('exportMessage'),
		//             loadMessage : req.flash('loadMessage'),
		//             host : config.annotator.host,
		//         });
		        
	    //     } else {
		//         res.render('main.ejs', {
		//             user : req.user,
		//             annotations : {'total':0},
		//             exportMessage: req.flash('exportMessage'),
		//             loadMessage: req.flash('loadMessage'),
		//             host: config.annotator.host,
		//         });
	    //     }
	    // });
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
		    
		    // if (sourceUrl.match(/\.pdf/g)){ // local pdf resouces
		    //     res.redirect("/dbmiannotator/viewer.html?file=" + sourceUrl+"&email=" + email); 
		    // }
		    
		    if (sourceUrl.match(/localhost.*html/g)) { 		    
                res.render('displayWebPage.ejs', {
			        htmlsource: req.htmlsource,
			        pluginSetL: config.profile.pluginSetL,
			        userProfile: config.profile.userProfile
                });   
	        }
		    else {
		        req.flash('loadMessage', 'The url you just entered is not valid!');
		        res.redirect('/dbmiannotator/main');
		    }
		    
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
	
	    var url = config.protocal + "://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search?email=" + req.query.email + "&annotationType=" + config.profile.def;
	    
	    request({url: url, json: true}, function(error,response,body){
	        if (!error && response.statusCode === 200) {
                
                var annsJsonRes = JSON.stringify(body.rows);
                res.attachment('annotations-'+req.query.email+'.json');
		        res.setHeader('Content-Type', 'application/json');
		        res.end(annsJsonRes);		       		        
	        } else {
		        res.redirect('/dbmiannotator/main');		        
	        }	
	    });	    	    
    });        

    // EXPORT TO CSV ==============================
    app.get('/dbmiannotator/exportcsv', isLoggedIn, function(req, res){
	
	    var url = config.protocal + "://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search?email=" + req.query.email + "&annotationType=" + config.profile.def;
        //var url = config.protocal + "://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search?annotationType=" + config.profile.def;
	    
	    request({url: url, json: true, followAllRedirects: true, "rejectUnauthorized": false}, function(error,response,body){            
	        if (!error && (response.statusCode === 200 || response.statusCode ===302)) {
                var jsonObjs = body.rows;

                res.attachment('annotations-'+req.query.email+'.csv');
		        res.setHeader('Content-Type', 'text/csv');
                resultsL = [];

                for (var i = 0; i < jsonObjs.length; i++) {
                    jsonObj = jsonObjs[i];
                    claim = jsonObj.argues;
                    dataL = claim.supportsBy;            

                    // initiate dict for one row in csv with claim information
                    var rowDict={"document":jsonObj.rawurl, "useremail":jsonObj.email, "claimlabel":claim.label, "claimtext":claim.hasTarget.hasSelector.exact, "method":claim.method, "relationship":claim.qualifiedBy.relationship, "drug1":claim.qualifiedBy.drug1, "drug2":claim.qualifiedBy.drug2, "precipitant":(claim.qualifiedBy.precipitant||''), "enzyme":(claim.qualifiedBy.enzyme||''), "rejected": "", "evRelationship":"", "participants":"", "participantstext":"", "drug1dose":"", "drug1formulation":"", "drug1duration":"", "drug1regimens":"", "drug1dosetext":"", "drug2dose":"", "phenotypetype": "", "phenotypevalue": "", "phenotypemetabolizer": "", "phenotypepopulation": "", "drug2formulation":"", "drug2duration":"", "drug2regimens":"", "drug2dosetext":"", "aucvalue":"", "auctype":"", "aucdirection":"", "auctext":"", "cmaxvalue":"", "cmaxtype":"", "cmaxdirection":"", "cmaxtext":"", "clearancevalue":"", "clearancetype":"", "clearancedirection":"", "clearancetext":"", "halflifevalue":"", "halflifetype":"", "halflifedirection":"", "halflifetext":"", "dipsquestion":"", "reviewer":"", "reviewerdate":"", "reviewertotal":"", "reviewerlackinfo":"", "grouprandomization":"", "parallelgroupdesign":"", "id": jsonObj.id};

                    if (claim.rejected != null)
                        rowDict["rejected"] = (claim.rejected || "");

                    // fill data and material to dict
                    if (dataL.length > 0) { // if data is available

                        for (var j = 0; j < dataL.length; j++) { // loop all data items
                            copyDict = JSON.parse(JSON.stringify(rowDict));
                            var data = dataL[j];
                            var method = data.supportsBy;
                            var material = method.supportsBy;

                            copyDict["evRelationship"] = (data.evRelationship || "");

                            if (material.participants != null) {
                                copyDict["participants"] = (material.participants.value || "")
                                copyDict["participantstext"] = (getSpanFromField(material.participants) || "")
                            }

                            dataFieldsL = ["auc","cmax","clearance","halflife"];
                            for (p = 0; p < dataFieldsL.length; p++) {
                                field = dataFieldsL[p];
                                if (data[field] != null) {
                                    copyDict[field + 'value'] = (data[field].value || "")
                                    copyDict[field + 'type'] = (data[field].type || "")
                                    copyDict[field + 'direction'] = (data[field].direction || "")
                                    copyDict[field + 'text'] = (getSpanFromField(data[field]) || "")
                                }
                            }

                            if (data.dips != null) {
                                dipsQsStr = "";
                                qsL=["q1","q2","q3","q4","q5","q6","q7","q8","q9","q10"];
                                for (q = 0; q < qsL.length; q++) {
                                    if (q == qsL.length - 1)
                                        dipsQsStr += data.dips[qsL[q]];
                                    else
                                        dipsQsStr += data.dips[qsL[q]] + "|";
                                }
                                copyDict["dipsquestion"] = dipsQsStr;
                            }

                            if (data.reviewer != null) {
                                copyDict["reviewer"] = data.reviewer.reviewer || "";
                                copyDict["reviewerdate"] = data.reviewer.date || "";
                                copyDict["reviewertotal"] = data.reviewer.total || "";
                                copyDict["reviewerlackinfo"] = data.reviewer.lackinfo || "";
                            }

                            if (data.grouprandom != null)
                                copyDict["grouprandomization"] = (data.grouprandom || "");                            
                            
                            if (data.parallelgroup != null)
                                copyDict["parallelgroupdesign"] = (data.parallelgroup || "");

                            if (material.drug1Dose != null) {
                                copyDict["drug1dose"] = (material.drug1Dose.value || "")
                                copyDict["drug1formulation"] = (material.drug1Dose.formulation || "")
                                copyDict["drug1duration"] = (material.drug1Dose.duration || "")
                                copyDict["drug1regimens"] = (material.drug1Dose.regimens || "")
                                copyDict["drug1dosetext"] = (getSpanFromField(material.drug1Dose) || "")
                            } 
                            if (material.drug2Dose != null) {
                                copyDict["drug2dose"] = (material.drug2Dose.value || "")
                                copyDict["drug2formulation"] = (material.drug2Dose.formulation || "")
                                copyDict["drug2duration"] = (material.drug2Dose.duration || "")
                                copyDict["drug2regimens"] = (material.drug2Dose.regimens || "")
                                copyDict["drug2dosetext"] = (getSpanFromField(material.drug2Dose) || "")
                            }                                 
                            if (material.phenotype != null) {
                                copyDict["phenotypetype"] = material.phenotype.type || "";
                                copyDict["phenotypevalue"] = material.phenotype.typeVal || "";
                                copyDict["phenotypemetabolizer"] = material.phenotype.metabolizer || "";
                                copyDict["phenotypepopulation"] = material.phenotype.population || "";
                            }                      
                            resultsL.push(copyDict);
                        }
                    } else {
                        resultsL.push(rowDict);
                    }
                }

                console.log(resultsL.length);
                csvTxt = utilcsv.toCsv(resultsL, '"', '\t');

		        res.attachment('annotations-'+req.query.email+'.csv');
		        res.setHeader('Content-Type', 'text/csv');
		        res.end(csvTxt);                                              
		        
	        } else {
		        //req.flash('exportMessage', 'exported failed, annotation fetch exception, please see logs or contact Yifan at yin2@pitt.edu!');
                console.log(error);
		        res.redirect('/dbmiannotator/main');		        
	        }	
	    });	    	    
    });        
};

// UTIL FUNCTIONS ==============================
function getSpanFromField(field) {
    if (field.hasTarget !=null) {
        if (field.hasTarget.hasSelector !=null) 
            return field.hasTarget.hasSelector.exact;
    } else {
        return "";
    }
}

// MIDDLE WARE FUNCTIONS ==============================

// parse web contents from url
function praseWebContents(req, res, next){
    var sourceUrl = req.query.sourceURL.trim();

    console.log("[DEBUG] parseWebContents");

    if(sourceUrl.match(/localhost.*html/g)){

        if (process.env.APACHE2_HOST != null) // use apache2 in docker network
            sourceUrl = sourceUrl.replace("localhost", process.env.APACHE2_HOST);

        request(sourceUrl, function(err, res, body){

            if (err){
                console.log(err);
                console.log(res);
                return;
            }             

            // skip tidy beacuse changing of char encoding
            labelDecode = body.replace(/&amp;/g,'&').replace(/&nbsp;/g,' ');   
            req.htmlsource = labelDecode;
            next();                        
        });

    } else {
        next();        
    }
}

// get plugin profile
function initPluginProfile(req, res, next){

    console.log("routes.js - initPluginProfile");

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

function loadArticleList(){
    console.log("Load article list.");
    var fs = require('fs');
    var result = [];
    var articleList = config.article;
    /*fs.readFile('./article-list/dailymed-list.csv', 'utf8', function(err, contents) {
        console.log(contents);
    });*/

    //synchronized read csv
    for (var j = 0; j < articleList.length; j++) {
        var contents = fs.readFileSync('./article-list/' + articleList[j] + '-list.csv', 'utf8');

        var list = [];
        var temp = contents.split('\n');
        for (var i = 0; i < temp.length; i++) {
            var arr = temp[i].split(',');
            list.push({'article':arr[0], 'link':arr[1]});
        }
        result[articleList[j]] = list;
    }
    return result;
}

