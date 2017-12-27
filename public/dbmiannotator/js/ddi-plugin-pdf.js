if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();
    var annotationType = $("#annotationtype-div").text();

    var sourceURL = getURLParameter("file").trim();
    var email = getURLParameter("email");

    // global variables for keeping status of text selection
    var isTextSelected = false;
    var multiSelected = false;

    var cachedOATarget = "";
    var cachedOARanges = "";

    // global variables for tracking specific data item
    var currAnnotationId = "";
    var currAnnotation = undefined;
    var currDataNum = "";
    var totalDataNum = "";
    var currFormType = "";

    // track the form editing status from user
    var unsaved = false;

    if (annotationType == "DDI")
        app.include(annotator.ui.ddimain);            
    else if (annotationType == "MP")
        app.include(annotator.ui.mpmain, {element: '', email: email, source: sourceURL});
    else 
        alert("[ERROR] plugin settings wrong, neither DDI nor MP plugin!");
    

    app.include(annotator.storage.debug);
    app.include(annotator.identity.simple);
    app.include(annotator.authz.acl);

    app.include(annotator.storage.http, {
	prefix: 'http://' + config.store.host + ':' + config.store.port
    });

    
    
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
    // load annotation after page contents loaded
    app.start().then(function () 
                     {
                         app.ident.identity = email;
                         $(".btn-success").css("display","block");
                     }).then(function(){
                         /*setTimeout(function(){
                             app.annotations.load({uri: sourceURL.replace(/[\/\\\-\:\.]/g, ""), email: email});                             
                         }, 3000);*/
                     }).then(function(){
                         annotationTable(sourceURL, email);
                     }).then(function(){

                         $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });
                         $('.mp-main-menu').css({left: '40px', top: '15px'});
                         // MP adder - open/close claim menu
                         // PMC page not ready - hanging... (comment line below)
                         // $(document).ready(function () {
                             
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

                         // change event for auc, cmax, clearance, halflife unchanged checkbox
                         unchangedCheckBoxDialog("auc");                        
                         unchangedCheckBoxDialog("cmax");
                         unchangedCheckBoxDialog("clearance");
                         unchangedCheckBoxDialog("halflife");

                         // jquery for checking form editing status
                         /*$(":input").change(function(){
                             console.log("[INFO] making changes - unsaved set to true");
                             unsaved = true;
                         });*/

                     });
    $( window ).load(function() {
        console.log( "window loaded" );
    });
    
}

//highlight drugs in quote dynamicly  
//moved from mp-annotation-editor                      
$("#Drug1").change(function (){selectDrug();});
$("#Drug2").change(function (){selectDrug();});

function selectDrug() {
    var drug1 = $('#Drug1 option:selected').text();
    var drug2 = $('#Drug2 option:selected').text();
    var drug1ID = $('#Drug1 option:selected').val();
    var drug2ID = $('#Drug2 option:selected').val();

    var quotestring = $("#quote").html();
    quotestring = quotestring.split("class=\"highlightdrug\"").join("class=\"annotator-hl\"");
    quotestring = quotestring.split("class=\"highlightdrug\"").join("class=\"annotator-hl\"");
    quotestring = quotestring.split("class=\"annotator-hl\" id=\""+drug1ID+"\"").join("class=\"highlightdrug\" id=\""+drug1ID+"\"");
    quotestring = quotestring.split("class=\"annotator-hl\" id=\""+drug2ID+"\"").join("class=\"highlightdrug\" id=\""+drug2ID+"\"");
    quotestring = quotestring.split("id=\""+drug1ID+"\" class=\"annotator-hl\"").join("class=\"highlightdrug\" id=\""+drug1ID+"\"");
    quotestring = quotestring.split("id=\""+drug2ID+"\" class=\"annotator-hl\"").join("class=\"highlightdrug\" id=\""+drug2ID+"\"");
    $("#quote").html(quotestring);
}

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

$(document).ready(function () {
    // splitter for show annotation panel
    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });
});

// dialog for confirm truncation when user check unchanged checkbox  
// fields allowed: auc, cmax, clearance, halflife
function unchangedCheckBoxDialog(field) {
    if (field !== "auc" && field!== "cmax" && field!== "clearance" && field !== "halflife") {
        return;
    }

    $('#' + field + '-unchanged-checkbox').change(function() {
        
        if ($(this).is(":checked")) {
            
            if ($('#'+field).val() != null && $('#'+field).val().trim() != "") {
                // show unchanged warn dialog
                var unchangedDialog = document.getElementById('unchanged-warn-dialog');
                unchangedDialog.style.display = "block";
                // When the user clicks anywhere outside of the dialog, close it
                window.onclick = function(event) {
                    if (event.target == unchangedDialog) {
                        unchangedDialog.style.display = "none";
                    }
                }
                
                var okBtn = document.getElementById("unchanged-dialog-ok-btn");
                var cancelBtn = document.getElementById("unchanged-dialog-cancel-btn");

                okBtn.onclick = function() {
                    unchangedDialog.style.display = "none";
                    $('#'+field).val('');
                    $('#'+field+'Type')[0].selectedIndex = -1;
                    $('#'+field+'Direction')[0].selectedIndex = -1;
                    
                    $('#'+field).attr('disabled', true);
                    $('#'+field+'Type').attr('disabled', true);
                    $('#'+field+'Direction').attr('disabled', true);   
                }
                cancelBtn.onclick = function() {
                    unchangedDialog.style.display = "none"; 
                $('#'+field+'-unchanged-checkbox').attr('checked',false);
                }
            } else {                
                $('#'+field+'Type')[0].selectedIndex = -1;
                $('#'+field+'Direction')[0].selectedIndex = -1;
                
                $('#'+field).attr('disabled', true);
                $('#'+field+'Type').attr('disabled', true);
                $('#'+field+'Direction').attr('disabled', true);                   
            }
            
        } else {
            // TODO: grey out fields
            $('#'+field).attr('disabled', false);
            $('#'+field+'Type').attr('disabled', false);
            $('#'+field+'Direction').attr('disabled', false);   
        }
    });
}

