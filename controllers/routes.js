config = require('./../config/config.js');
var request = require("request");
var tidy = require('htmltidy').tidy;

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
    app.get('/dbmiannotator/main', isLoggedIn, function(req, res) {
        
	    // fetch all DDI annotations for current user
	    var url = "http://" + config.store.host +":" + config.store.port + "/search?email=" + req.user.email + "&annotationType=DDI";
	    
	    request({url: url, json: true}, function(error,response,body){
	        if (!error && response.statusCode === 200) {
		        
		        res.render('main.ejs', {
		            user : req.user,
		            annotations : body,
		            exportMessage: req.flash('exportMessage'),
		            loadMessage: req.flash('loadMessage'),
		            host: config.annotator.host
		        });
		        
	        } else {
		        res.render('main.ejs', {
		            user : req.user,
		            annotations : {'total':0},
		            exportMessage: req.flash('exportMessage'),
		            loadMessage: req.flash('loadMessage'),
		            host: config.annotator.host
		        });
	        }
	    });
    });
    
    // LOGOUT ==============================
    app.get('/dbmiannotator/logout', function(req, res) {
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
                res.render('displayWebPage.ejs', {
                    htmlsource: req.htmlsource
                });   
	        }
        }
        else {
	        req.flash('loadMessage', 'The url you just entered is not valid!');
	        res.redirect('/dbmiannotator/main');
	    }
	    
    });
    

    // EXPORT ==============================
    app.get('/dbmiannotator/exportcsv', isLoggedIn, function(req, res){
	
	var url = "http://" + config.store.host + ":" + config.store.port + "/search?email=" + req.query.email + "&annotationType=DDI";
	    
	request({url: url, json: true}, function(error,response,body){
	    if (!error && response.statusCode === 200) {
		
		var json2csv = require('json2csv');
		json2csv({data: body.rows, fields: ['email', 'rawurl', 'annotationType', 'assertion_type', 'quote', 'relationship', 'Drug1', 'Type1', 'Role1', 'Drug2', 'Type2', 'Role2', 'enzyme', 'Modality', 'Evidence_modality','Number_participants','FormulationP','FormulationO','DoseMG_precipitant','DoseMG_object','Duration_precipitant','Duration_object','RegimentsP','RegimentsO','Aucval','AucType','AucDirection','Clval','ClType','ClDirection','cmaxval','cmaxType','cmaxDirection','cminval','cminType','cminDirection','t12','t12Type','t12Direction','Comment']}, function(err, csv) {
		    
		    if (err) console.log(err);
		    
		    res.attachment('annotations-'+req.query.email+'.csv');
		    res.setHeader('Content-Type', 'text/csv');
		    res.end(csv);

		    //req.flash('exportMessage', 'successfully downloaded!');
		    //res.redirect('/dbmiannotator/main');		    
		});
		
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

    request(sourceUrl, function(err, res, body){

        labelDecode = body.replace(/&amp;/g,'&').replace(/&nbsp;/g,' ');        

        // normalize html source
        tidy(labelDecode, function(err, html) {
            if (err){
                console.log(err);
            }
            req.htmlsource = html;
            next();
            //console.log(html);
        });
        
    });
    }
}


// get annotation list
function getAnnotationList(req, res, next){
	// fetch annotations for current document
	var url = "http://" + config.store.host +":" + config.store.port + "/search?email=" + req.user.email + "&annotationType=DDI&";
	
	request({url: url, json: true}, function(error,response,body){
	    if (!error && response.statusCode === 200) {
            req.annotations = body;
            next();
        }
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

