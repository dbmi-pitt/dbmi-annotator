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
	prefix: 'http://127.0.0.1:5000'
    });
    
    var sourceURL = getURLParameter("sourceURL");
    var username = getURLParameter("username");
    
    // add attribute uri for annotation as source url
    var pageUri = function () {

	source = getURLParameter("sourceURL");
    	return {
            beforeAnnotationCreated: function (ann) {
    		ann.uri = source.replace(/[\/\\\-\:\.]/g, "");
            }
    	};
    };
    app.include(pageUri);

    $(".btn-success").css("display","block");
    $("#subcontent").load(sourceURL);
    
    app.start().then(function () 
		     {
			 app.ident.identity = username;
			 
		     }).then(function(){
			 
			 app.annotations.load({uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")});
			 alert("annotations for user: " + username + " are loaded");
		     });

}


function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}


function getCookie(cname) {

    //alert('get cookie by name: ' + cname)
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
} 

