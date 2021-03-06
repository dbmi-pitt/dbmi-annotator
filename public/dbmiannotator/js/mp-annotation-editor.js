// MP CLAIM ================================================================================
// open claim editor
function claimEditorLoad() {
    currFormType = "claim";
    $("#mp-claim-form").show();
    $('#quote').show();
    $("#claim-label-data-editor").hide();
    $(".annotator-save").hide();
    $("#mp-data-nav").hide();
    $("#mp-dips-nav").hide();
    $("#mp-experiment-nav").hide();
    $("#mp-data-form-evRelationship").hide();
    $("#mp-data-form-participants").hide();
    $("#mp-data-form-dose1").hide();
    $("#mp-data-form-dose2").hide();
    $("#mp-data-form-phenotype").hide();
    $("#mp-data-form-auc").hide();
    $("#mp-data-form-cmax").hide();
    $("#mp-data-form-clearance").hide();
    $("#mp-data-form-halflife").hide();
    $("#mp-data-form-studytype").hide();
    $("#mp-data-form-reviewer").hide();
    $("#mp-data-form-q1").hide();
    $("#mp-data-form-q2").hide();
    $("#mp-data-form-q3").hide();
    $("#mp-data-form-q4").hide();
    $("#mp-data-form-q5").hide();
    $("#mp-data-form-q6").hide();
    $("#mp-data-form-q7").hide();
    $("#mp-data-form-q8").hide();
    $("#mp-data-form-q9").hide();
    $("#mp-data-form-q10").hide();
    $("#mp-data-form-cellSystem").hide();
    $("#mp-data-form-rateWith").hide();
    $("#mp-data-form-rateWithout").hide();
    $("#mp-data-form-cl").hide();
    $("#mp-data-form-vmax").hide();
    $("#mp-data-form-km").hide();
    $("#mp-data-form-ki").hide();
    $("#mp-data-form-inhibition").hide();
    $("#mp-data-form-kinact").hide();
    $("#mp-data-form-ic50").hide();
}

function reviewerChange() {
    if ($("input[name=dips-reviewer]:checked").val() == 'External') {
        $("#author-lackscore").prop('checked', false);
        $("#author-total").val('NA');
    }
}

// edit claim
function editClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();

    scrollToAnnotation(annotationId, "claim", 0);
    showEditor();
    claimEditorLoad();
        
    $.ajax({url: config.protocal + "://" + config.apache2.host + "/annotatorstore/annotations/" + annotationId,
            data: {},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(annotation){
                // enable delete button
                $("#annotator-delete").show();
                
                // call AnnotatorJs editor for update    
                app.annotations.update(annotation);   
            }
           });        
}

