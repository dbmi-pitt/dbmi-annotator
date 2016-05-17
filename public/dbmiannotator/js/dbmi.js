$(document).ready(function () {
    // splitter for show annotation panel
    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });

    // MP adder - open/close claim menu
    $(function() {
        $('.mp-menu-btn').hover(function() { 
            $('.mp-main-menu').show(); 
        });
    });
    
    $('.mp-main-menu-2').mouseenter(function(){
        $(this).find('.mp-sub-menu-2').slideDown();
    });
    
    $('.mp-main-menu-2').mouseleave(function(){
        $(this).find('.mp-sub-menu-2').slideUp();
    });
 
});

// modify annotaiton id when user pick claim on mpadder's menu
// update annotation table if necessary
function claimSelectedInMenu(annotationId) {
    $("#mp-annotation-work-on").html(annotationId);
    annTableId = $('#mp-editor-claim-list option:selected').val();

    if (annotationId != annTableId){
        $("#mp-editor-claim-list option[value='" + annotationId + "']").attr("selected", "true");
        changeClaimInAnnoTable();
    }
}

// open claim editor
function claimEditorLoad() {
    $("#mp-editor-type").html('claim');
    $("#mp-claim-form").show();

    showEnzyme();

    $("#mp-data-nav").hide();
    $("#mp-data-form-participants").hide();
    $("#mp-data-form-dose1").hide();
    $("#mp-data-form-dose2").hide();
}


// changed claim in annotation table, update data & material
function changeClaimInAnnoTable() {
    var newAnnotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("claim changed to :" + newAnnotationId);
    $("#mp-annotation-work-on").html(newAnnotationId);

    sourceURL = getURLParameter("sourceURL").trim();
    email = getURLParameter("email");

    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: "MP", 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){
                updateClaimAndData(response.rows, newAnnotationId);
            }     
           });    
}


// open data Editor (1) if annotation is null, then switch form for data field
// (2) otherwise, load annotation to editor, then shown specific form
function dataEditorLoad(annotation, field, annotationId) {
    console.log("dataEditorLoad - id: " + annotationId + " | field: " + field);
    
    // updating current MP annotation
    if (annotationId != null)
        $("#mp-annotation-work-on").html(annotationId);

    switchDataForm(field);

    // call AnnotatorJs editor for update    
    app.annotations.update(annotation);                        
}


// load data Editor based on selection from annotation table
// (1) if annotation is null, then switch form for data field
// (2) otherwise, load annotation to editor, then shown specific form
function dataEditorLoadAnnTable(field) {

    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("dataEditorLoad - id: " + annotationId + " | field: " + field);

    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
            data: {},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(annotation){

                console.log(annotation);
                // updating current MP annotation
                if (annotationId != null)
                    $("#mp-annotation-work-on").html(annotationId);

                switchDataForm(field);

                // call AnnotatorJs editor for update    
                app.annotations.update(annotation);   
            }
           });                     
}

// open data editor with specific form
function switchDataForm(field) {

    fieldL = ["participants","dose1","dose2"];
    
    if (field == null) 
        field = "participants";
    $("#mp-editor-type").html(field);
    
    $("#mp-data-nav").show();
    $("#mp-claim-form").hide();
    
    // shown specific data form, hide others
    for (i = 0; i < fieldL.length; i++){
        var dataid = "mp-data-form-"+fieldL[i];
        if (fieldL[i] == field){
            $("#"+dataid).show();            
        } else {
            $("#"+dataid).hide();
        }
    }
}


// Claim editor - options 1) continue create claim, 2) add data, 3) done
function serveClaimOptions(){

    if ($("#mp-editor-type").html() == "claim") { 
        $( "#claim-dialog-confirm" ).dialog({
            resizable: false,
            height: 'auto',
            width: '400px',
            modal: true,
            buttons: {
                "Add another claim": function() {
                    $( this ).dialog( "close" );
                },
                "Add data": function() {
                    $( this ).dialog( "close" );
                },
                "Done": function() {
                    $( this ).dialog( "close" );
                    showrightbyvalue();
                }
            }
        });
    } else {
        showrightbyvalue();        
    }
}


