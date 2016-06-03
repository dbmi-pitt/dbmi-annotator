if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    var annType = $('#mp-annotation-tb').attr('name');
    var sourceURL = getURLParameter("sourceURL").trim();
    var email = getURLParameter("email");

    if (annType == "DDI")
        app.include(annotator.ui.dbmimain);            
    else if (annType == "MP")
        app.include(annotator.ui.mpmain, {element: subcontent, email: email, source: sourceURL});
    else 
        alert("[ERROR] plugin settings wrong, neither DDI nor MP plugin!");

    
    app.include(annotator.storage.debug);
    app.include(annotator.identity.simple);
    app.include(annotator.authz.acl);

    app.include(annotator.storage.http, {
	    prefix: 'http://' + config.store.host + ':' + config.store.port
    });

    // var annotationCreateHelper = function () {

	//     source = getURLParameter("sourceURL").trim();
    // 	return {
    //         beforeAnnotationCreated: function (ann) {
	// 	        ann.rawurl = source;
    // 		    ann.uri = source.replace(/[\/\\\-\:\.]/g, "");		
	// 	        ann.email = email;
    //         },
    //         annotationCreated: function (ann) {
    //             if (ann.annotationType == "MP") {
    //                 $("#mp-annotation-work-on").html(ann.id);
    //                 annotationTable(ann.rawurl, ann.email);
    //                 console.log("refresh ann table");
    //             }
    //         },
    //         annotationUpdated: function(ann) {
    //             if (ann.annotationType == "MP") {
    //                 $("#mp-annotation-work-on").html(ann.id);
    //                 annotationTable(ann.rawurl, ann.email);
    //                 console.log("refresh ann table");
    //             }
    //         },
    //         annotationDeleted: function (ann) {
                
    //             setTimeout(function(){
    //                 console.log("refresh ann table");
    //                 annotationTable(source, email);
    //             },1000);
    //         }            
    // 	};
    // };
    // app.include(annotationCreateHelper);

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
                         annotationTable(sourceURL, email);
                         console.log("initial ann table");
                     }).then(function(){

                         $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });

                         // MP adder - open/close claim menu
                         // PMC page not ready - hanging... (comment line below)
                         // $(document).ready(function () {
                         console.log("add hover for mpadder menu");
                             
                         $('.mp-menu-btn').hover(function() { 
                             $('.mp-main-menu').show(); 
                         });                             

                         $('.mp-main-menu').mouseleave(function(){
                             $('.mp-main-menu').hide(); 
                         });
                         
                         $('.mp-main-menu-2').mouseenter(function(){
                             $(this).find('.mp-sub-menu-2').slideDown();
                         });
                         
                         $('.mp-main-menu-2').mouseleave(function(){
                             $(this).find('.mp-sub-menu-2').slideUp();
                         });

                         $('#relationship').change(function() {
                             showEnzyme();
                         });

                     });
}


function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

$(document).ready(function () {
    // splitter for show annotation panel
    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });
});


// var getUrlParameter = function getUrlParameter(sParam) {
//     var sPageURL = decodeURIComponent(window.location.search.substring(1)),
//         sURLVariables = sPageURL.split('&'),
//         sParameterName,
//         i;

//     for (i = 0; i < sURLVariables.length; i++) {
//         sParameterName = sURLVariables[i].split('=');

//         if (sParameterName[0] === sParam) {
//             return sParameterName[1] === undefined ? true : sParameterName[1];
//         }
//     }
// };