// when method is phenotype and relationship is inhibits or substrate of
function changeCausedbyMethod() {
    $("#relationship option[value = 'interact with']").removeAttr('disabled');
    $("#relationship option[value = 'interact with']").show();
    $("#relationship option[value = 'inhibits']").removeAttr('disabled');
    $("#relationship option[value = 'inhibits']").show();
    $("#relationship option[value = 'substrate of']").removeAttr('disabled');
    $("#relationship option[value = 'substrate of']").show();
    $('#object-metabolite').parent().hide();
    $('#object-metabolite-label').parent().hide();
    var selectR = $("#relationship option:selected").text();
    if (selectR == "has metabolite" || selectR == "controls formation of" || selectR == "inhibition constant") {
        $("#relationship option:selected").prop("selected", false);
        $("#relationship option[value='interact with']").prop("selected", true);
    }

    var methodValue = $("#method option:selected").text();
    //statement
    if (methodValue == "Statement") {
        $('#negationdiv').parent().show();
        $('#negation-label').parent().show();
    } else {
        $('#negationdiv').parent().hide();
        $('#negation-label').parent().hide();
    }
    //phenotype - no interact with
    if (methodValue == "Phenotype clinical study") {
        $("#relationship option[value = 'interact with']").attr('disabled', 'disabled');
        $("#relationship option[value = 'interact with']").hide();
        if ($("#relationship option:selected").text() == "interact with") {
            $("#relationship option:selected").prop("selected", false);
            $("#relationship option[value='inhibits']").prop("selected", true);
        }
    }
    //case report - no substrate of or inhibits
    if (methodValue == "Case Report") {
        $("#relationship option[value = 'inhibits']").attr('disabled', 'disabled');
        $("#relationship option[value = 'inhibits']").hide();
        $("#relationship option[value = 'substrate of']").attr('disabled', 'disabled');
        $("#relationship option[value = 'substrate of']").hide();
        if ($("#relationship option:selected").text() == "inhibits" || $("#relationship option:selected").text() == "substrate of") {
            $("#relationship option:selected").prop("selected", false);
            $("#relationship option[value='interact with']").prop("selected", true);
        }
    }
    //experiment - no interact with, add "has metabolite", "controls formation of", "inhibition constant"
    if (methodValue == "Experiment") {
        $("#relationship option").removeAttr('disabled');
        $("#relationship option").show();
        $("#relationship option[value = 'interact with']").attr('disabled', 'disabled');
        $("#relationship option[value = 'interact with']").hide();
        var selectedR = $("#relationship option:selected").text();
        if (selectedR == "interact with") {
            $("#relationship option:selected").prop("selected", false);
            $("#relationship option[value='inhibits']").prop("selected", true);
        }
        $('#object-metabolite').parent().show();
        $('#object-metabolite-label').parent().show();
    } else {
        $("#relationship option[value = 'has metabolite']").attr('disabled', 'disabled');
        $("#relationship option[value = 'has metabolite']").hide();
        $("#relationship option[value = 'controls formation of']").attr('disabled', 'disabled');
        $("#relationship option[value = 'controls formation of']").hide();
        $("#relationship option[value = 'inhibition constant']").attr('disabled', 'disabled');
        $("#relationship option[value = 'inhibition constant']").hide();
    }

    //phenotype & statement
    if ((methodValue == "Phenotype clinical study" || methodValue == "Statement") && ($("#relationship option:selected").text() == "inhibits"||$("#relationship option:selected").text()=="substrate of")) {
        $("#Drug1-label").html("Drug: ");
        $("#Drug2-label").parent().hide();
        $("#Drug2").parent().hide();
        $("#Drug2")[0].selectedIndex = 0;
        $("#enzymesection1").show();
        $("#enzyme").show();

        $('input[name=precipitant]').prop('checked', false);
        $('input[type=radio][name=precipitant]').parent().hide();
        $('.precipitantLabel').parent().hide();
    } else {
        $("#Drug1-label").html("Drug1: ");
        $("#Drug2-label").parent().show();
        $("#Drug2").parent().show();
        //$('input[name=precipitant]').prop('checked', false);
        $('input[type=radio][name=precipitant]').parent().show();
        $('.precipitantLabel').parent().show();
        //$("#Drug2")[0].selectedIndex = 0;
        console.log($("#Drug2 option:selected").text());
    }
    showEnzyme();
    selectDrug();
}

// when reviewer is author
function showLackQuestionInfo() {
    var reviewerValue = $("input[name=dips-reviewer]:checked").val();
    console.log(reviewerValue);
    if (reviewerValue == "Author") {
        $("#author-lackscore").show();
        $("#author-lackscore-label").show();
    } else {
        $("#author-lackscore").hide();
        $("#author-lackscore-label").hide();
        $("#author-total").hide();
        $("#author-total-label").hide();
    }
}

// when question score is lack, input total score directly
function showTotalScore() {
    var lackScore = $("#author-lackscore").is(':checked');
    if (lackScore) {
        $('.dipsQuestion').prop('disabled', true);
        $("#author-total").show();
        $("#author-total-label").show();
    } else {
        $('.dipsQuestion').prop('disabled', false);
        $("#author-total").hide();
        $("#author-total").val('NA');
        $("#author-total-label").hide();
    }
}

// when type is Genotype
function showPhenotypeType() {
    console.log($("input[name=phenotypeGenre]:checked").val());
    console.log($("input[name=phenotypeMetabolizer]:checked").val());
    if ($("input:radio[name=phenotypeGenre]:checked").val() == "Genotype") {
        $('#geneFamily').show();
        $('#geneFamily-label').show();
        $('#markerDrug').hide();
        $('#markerDrug-label').hide();
    } else {
        $('#geneFamily').hide();
        $('#geneFamily-label').hide();
        $('#markerDrug').show();
        $('#markerDrug-label').show();
    }
}

