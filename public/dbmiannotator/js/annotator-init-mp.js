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
    var currEmail = getURLParameter("email");
    
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

    // form editing status from user
    var unsaved = false;

    // users annotation been imported
    var userEmails = new Set();

    if (annType == "DDI")
        app.include(annotator.ui.dbmimain);            
    else if (annType == "MP")
        app.include(annotator.ui.mpmain, {element: subcontent, email: currEmail, source: sourceURL});
    else 
        alert("[ERROR] plugin settings wrong, neither DDI nor MP plugin!");
    
    app.include(annotator.storage.debug);
    app.include(annotator.identity.simple);
    app.include(annotator.authz.acl);

    // call apache2 server, instead of annotator store at port 5000
    app.include(annotator.storage.http, {
	prefix: config.protocal + '://' + config.apache2.host + ':' + config.apache2.port + '/annotatorstore' 
    });

    // load annotation after page contents loaded
    app.start().then(
        function () {
            console.log(config);

			app.ident.identity = currEmail;
			$(".btn-success").css("display","block");            
            
            initMpAdder(); // initiate mp adder
            
            initLiseners(); // initiate listeners on data unchange button, claim relationship change, etc
            
            initSplitter(); // initiate screen splitter
            
            importAnnotationDialog(sourceURL, currEmail); // annotation import dialog    
        });
    $body = $("body");
    $(document).on({
        ajaxStart: function() { $body.addClass("loading"); },
        ajaxStop: function() { $body.removeClass("loading"); }    
    });

    $( function() {
        $( document ).tooltip();
    });

    $( function() {
        $( "#datepicker" ).datepicker();
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

    $('#method').change(function() {
        changeCausedbyMethod();
        showEnzyme();
    });

    $('input[name=phenotypeGenre]').change(function() {
        showPhenotypeType();
    });

    $('input[name=dips-reviewer]').change(function() {
        showLackQuestionInfo();
    });

    $('#author-lackscore').change(function() {
        showTotalScore();
    });

    $('#dips-reviewer').change(function() {
        reviewerChange();
    });

    $('#editDrug1').click(function() {
        $('#Drug1').hide();
        $('#Drug1-input').show();
        $('#editDrug1').hide();
        $('#commitDrug1').show();
    });

    $('#editDrug2').click(function() {
        $('#Drug2').hide();
        $('#Drug2-input').show();
        $('#editDrug2').hide();
        $('#commitDrug2').show();
    });

    $('#edit-clUnit').click(editUnit);
    $('#edit-vmaxUnit').click(editUnit);
    $('#edit-inhibitionUnit').click(editUnit);
    $('#edit-kmUnit').click(editUnit);
    $('#edit-kiUnit').click(editUnit);
    $('#edit-kinactUnit').click(editUnit);
    $('#edit-ic50Unit').click(editUnit);

    function editUnit() {
        var field = currFormType + "Unit";
        $('#' + field).hide();
        $('#' + field + '-input').show();
        $('#edit-' + field).hide();
        $('#commit-' + field).show();
    }

    $('#commit-clUnit').click(checkEditedUnit);
    $('#commit-vmaxUnit').click(checkEditedUnit);
    $('#commit-inhibitionUnit').click(checkEditedUnit);
    $('#commit-kmUnit').click(checkEditedUnit);
    $('#commit-kiUnit').click(checkEditedUnit);
    $('#commit-kinactUnit').click(checkEditedUnit);
    $('#commit-ic50Unit').click(checkEditedUnit);

    function checkEditedUnit() {
        var field = currFormType + "Unit";
        $('#' + field).show();
        $('#' + field + '-input').hide();
        $('#edit-' + field).show();
        $('#commit-' + field).hide();
        //add input drug1 to dropdown list
        var input_object = $('#'+field+'-input').val();
        if (input_object != "") { //sanity check
            //sanity check - input duplicates
            var tempval = input_object;
            //add option
            if ($('#'+field+' option[value = \"'+tempval+'\"]').length == 0) {
                $('#'+field).append($('<option>', {
                    value: tempval,
                    text: tempval
                }));
            }
            //select option
            $('#'+field+' > option').each(function () {
                console.log(this.text);
                if (this.text === tempval) {
                    $(this).prop('selected', true);
                } else {
                    $(this).prop('selected', false);
                }
            });
        }
    }

    $('#edit-object-metabolite').click(function() {
        $('#object-metabolite').hide();
        $('#object-metabolite-input').show();
        $('#edit-object-metabolite').hide();
        $('#commit-object-metabolite').show();
    });

    $('#commit-object-metabolite').click(function() {
        $('#object-metabolite').show();
        $('#object-metabolite-input').hide();
        $('#edit-object-metabolite').show();
        $('#commit-object-metabolite').hide();
        //add input drug1 to dropdown list
        var input_object = $('#object-metabolite-input').val();
        if (input_object != "") { //sanity check
            //sanity check - input duplicates
            var tempval = input_object;
            //add option
            if ($('#object-metabolite option[value = \"'+tempval+'\"]').length == 0) {
                $('#object-metabolite').append($('<option>', {
                    value: tempval,
                    text: tempval
                }));
            }
            //select option
            $('#object-metabolite > option').each(function () {
                console.log(this.text);
                if (this.text === tempval) {
                    $(this).prop('selected', true);
                } else {
                    $(this).prop('selected', false);
                }
            });
        }
    });

    $('#commitDrug1').click(function() {
        $('#Drug1').show();
        $('#Drug1-input').hide();
        $('#editDrug1').show();
        $('#commitDrug1').hide();
        //add input drug1 to dropdown list
        var input_drug1 = $('#Drug1-input').val();
        if (input_drug1 != "") { //sanity check
            //sanity check - input duplicates
            var tempval = input_drug1 + "_0";
            if ($('#Drug1 option[value = \"'+tempval+'\"]').length == 0) {
                $('#Drug1').append($('<option>', {
                    value: input_drug1 + "_0",
                    text: input_drug1
                }));
            }

            $('#Drug1 > option').each(function () {
                console.log(this.text);
                if (this.text === input_drug1) {
                    $(this).prop('selected', true);
                } else {
                    $(this).prop('selected', false);
                }
            });
            selectDrug();
        }
    });

    $('#commitDrug2').click(function() {
        $('#Drug2').show();
        $('#Drug2-input').hide();
        $('#editDrug2').show();
        $('#commitDrug2').hide();
        //add input drug2 to dropdown list
        var input_drug2 = $('#Drug2-input').val();
        if (input_drug2 != "") { //sanity check - input is null
            //sanity check - input duplicates
            var tempval = input_drug2 + "_0";
            if ($('#Drug2 option[value = \"'+tempval+'\"]').length == 0) {
                $('#Drug2').append($('<option>', {
                    value: input_drug2 + "_0",
                    text: input_drug2
                }));
            }
            $('#Drug2 > option').each(function () {
                if (this.text === input_drug2) {
                    $(this).prop('selected', true);
                } else {
                    $(this).prop('selected', false);
                }
            });
            selectDrug();
        }
    });
    
    rejectEvidenceCheckBox("rejected-evidence");
            
    // change event for auc, cmax, clearance, halflife unchanged checkbox
    unchangedCheckBoxDialog("auc");                        
    unchangedCheckBoxDialog("cmax");
    unchangedCheckBoxDialog("clearance");
    unchangedCheckBoxDialog("halflife");
    unchangedCheckBoxDialog("cl");
    unchangedCheckBoxDialog("vmax");
    unchangedCheckBoxDialog("km");
    unchangedCheckBoxDialog("ki");
    unchangedCheckBoxDialog("inhibition");
    unchangedCheckBoxDialog("kinact");
    unchangedCheckBoxDialog("ic50");
    
    // jquery for checking form editing status
    $(":input").change(function(){
        unsaved = true;
    });

    //highlight drugs in quote dynamicly  
    //moved from mp-annotation-editor                      
    $("#Drug1").change(function (){selectDrug();});
    $("#Drug2").change(function (){selectDrug();});
}
    //helper function
    function findIndex(string, old, no) {
        var i = 0;
        var pos = -1;
        while(i <= no && (pos = string.indexOf(old, pos + 1)) != -1) {
            i++;
        }
        return pos;
    }
    function replaceIndex(string, at, old, repl) {
        return string.replace(new RegExp(old, 'g'), function(match, i) {
            if( i === at ) return repl;
                return match;
        });
    }


function selectDrug() {

    var drug1 = $('#Drug1 option:selected').text();
    var drug2 = $('#Drug2 option:selected').text();
    //console.log("select new drug:" + drug1 + "," + drug2);
    var drug1ID = $('#Drug1 option:selected').val();
    var drug1Index = parseInt(drug1ID.split("_")[1]);
    var drug2ID;
    var drug2Index;
    
    if ($("#Drug2")[0].selectedIndex != -1) {
        drug2ID = $('#Drug2 option:selected').val();
        drug2Index = parseInt(drug2ID.split("_")[1]);
    } else {
        drug2 = "";
    }

    //deselect drug
    var quotecontent = $("#quotearea").html();
    var element = $(quotecontent);//convert string to JQuery element
    element.find(".highlightdrug").each(function(index) {
        var text = $(this).text();//get span content
        $(this).replaceWith(text);//replace all span with just content
    });
    quotecontent = "<p>" + element.html() + "</p>";//get back new string

    //select drug
    drug1Index = findIndex(quotecontent, drug1, drug1Index);
    drug2Index = drug2 == "" ? drug1Index : findIndex(quotecontent, drug2, drug2Index);
    var drug1End = drug1Index + drug1.length;
    var drug2End = drug2Index + drug2.length;
    if (drug1Index != -1 && drug2Index != -1) {
        if ((drug1Index <= drug2Index && drug1End >= drug2Index) || (drug2Index <= drug1Index && drug2End >= drug1Index)) {
            var end = Math.max(drug1End, drug2End);
            var start = Math.min(drug1Index, drug2Index);
            quotecontent = quotecontent.substring(0, start) + "<span class=\"highlightdrug\">" + quotecontent.substring(start, end) + "</span>" + quotecontent.substring(end, quotecontent.length);
        } else {
            if (drug1Index <= drug2Index) {
                quotecontent = quotecontent.substring(0, drug1Index) + "<span class=\"highlightdrug\">" + drug1 + "</span>" +
                                quotecontent.substring(drug1End, drug2Index) + "<span class=\"highlightdrug\">" + drug2 + "</span>" +
                                quotecontent.substring(drug2End, quotecontent.length);
            } else {
                quotecontent = quotecontent.substring(0, drug2Index) + "<span class=\"highlightdrug\">" + drug2 + "</span>" +
                                quotecontent.substring(drug2End, drug1Index) + "<span class=\"highlightdrug\">" + drug1 + "</span>" +
                                quotecontent.substring(drug1End, quotecontent.length);
            }
        }
    } else if (drug1Index != -1) {
        quotecontent = quotecontent.substring(0, drug1Index) + "<span class=\"highlightdrug\">" + drug1 + "</span>" +
                                quotecontent.substring(drug1End, quotecontent.length);
    } else if (drug2Index != -1) {
        quotecontent = quotecontent.substring(0, drug2Index) + "<span class=\"highlightdrug\">" + drug2 + "</span>" +
                                quotecontent.substring(drug2End, quotecontent.length);
    }
    $("#quotearea").html(quotecontent);
}


// get parameter from url
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

function rejectEvidenceCheckBox(field) {
    $('#' + field).change(function() {
        if ($('#' + field).is(':checked')) {
            $('#reject-reason').show();
            $('#reject-reason-label').show();
            $('#reject-reason-comment').show();
            $('#reject-reason-comment-label').show();
        } else {
            $('#reject-reason').hide();
            $('#reject-reason-comment').hide();
            $('#reject-reason-label').hide();
            $('#reject-reason-comment-label').hide();
        }
    });
}


// dialog for confirm truncation when user check unchanged checkbox  
// fields allowed: auc, cmax, clearance, halflife
function unchangedCheckBoxDialog(field) {
    //auc, cmax, clearance, halflife
    if (field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") {

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

    //experiment measurement: cl, vmax, km, ki, inhibition, kinact, ic50
    if (field == "cl" || field == "vmax" || field == "km" || field == "ki" || field == "inhibition" || field == "kinact" || field == "ic50") {

        $('#' + field + '-unchanged-checkbox').change(function() {
            
            if ($(this).is(":checked")) {
                if ($('#'+field+'Value').val() != null && $('#'+field+'Value').val().trim() != "") {
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
                        $('#'+field+'Value').val('');
                        $('#'+field+'Unit')[0].selectedIndex = -1;
                        
                        $('#' + field + 'Unit').attr('disabled', true);
                        $('#' + field + 'Value').attr('disabled', true);  
                    }
                    cancelBtn.onclick = function() {
                        unchangedDialog.style.display = "none"; 
                        $('#'+field+'-unchanged-checkbox').attr('checked',false);
                    }
                } else {                
                    $('#'+field+'Unit')[0].selectedIndex = -1;
                    
                    $('#' + field + 'Unit').attr('disabled', true);
                    $('#' + field + 'Value').attr('disabled', true);                 
                }            
            } else {
                // TODO: grey out fields
                $('#' + field + 'Unit').attr('disabled', false);
                $('#' + field +'Value').attr('disabled', false);
            }
        });
    }
}

// pop up dialog for importable existing annotation sets  
function importAnnotationDialog(sourceURL, email) {

    var uri = sourceURL.replace(/[\/\\\-\:\.]/g, "");
    var emailS = new Set();
    var allMPAnnsD = {}; // dict for all MP annotations {email: annotations}
    var allDrugAnnsD = {}; // dict for all drug mention annotation {email: annotations}
    var urlReq = config.protocal + "://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search";

    console.log(urlReq);

    $.ajax({url: urlReq,
            data: {
                //annotationType: "MP", 
                uri: uri},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
		        console.log(jqXHR);
            },
            success : function(response){

                for (var i=0; i < response.total; i++) {
                    var ann = response.rows[i];
                    var email = ann.email;
                    emailS.add(email);

                    if (ann.annotationType == "MP") {
                        if (allMPAnnsD[email] == null) 
                            allMPAnnsD[email] = [ann];
                        else 
                            allMPAnnsD[email].push(ann);                   
                    } else if (ann.annotationType == "DrugMention") {
                        if (allDrugAnnsD[email] == null) 
                            allDrugAnnsD[email] = [ann];
                        else 
                            allDrugAnnsD[email].push(ann);                   
                    }                    
                }
                //console.log(allMPAnnsD);
                //console.log(allDrugAnnsD);
                var htmlCnt = "";
                emailS.forEach(function (email){
                    var numsOfAnns = 0
                    if (allMPAnnsD[email] != null)
                        numsOfAnns += allMPAnnsD[email].length;
                    if (allDrugAnnsD[email] != null)
                        numsOfAnns += allDrugAnnsD[email].length;    

                    htmlCnt += "<b>"+email+": </b>" + numsOfAnns;

                    if (email != currEmail){ // other user's annotation set - optional      
                        htmlCnt += "&nbsp;&nbsp;<input type='checkbox' name='anns-load-by-email' value='"+email+"'><br>";
                    } else { // load current user's annotation set by default
                        htmlCnt += "&nbsp;&nbsp;<input type='checkbox' name='current-user-email' value='"+email+"' disabled='disabled' checked><br>";                        
                    }
                    
                });                                
                $('#import-annotation-selection').html(htmlCnt);                
            }
           });

    userEmails.add(currEmail); // add current user as default
    importAnnotationActions(userEmails, allMPAnnsD, uri, email) // import, cancel, close buttons
}

