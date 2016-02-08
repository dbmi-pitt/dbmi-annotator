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

    // add attribute uri for annotation as source url
    var pageUri = function () {
    	return {
            beforeAnnotationCreated: function (ann) {
		ann.uri = $('input#hdURL').val().replace(/[\/\\\-\:\.]/g, "");
            }
    	};
    };
    
    app.include(pageUri);

    app.start().then(function () 
		     {   
			 var currUser = getCookie('email');
			 if (currUser != null){
			     app.ident.identity = currUser;
			 } else{
			     app.ident.identity = 'anonymous@gmail.com';                 
			 }
		     });
    
    $('#loadButton').click(function(event) {
	event.preventDefault();

	var sourceUrlTxt = $('#sourceURL').val()
	// set source url
	$('input#hdURL').val(sourceUrlTxt)
	
	// if dailymed html label, load label in range of div content
	if(sourceUrlTxt.indexOf('.html') >= 0){
	    $("#content").load($("#sourceURL").val());
	    // after html label loaded, then load annotations
	    app.annotations.load({uri: $('input#hdURL').val().replace(/[\/\\\-\:\.]/g, "")})
	}
	
	// if source is pdf documents, jump to pdf.js viewer.html
	if(sourceUrlTxt.indexOf('.pdf') >= 0){
	    window.location.href = "http://localhost/static/js/web/viewer.html?file=" + sourceUrlTxt;
	}
    });

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

