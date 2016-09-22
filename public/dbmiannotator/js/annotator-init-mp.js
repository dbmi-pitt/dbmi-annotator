if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    // var annType = $('#mp-annotation-tb').attr('name');
    var annType = "MP";
    var sourceURL = getURLParameter("sourceURL").trim();
    var email = getURLParameter("email");
    
    // global variables for keeping status of text selection
    var isTextSelected = false;
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
    app.start().then(
        function () {
			app.ident.identity = email;
			$(".btn-success").css("display","block");            
            
            initMpAdder(); // initiate mp adder
            
            initLiseners(); // initiate listeners on data unchange button, claim relationship change, etc
            
            initSplitter(); // initiate screen splitter
            
            importAnnotationDialog(sourceURL, email); // annotation import dialog    
        });
}


// initiate splitter
function initSplitter() {

    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });

    var resizeTimer;           
    $(window).resize(function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(resetSplitter, 300);
    });    
}

// reset splitter when window size changed
function resetSplitter() {    
    console.log("resize window - resetSplitter called");
    $('#splitter').jqxSplitter({
        showSplitBar: false, 
        width: $(window).width(), 
        height: $(window).height(), 
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 250}]
    });
}


// initiate Mp adder
function initMpAdder() {
    // MP adder - open/close claim menu           
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
}


// add action listeners 
function initLiseners() {

    $('#relationship').change(function() {
        showEnzyme();
    });
            
    // change event for auc, cmax, clearance, halflife unchanged checkbox
    unchangedCheckBoxDialog("auc");                        
    unchangedCheckBoxDialog("cmax");
    unchangedCheckBoxDialog("clearance");
    unchangedCheckBoxDialog("halflife");
    
    // jquery for checking form editing status
    $(":input").change(function(){
        unsaved = true;
    });

    //highlight drugs in quote dynamicly  
    //moved from mp-annotation-editor                      
    $("#Drug1").change(function (){selectDrug();});
    $("#Drug2").change(function (){selectDrug();});
}



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


// get parameter from url
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}



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

// pop up dialog for importable existing annotation sets  
function importAnnotationDialog(sourceURL, email) {

    var uri = sourceURL.replace(/[\/\\\-\:\.]/g, "");
    var importDialog = document.getElementById('dialog-annotation-import');

    importDialog.style.display = "block"; 

    var okBtn = document.getElementById("ann-import-confirm-btn");
    var cancelBtn = document.getElementById("ann-import-cancel-btn");

    cancelBtn.onclick = function() {
        importDialog.style.display = "none"; 
        annotationTable(sourceURL, email);
    }

    okBtn.onclick = function() {
        console.log("import clicked");
		app.annotations.load({uri: uri, email: email});                             
        importDialog.style.display = "none"; 
        annotationTable(sourceURL, email);
    }	
}



$(document)
    .ajaxStart(function () {
        $('#wait').show();
    })
    .ajaxStop(function () {
        $('#wait').hide();
    });
