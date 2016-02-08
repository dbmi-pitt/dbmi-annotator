if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    app.include(annotator.ui.dbmimain);
    app.include(annotator.storage.debug);
    app.include(annotator.identity.simple);
    app.include(annotator.authz.acl);

    app.include(annotator.storage.http, {
	prefix: 'http://130.49.206.139:5000'
    });

    var sourceURL = getURLParameter("file").trim();
    var email = getURLParameter("email");
    
    var pageUri = function () {

	source = getURLParameter("file").trim();
    	return {
            beforeAnnotationCreated: function (ann) {
		ann.rawurl = source;
    		ann.uri = source.replace(/[\/\\\-\:\.]/g, "");
		ann.email = email;
            }
    	};
    };
    app.include(pageUri);
    app.start().then(function () 
		     {
			 app.ident.identity = email;
			 //setTimeout(function () { alert(document.readyState); }, 2000);
			 setTimeout(function ()
				    { app.annotations.load(
					{uri: sourceURL.replace(/[\/\\\-\:\.]/g, ""), email: email});
				    }, 2100);
		     });
    
}

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}