// when relationship is inhibits or substrate of, show field enzyme
function showEnzyme() {

    if($("#relationship option:selected").text() == "inhibits"||$("#relationship option:selected").text()=="substrate of") {
        if ($("#method option:selected").text() == "Phenotype clinical study" || $("#method option:selected").text() == "Statement") {
            //hide drug2
            $("#Drug1-label").html("Drug: ");
            $("#Drug2-label").parent().hide();
            $("#Drug2").parent().hide();
            //hide metabolite
            $("#drug2enantiomerLabel").parent().hide();
            $("#drug2enantiomer").parent().hide();
            $("#drug2metaboliteLabel").parent().hide();
            $("#drug2metabolite").parent().hide();
            //hide precipitant
            $('input[name=precipitant]').prop('checked', false);
            $('input[type=radio][name=precipitant]').parent().hide();
            $('.precipitantLabel').parent().hide();
        } else {
            //show drug2
            $("#Drug1-label").html("Drug1: ");
            $("#Drug2-label").parent().show();
            $("#Drug2").parent().show();
            //show metabolite
            $("#drug2enantiomerLabel").parent().show();
            $("#drug2enantiomer").parent().show();
            $("#drug2metaboliteLabel").parent().show();
            $("#drug2metabolite").parent().show();
            //show precipitant
            $('input[type=radio][name=precipitant]').parent().show();
            $('.precipitantLabel').parent().show();
        }
        //show enzyme
        $("#enzyme")[0].selectedIndex = 0;
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        //show drug2
        $("#Drug1-label").html("Drug1: ");
        $("#Drug2-label").parent().show();
        $("#Drug2").parent().show();
        //show metabolite
        $("#drug2enantiomerLabel").parent().show();
        $("#drug2enantiomer").parent().show();
        $("#drug2metaboliteLabel").parent().show();
        $("#drug2metabolite").parent().show();
        //show enzyme
        $("#enzymesection1").hide();
        $("#enzyme").hide();
        //show precipitant
        $('input[type=radio][name=precipitant]').parent().show();
        $('.precipitantLabel').parent().show();
    }
}


// modify annotaiton id when user pick claim on mpadder's menu
// update annotation table if necessary
function claimSelectedInMenu(annotationId) {
    currAnnotationId = annotationId;
    annTableId = $('#mp-editor-claim-list option:selected').val();

    if (annotationId != annTableId){
        $("#mp-editor-claim-list option[value='" + annotationId + "']").attr("selected", "true");
        changeClaimInAnnoTable();
    }
}