// add actions for button in import panel
// actions: import selected sets, cancel import, close window
function importAnnotationActions(userEmails, allMPAnnsD, uri, email) {
    var importDialog = document.getElementById('dialog-annotation-import');
    importDialog.style.display = "block"; 

    var selectedMPAnnsL = []; // selected annotations
    var okBtn = document.getElementById("ann-import-confirm-btn");
    var cancelBtn = document.getElementById("ann-import-cancel-btn");
    var closeBtn = document.getElementById("annotation-import-dialog-close");

    okBtn.onclick = function() {

        // load all selected users
        $("input:checkbox[name=anns-load-by-email]:checked").each(function(){
            var email = $(this).val();
            userEmails.add(email); // add user emails to set as global variable     
        });
        
        userEmails.forEach(function(email) { // draw all annotaitons by email
		    app.annotations.load({uri: uri, email: email});

            // console.log("[DEBUG] anns by email: " + email);
            // console.log(allMPAnnsD[email]);
            if (allMPAnnsD[email] != null)
                selectedMPAnnsL = selectedMPAnnsL.concat(allMPAnnsD[email]);
        });

        initAnnTable(selectedMPAnnsL); // update annotation table
        importDialog.style.display = "none"; // hide panel        
    }	

    cancelBtn.onclick = function() { // only load current user's annotation
        
        selectedMPAnnsL = allMPAnnsD[currEmail];        
        userEmails.forEach(function(email) { // draw all annotaitons by email
		    app.annotations.load({uri: uri, email: email});
        });
        initAnnTable(selectedMPAnnsL); // update annotation table
        importDialog.style.display = "none"; 
    }

    closeBtn.onclick = function() {
        selectedMPAnnsL = allMPAnnsD[currEmail];        
        userEmails.forEach(function(email) { // draw all annotaitons by email
		    app.annotations.load({uri: uri, email: email});
        });
        initAnnTable(selectedMPAnnsL); // update annotation table
        importDialog.style.display = "none"; 
    }
}



$(document).ajaxStart(function () {
    $('#wait').show();
}).ajaxStop(function () {
    $('#wait').hide();
});
