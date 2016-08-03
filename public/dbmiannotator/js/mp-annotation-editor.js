// MP CLAIM ================================================================================
// open claim editor
function claimEditorLoad() {
    currFormType = "claim";
    $("#mp-claim-form").show();
    $('#quote').show();
    $("#claim-label-data-editor").hide();
    $(".annotator-save").hide();
    $("#mp-data-nav").hide();
    $("#mp-data-form-evRelationship").hide();
    $("#mp-data-form-participants").hide();
    $("#mp-data-form-dose1").hide();
    $("#mp-data-form-dose2").hide();
    $("#mp-data-form-auc").hide();
    $("#mp-data-form-cmax").hide();
    $("#mp-data-form-clearance").hide();
    $("#mp-data-form-halflife").hide();
    $("#mp-data-form-question").hide();
}

// scroll to the claim text span
function viewClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();
    scrollToAnnotation(annotationId, "claim", 0);
}

// edit claim
function editClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();

    scrollToAnnotation(annotationId, "claim", 0);
    showEditor();
    claimEditorLoad();
        
    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
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


$("#Drug1").change(function (){selectDrug();});
$("#Drug2").change(function (){selectDrug();});

function selectDrug() {
    var drug1 = $("#Drug1").val();
    var drug2 = $("#Drug2").val();
    var quotestring = $("#quote").html();
    quotestring = quotestring.replace(drug2, "<span class='selecteddrug'>"+drug2+"</span>");
    quotestring = quotestring.replace(drug1, "<span class='selecteddrug'>"+drug1+"</span>");
    $("#quote").html(quotestring);
}

$("#Drug1").mousedown(function (){deselectDrug();});
$("#Drug2").mousedown(function (){deselectDrug();});

function deselectDrug() {
    var drug1 = $("#Drug1").val();
    var drug2 = $("#Drug2").val();
    var quotestring = $("#quote").html();
    quotestring = quotestring.replace("<span class='selecteddrug'>"+drug2+"</span>", drug2);
    quotestring = quotestring.replace("<span class='selecteddrug'>"+drug1+"</span>", drug1);
    $("#quote").html(quotestring);
}


// when relationship is inhibits or substrate of, show field enzyme
function showEnzyme() {

    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzyme")[0].selectedIndex = 0;
        $("#enzymesection1").show();
        $("#enzyme").show();

        $('input[name=precipitant]').prop('checked', false);
        $('input[type=radio][name=precipitant]').hide();
        $('.precipitantLabel').hide();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
        $('input[type=radio][name=precipitant]').show();
        $('.precipitantLabel').show();
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

    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("addDataCellByEditor - id: " + annotationId + " | data: " + dataNum + " | field: " + field);

    $("#claim-label-data-editor").show();

    // return if no text selection 
    if (!isTextSelected && field != "evRelationship" && field != "question") {
        warnSelectTextSpan(field);
    } else {
        // hide data fields navigation if editing evidence relationship 
        if (field == "evRelationship" || field == "question") {
            $("#mp-data-nav").hide();
            $(".annotator-save").hide();
        } else {
            $(".annotator-save").show();            
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

        //switchDataForm(field);        
        preDataForm(field);

        $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
                data: {},
                method: 'GET',
                error : function(jqXHR, exception){
                    console.log(exception);
                },
                success : function(annotation){
                    // add data if not avaliable  
                    if (annotation.argues.supportsBy.length == 0 || isNewData){ 

                        var data = {type : "mp:data", evRelationship: "", auc : {}, cmax : {}, clearance : {}, halflife : {}, supportsBy : {type : "mp:method", supportsBy : {type : "mp:material", participants : {}, drug1Dose : {}, drug2Dose : {}}}, grouprandom: "", parallelgroup: ""};
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
    
    // hide data fields navigation if editing evidence relationship 
    if (field == "evRelationship" || field == "question") {
        $("#mp-data-nav").hide();
        $(".annotator-save").hide();
    } else {
        $(".annotator-save").show();
    }

    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("editDataCellByEditor - id: " + annotationId + " | data: " + dataNum + " | field: " + field);
    
    // cached editing data cell
    currAnnotationId = annotationId;
    currDataNum = dataNum;
    currFormType = field;

    // scroll to the position of annotation
    scrollToAnnotation(annotationId, field, dataNum);
        
    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
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
                if ((field == "participants" && material.participants.value != null) || (field == "dose1" && material.drug1Dose.value != null) || (field == "dose2" && material.drug2Dose.value != null) || ((field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") && (data[field].value != null)))
                    $("#annotator-delete").show();
                
                // call AnnotatorJs editor for update    
                app.annotations.update(annotation);   
            }
           });               
}


function preDataForm(targetField, isNotNeedValid) {
    quoteF = $('#'+targetField+'quote').html();         
    // unsaved warning box  
    if (!warnUnsavedDialog())
        return;

    // pop up warn for selecting span when switch to new targetField dring editing mode
    if (!isTextSelected && (targetField != "evRelationship" || targetField != "question") && quoteF == "" && !isNotNeedValid) {
        warnSelectTextSpan(targetField);
        return;
    } 
    
    if (targetField == null) 
        targetField = "participants";

    currFormType = targetField;
}



// switch data from from nav button
function switchDataForm(targetField, isNotNeedValid) {
    quoteF = $('#'+targetField+'quote').html();         
    // unsaved warning box  
    if (!warnUnsavedDialog())
        return;

    // pop up warn for selecting span when switch to new targetField dring editing mode
    if (!isTextSelected && (targetField != "evRelationship" || targetField != "question") && quoteF == "" && !isNotNeedValid) {
        warnSelectTextSpan(targetField);
        return;
    } 
    
    if (targetField == null) 
        targetField = "participants";

    currFormType = targetField;
    switchDataFormHelper(targetField);
}

function switchDataFormHelper(targetField) {

    // field actual div id mapping
    fieldM = {"evRelationship":"evRelationship", "participants":"participants", "dose1":"drug1Dose", "dose2":"drug2Dose", "auc":"auc", "cmax":"cmax", "clearance":"clearance", "halflife":"halflife", "question":"question"};

    var showDeleteBtn = false;

    for (var field in fieldM) {       
        var dataid = "mp-data-form-"+field;
        if (field === targetField) {
            $("#"+dataid).show();  // show specific data form 
            // inspect that is target form has value filled 

            if (field == "evRelationship" || field =="question") { // when field is radio button
                fieldVal = $("input[name="+field+"]:checked").val();
            } else if (field == "auc" || field == "cmax" || field == "clearance" || field == "halflife") { // when field is checkbox
                $("#mp-data-nav").show();
                if ($('#' + field + '-unchanged-checkbox').is(':checked')) 
                    showDeleteBtn = true;                    
                fieldVal = $("#" + fieldM[field]).val();
            } else { // when field is text input
                $("#mp-data-nav").show();
                fieldVal = $("#" + fieldM[field]).val();
            }

            console.log(fieldVal);
                
            if (fieldVal !=null && fieldVal != "")
                $("#annotator-delete").show();
            else if (showDeleteBtn)
                $("#annotator-delete").show();
            else 
                $("#annotator-delete").hide();
        }                        
        else {
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