// MP DATA & MATERIAL ========================================================================
// called when click annotation table cell when value of cell is empty
// (1) if no text selection avaliable, then pop up warning message then return 
// to mp annotation table
// (2) otherwise, load annotation to editor, then shown specific data form
function addDataCellByEditor(field, dataNum, isNewData) {

    
    $("#button#drug1-dose-switch-btn").focus();

    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("addDataCellByEditor - id: " + annotationId + " | data: " + dataNum + " | field: " + field);

    $("#claim-label-data-editor").show();
    //fields whitch don't need text selected
    var selectedTextNotNeed = ["evRelationship", "studytype", "reviewer", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"];

    // return if no text selection 
    if (!isTextSelected && !selectedTextNotNeed.includes(field)) {
        warnSelectTextSpan(field);
    } else {
        $("#mp-data-nav").hide();
        $("#mp-dips-nav").hide();
        $("#mp-experiment-nav").hide();
        // hide data fields navigation if editing evidence relationship 
        if (field == "evRelationship" || field =="studytype") {
            $("#mp-data-nav").hide();
            $(".annotator-save").hide();
        } else if (field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") { // when field is checkbox
            $("#mp-data-nav").show();
            $("#mp-dips-nav").hide();
            $(".annotator-save").show(); 
        } else if (currAnnotation.argues.method == "Case Report"){ // when field is text input
            $("#mp-data-nav").hide();
            $("#mp-dips-nav").show();
            $(".annotator-save").show(); 
            var flag = currAnnotation.argues.supportsBy[dataNum];
            if (flag == undefined || flag.reviewer.lackInfo) {
                $('.dipsQuestion').prop('disabled', true);
            } else {
                $('.dipsQuestion').prop('disabled', false);
            }
        } else if (currAnnotation.argues.method == "Experiment"){
            $("#mp-experiment-nav").show();
            //$("#annotator-save").show();
        } else {
            $("#mp-data-nav").show();
            $("#mp-dips-nav").hide();
            $(".annotator-save").show(); 
        }
        if (currAnnotation.argues.method == "Phenotype clinical study") {
            $('#nav-dose2-btn').hide();
            $('#nav-phenotype-btn').show();
        } else if (currAnnotation.argues.method != "Experiment"){
            $('#nav-dose2-btn').show();
            $('#nav-phenotype-btn').hide();
        }

        // cached editing data cell
        currAnnotationId = annotationId;
        currDataNum = dataNum;
        currFormType = field;

        showEditor();
        if (cachedOATarget.hasSelector != null)
            $("#" + field + "quote").html(cachedOATarget.hasSelector.exact);
        $("#annotator-delete").hide();
        
        // updating current MP annotation
        if (annotationId != null)
            currAnnotationId = annotationId;     

        preDataForm(field);

        $.ajax({url: config.protocal + "://" + config.apache2.host + "/annotatorstore/annotations/" + annotationId,
                data: {},
                method: 'GET',
                error : function(jqXHR, exception){
                    console.log(exception);
                },
                success : function(annotation){
                    // add data if not avaliable  
                    if (annotation.argues.supportsBy.length == 0 || isNewData){ 

                        var data = {type : "mp:data", evRelationship: "", auc : {}, cmax : {}, clearance : {}, halflife : {}, reviewer: {}, dips: {}, cellSystem: {}, metaboliteRateWith: {}, metaboliteRateWithout: {}, measurement: {}, supportsBy : {type : "mp:method", supportsBy : {type : "mp:material", participants : {}, drug1Dose : {}, drug2Dose : {}, phenotype: {}}}, grouprandom: "", parallelgroup: ""};
                        annotation.argues.supportsBy.push(data); 
                    } 
                    
                    // call AnnotatorJs editor for update    
                    app.annotations.update(annotation);
  
                }                 
               });
        }
}
              
        
// called when click annotation table cell when value of cell is not null
// (1) scroll to the annotation upon document
// (2) load annotation to editor, then shown specific data form
function editDataCellByEditor(field, dataNum) {

    showEditor();
    $("#claim-label-data-editor").show();
    $('#quote').hide();
    $("#mp-data-nav").hide();
    $("#mp-dips-nav").hide();
    $("#mp-experiment-nav").hide();
    // hide data fields navigation if editing evidence relationship 
    if (field == "evRelationship" || field =="studytype") {
        $("#mp-data-nav").hide();
        $(".annotator-save").hide();
    } else if (field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") { // when field is checkbox
        $("#mp-data-nav").show();
        $("#mp-dips-nav").hide();
        $(".annotator-save").show(); 
    } else if (currAnnotation.argues.method == "Case Report"){ // when field is text input
        $("#mp-data-nav").hide();
        $("#mp-dips-nav").show();
        $(".annotator-save").show(); 
        // freeze question nav
        if (currAnnotation.argues.supportsBy[dataNum].reviewer.lackInfo) {
            $('.dipsQuestion').prop('disabled', true);
        } else {
            $('.dipsQuestion').prop('disabled', false);
        }
    } else if (currAnnotation.argues.method == "Experiment"){
        $("#mp-experiment-nav").show();
        //$("#annotator-save").show();
    } else {
        $("#mp-data-nav").show();
        $("#mp-dips-nav").hide();
        $(".annotator-save").show(); 
    }

    if (currAnnotation.argues.method == "Phenotype clinical study") {
        $('#nav-dose2-btn').hide();
        $('#nav-phenotype-btn').show();
    } else {
        $('#nav-dose2-btn').show();
        $('#nav-phenotype-btn').hide();
    }


    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("editDataCellByEditor - id: " + annotationId + " | data: " + dataNum + " | field: " + field);
    
    // cached editing data cell
    currAnnotationId = annotationId;
    currDataNum = dataNum;
    currFormType = field;

    // scroll to the position of annotation
    scrollToAnnotation(annotationId, field, dataNum);
        
    $.ajax({url: config.protocal + "://" + config.apache2.host + "/annotatorstore/annotations/" + annotationId,
            data: {},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(annotation){
                
                // updating current MP annotation
                if (annotationId != null)
                    currAnnotationId = annotationId;
                
                //switchDataForm(field, true);
                preDataForm(field, true);

                // show delete button
                data = annotation.argues.supportsBy[dataNum];
                material = data.supportsBy.supportsBy;
                
                if ((field == "participants" && material.participants.value != null) || (field == "dose1" && material.drug1Dose.value != null) || (field == "dose2" && material.drug2Dose.value != null) || ((field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") && (data[field].value != null)) || 
                    field == "rateWithout" || field == "rateWith" || field == "cellSystem" || field == "cl" || field == "vmax" || field == "km" || field == "ki" || field == "inhibition" || field == "kinact" || field == "ic50")
                    $("#annotator-delete").show();
                
                // call AnnotatorJs editor for update    
                app.annotations.update(annotation);   
            }
           });               
}

// warning dialog for opening data editor
function preDataForm(targetField, isNotNeedValid) {
    $("#mp-claim-form").hide();
    quoteF = $('#'+targetField+'quote').html();         
    // unsaved warning box  
    if (!warnUnsavedDialog())
        return;

    if (!isTextSelected && (targetField != "evRelationship" || targetField != "studytype") && quoteF == "" && !isNotNeedValid) {
        warnSelectTextSpan(targetField);
        return;
    } 
    
    if (targetField == null) 
        targetField = "participants";

    currFormType = targetField;

    focusOnDataField(targetField);
}

// switch data from nav button
function switchDataForm(targetField, isNotNeedValid) {

    $("#mp-claim-form").hide();
    quoteF = $('#'+targetField+'quote').html();         
    // unsaved warning box  
    if (!warnUnsavedDialog())
        return;

    // pop up warn for selecting span when switch to new targetField dring editing mode
    if (!isTextSelected && (targetField != "evRelationship" || targetField != "studytype") && quoteF == "" && !isNotNeedValid) {
        warnSelectTextSpan(targetField);
        return;
    } 
    

    if (targetField == null) 
        targetField = "participants";

    currFormType = targetField;

    try {
        
        //redraw data currhighlight & add/edit data to currAnnotation
        app.annotations.update(currAnnotation);
        // scroll to the position of annotation
        scrollToAnnotation(currAnnotation.id, currFormType, currDataNum);
        
        switchDataFormHelper(targetField);

    } catch (err) {
        console.log(err);
    }
}

// when switch data field, show or hide delete button, nav buttons and data forms 
function switchDataFormHelper(targetField) {

    // field actual div id mapping
    fieldM = {"reviewer":"reviewer", "evRelationship":"evRelationship", "participants":"participants", "dose1":"drug1Dose", "dose2":"drug2Dose", "phenotype":"phenotype", "auc":"auc", "cmax":"cmax", "clearance":"clearance", "halflife":"halflife", "studytype":"studytype",
    "q1":"q1", "q2":"q2", "q3":"q3", "q4":"q4", "q5":"q5", "q6":"q6", "q7":"q7", "q8":"q8", "q9":"q9", "q10":"q10"};

    var showDeleteBtn = false;

    for (var field in fieldM) {       
        var dataid = "mp-data-form-"+field;
        if (field === targetField) {
            $("#"+dataid).show();  // show specific data form 
            // inspect that is target form has value filled 

            if (field == "evRelationship" || field =="studytype") { // when field is radio button
                fieldVal = $("input[name="+field+"]:checked").val();
            } else if (field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") { // when field is checkbox
                $("#mp-data-nav").show();
                $("#mp-dips-nav").hide();
                if ($('#' + field + '-unchanged-checkbox').is(':checked')) 
                    showDeleteBtn = true;                    
                fieldVal = $("#" + fieldM[field]).val();
            } else if (currAnnotation.argues.method == "Case Report"){ // when field is text input
                $("#mp-data-nav").hide();
                $("#mp-dips-nav").show();
                fieldVal = $("#" + fieldM[field]).val();
            } else {
                $("#mp-data-nav").show();
                $("#mp-dips-nav").hide();
                fieldVal = $("#" + fieldM[field]).val();
            }

            if (fieldVal !=null && fieldVal != "")
                $("#annotator-delete").show();
            else if (showDeleteBtn)
                $("#annotator-delete").show();
            else 
                $("#annotator-delete").hide();
            focusOnDataField(targetField);
        }  else {
            cleanFocusOnDataField(field);
            $("#"+dataid).hide();
        }                           
    }
}


// scroll current focus on window to specific highlight piece
function scrollToAnnotation(annotationId, fieldName, dataNum) {
    var divId = annotationId + "-" + fieldName + "-" + dataNum;
    if (document.getElementById(divId))
        document.getElementById(divId).scrollIntoView(true);
}

// unselect study type questions 
function clearStudyTypeQuestions() {
    $('input[name=grouprandom]').prop('checked', false);
    $('input[name=parallelgroup]').prop('checked', false);
}


function focusOnDataField (fieldName) {
    $("button#nav-"+fieldName+"-btn").css("border","3px solid #336699");
}


function cleanFocusOnDataField(fieldName) {
    $("button#nav-"+fieldName+"-btn").css("border","");
}