//show right splitter directly
function showright(){
    //open editor tab before editor is triggered
    var index = $("#tabs-1").index();
    $('#tabs').tabs("option", "active", index);
    $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
    });
    $('.editorsection').show();
    $('.btn-success').val("show");
    $('.annotator-editor').show();
    $('.btn-success').css("margin-bottom",270);
    $('.btn-home').css("margin-bottom",270);
    $('#menu').html("&nbsp Collapse");
    
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
}


var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

//show right splitter by button "btn-success"
  function buttonshowright(){
    
    if($('.btn-success').val()=="hide") {

      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
      });
    
      $('#tabs').tabs("option", "active", 0);
      $('.editorsection').hide();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",270);
      $('.btn-home').css("margin-bottom",270);
      $('#menu').html("&nbsp Collapse");
    }
    else {
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: '100%',
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '100%', min: 200}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-bottom",0);
      $('.btn-home').css("margin-bottom",0);
      $('#menu').html("&nbsp Menu");
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
    
    
  }

  function showrightbyvalue(){
    
    if($('.btn-success').val()=="hide") {
      var tab = $('#tabs-2').attr('href');
      $('#tabs').tabs('select', tab);
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
      });
      $('.editorsection').show();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",270);
      $('.btn-home').css("margin-bottom",270);
      $('#menu').html("&nbsp Collapse");
    }
    else {
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: '100%',
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '100%', min: 200}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-bottom",0);
      $('.btn-home').css("margin-bottom",0);
      $('#menu').html("&nbsp Menu");
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
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


$("#relationship").change(function showEnzyme() {
    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
    }
});

function showEnzyme() {
    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
    }
}

// $("#assertion_type").change(function changeFunc() {
//     if($("#assertion_type option:selected").text()=="DDI clinical trial") { 
//         $("#firstsection").hide(); 
//         $("#altersection").show();
//         var object = $("#Drug1 option:selected").text(); 
//         $("#objectinalter").html("Object: "+object);
//         var precipt = $("#Drug2 option:selected").text(); 
//         $("#preciptinalter").html("Precipt: "+precipt);
//         $("#back").show();
//         var modal = $("#Modality:checked").val();
//         $("#modalityinalter").html("Modality: "+modal);
//         var evid = $("#Evidence_modality:checked").val();
//         $("#evidenceinalter").html("Evidence: "+evid);
        
//     } else {
//         $("#altersection").hide();$("#forward").hide();
//     }
// });


// function flipdrug() {
//     var object = $("#Drug1 option:selected").text();
//     var precip = $("#Drug2 option:selected").text();
//     $("#Drug1 option").removeAttr("selected");
//     $("#Drug2 option").removeAttr("selected");
//     $("#Drug1 > option").each(function () {
//         if ($(this).text() == precip){ 
//             $(this).prop("selected", "selected");
//         }
//     });
//     $("#Drug2 > option").each(function () {
//         if ($(this).text() == object) 
//             $(this).prop("selected", "selected");
//     });
// }

// function backtofirst() {
//     $("#firstsection").show(); 
//     $("#altersection").hide();
//     $("#forward").show();
//     $("#back").hide();
// }

// function forwardtosecond() {
//     $("#firstsection").hide(); 
//     $("#altersection").show();
//     $("#forward").hide();
//     $("#back").show();
//     var object = $("#Drug1 option:selected").text(); 
//     $("#objectinalter").html("Object: "+object);
//     var precipt = $("#Drug2 option:selected").text(); 
//     $("#preciptinalter").html("Precipt: "+precipt);
//     var modal = $("#Modality:checked").val();
//     $("#modalityinalter").html("Modality: "+modal);
//     var evid = $("#Evidence_modality:checked").val();
//     $("#evidenceinalter").html("Evidence: "+evid);
// }

// function changeRole1(role) {
//     $(".Role2").each(function(){ 
//         if(this.value != role) 
//             this.checked = true; 
//         else 
//             this.checked = false;
//     });
// }

// function changeRole2(role) {
//     $(".Role1").each(function(){ 
//         if(this.value != role) 
//           this.checked = true; 
//         else this.checked = false;
//       });
// }
