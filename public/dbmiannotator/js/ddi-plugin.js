
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
	    prefix: 'http://' + config.store.host + ':' + config.store.port
    });

    var sourceURL = getURLParameter("sourceURL").trim();
    var email = getURLParameter("email");

    var annotationCreateHelper = function () {

	    source = getURLParameter("sourceURL").trim();
    	return {
            beforeAnnotationCreated: function (ann) {
		        ann.rawurl = source;
    		    ann.uri = source.replace(/[\/\\\-\:\.]/g, "");		
		        ann.email = email;
            },
            annotationCreated: function (ann) {
                refreshAnnotationList(ann.rawurl, ann.email);
            },
            annotationUpdated: function(ann) {
                refreshAnnotationList(ann.rawurl, ann.email);
            },
            annotationDeleted: function (ann) {
                setTimeout(function(){
                    refreshAnnotationList(source, email);
                },800);
            }
            
    	};
    };
    app.include(annotationCreateHelper);

    // load annotation after page contents loaded
    app.start().then(function () 
		             {
			             app.ident.identity = email;
			             $(".btn-success").css("display","block");
		             }).then(function(){
			             setTimeout(function(){
			                 app.annotations.load({uri: sourceURL.replace(/[\/\\\-\:\.]/g, ""), email: email});
			             }, 1000);
		             }).then(function(){
                         refreshAnnotationList(sourceURL, email);
                     });
}


function refreshAnnotationList(sourceURL, email){

    console.log("[INFO] refreshAnnotationList called");

    $.ajax({url: 'http://' + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: 'DDI', 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){

                //console.log(response);
                if (response.total > 0){
                    
                    listTable = "<table>";
                    listTable += "<tr><td>Subject</td><td>Predicate</td><td>Object</td><td>Assertion Type</td><td>Date</td><td>Quote</td><td></td></tr>";
                    for (i = 0; i < response.total; i++){
                        row = response.rows[i];
                        listTable += "<tr><td>" + row.Drug1 + "</td><td>Interact with</td><td>" + row.Drug2 + "</td><td>" + row.assertion_type + "</td><td>" + row.created + "</td><td>text</td><td><a href='#" + row.id + "' >annotation</a></td></tr>"
                    }
                    listTable += "</table>";
                    $("#annotation-list").html(listTable);  
                } else {
                    $("#annotation-list").html("No DDI annotations been made!");  
                }
                
            }
     
           });

}



function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}


