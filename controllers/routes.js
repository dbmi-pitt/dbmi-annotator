module.exports = function(app, passport) {

    // index page
    app.get('/', function(req, res) {
        res.render('index.ejs', { message: req.flash('loginMessage') }); 
    });

    
    // LOGIN ===============================
    app.get('/login', function(req, res) {
        // render the page and pass in any flash data if it exists
        res.render('login.ejs', { message: req.flash('loginMessage') }); 
    });

    app.post('/login', passport.authenticate('local-login', {
        successRedirect : '/main', 
        failureRedirect : '/login', 
        failureFlash : true 
    }));    


    // SIGNUP ==============================
    app.get('/register', function(req, res) {
        res.render('register.ejs', { message: req.flash('signupMessage') });
    });

    app.post('/register', passport.authenticate('local-signup', {
        successRedirect : '/main', // redirect to the secure profile section
        failureRedirect : '/register', // redirect back to the signup page if there is an error
        failureFlash : true // allow flash messages
    }));

    // MAIN ==============================
    app.get('/main', isLoggedIn, function(req, res) {
        res.render('main.ejs', {
            user : req.user 
        });
    });
    

    // LOGOUT ==============================
    app.get('/logout', function(req, res) {
        req.logout();
        res.redirect('/');
    });
};

// route middleware to make sure a user is logged in
function isLoggedIn(req, res, next) {

    // if user is authenticated in the session, carry on 
    if (req.isAuthenticated())
        return next();

    // if they aren't redirect them to the home page
    res.redirect('/');
}


// app.get('/extractImages', function(req, res) {
    
//     var pdfdoc = req.param('pdfdoc');
    
//     console.log("[INFO] server received request with doc: " + pdfdoc)

//     // run pdfimages
//     var sys = require('sys')
//     var exec = require('child_process').exec;

//     var imgDirName = "images-" + pdfdoc;
//     exec("mkdir public/pdf-images/" + imgDirName);
//     exec("pdfimages -j public/DDI-pdfs/" +pdfdoc + " public/pdf-images/"+ imgDirName +"/");
//     console.log("[INFO] extraction complete!");

//     var img = fs.readFileSync('public/pdf-images/' + imgDirName + "/-000.jpg");
//     res.writeHead(200, {'Content-Type': 'image/jpg' });
//     res.end(img, 'binary');
    
//     res.send('pdfdoc: ' + pdfdoc);
    
// });
