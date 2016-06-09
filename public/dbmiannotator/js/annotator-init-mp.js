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
    
    // global variables for keeping status of text selection
    var isTextSelected = false;
    var cachedOATarget = "";
    var cachedOARanges = "";

    // global variables for tracking specific data item
    var currAnnotationId = "";
    var currDataNum = "";
    var totalDataNum = "";
    var currDataField = "";

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
                             
                         $('.mp-menu-btn').hover(
                             function() { 
                                 $('.mp-main-menu').show(); 
                             }
                         ); 
                         // hide menu when mouse over drugMention adder
                         $('.hl-adder-btn').mouseenter(function(){
                             $('.mp-main-menu').hide();
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

