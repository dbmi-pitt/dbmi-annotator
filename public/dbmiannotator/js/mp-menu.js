// show annotation table
function showAnnTable(){
    console.log("mp-menu - showAnnTable()");
    $('#tabs').tabs("option", "active", 0);

    $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 250}]
    });

    $('.editorsection').hide();
    $('.annotator-editor').hide();

    $('.btn-success').val("show");
    $('.btn-success').css("margin-bottom",250);
    $('.btn-home').css("margin-bottom",250);
    $('#menu').html("&nbsp Collapse");
    
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
}

//undraw currhigglighter
function undrawCurrhighlighter() {

    var currhighlighters =  $("span[name='annotator-currhl']");
    for(var i=0;i<currhighlighters.length;i++) {
        var h = currhighlighters[i];
        $(h).replaceWith(h.childNodes);
    }
}


//show annotaton editor
function showEditor(){
    //open editor tab before editor is triggered
    var index = $("#tabs-1").index();
    $('#tabs').tabs("option", "active", index);
    $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 250}]
    });
    $('.editorsection').show();
    $('.btn-success').val("show");
    $('.annotator-editor').show();
    $('.btn-success').css("margin-bottom",250);
    $('.btn-home').css("margin-bottom",250);
    $('#menu').html("&nbsp Collapse");
    
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);

    // hide delete button
    // console.log("mp-menu - showEditor - disable delete button");
    $("#annotator-delete").hide();
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

//show annotator panel by button "btn-success"
//deprecated buttonshowright
function annotationPanelClick(){
    
    if($('.btn-success').val()=="hide") {
        
        $('#splitter').jqxSplitter({
            showSplitBar:false,
            width: $(window).width(),
            height: $(window).height(),
            orientation: 'horizontal', 
            panels: [{size: '80%', min: 200}, {size: '20%', min: 250}]
        });
        
        $('#tabs').tabs("option", "active", 0);
        $('.editorsection').hide();
        $('.btn-success').val("show");
        $('.annotator-editor').show();
        $('.btn-success').css("margin-bottom",250);
        $('.btn-home').css("margin-bottom",250);
    }
    else {
        
        // unsaved warning box  
        if (!warnUnsavedDialog())
            return;

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
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
    
}

function exitEditorToAnnTable(){
    
    if($('.btn-success').val()=="hide") {
        var tab = $('#tabs-2').attr('href');
        $('#tabs').tabs('select', tab);
        $('#splitter').jqxSplitter({
            showSplitBar:false,
            width: $(window).width(),
            height: $(window).height(),
            orientation: 'horizontal', 
            panels: [{size: '80%', min: 200}, {size: '20%', min: 250}]
        });
        $('.editorsection').show();
        $('.btn-success').val("show");
        $('.annotator-editor').show();
        $('.btn-success').css("margin-bottom",250);
        $('.btn-home').css("margin-bottom",250);
        // $('#menu').html("&nbsp Collapse");
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
      // $('#menu').html("&nbsp Menu");
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
  }


// click home button back to main page
function backToHome() {
    // unsaved warning box  
    if (!warnUnsavedDialog())
        return;

    location.href = '/dbmiannotator/main';
}


// if there is unsaved changes, pop up dialog for reminding 
// return true if everything saved, otherwise return false
function warnUnsavedDialog() {

    if (unsaved) {
        var unsaveDialog = document.getElementById('remind-unsave-dialog');
        var dialogBtn = document.getElementById('remind-dialog-ok-btn');
        var span = document.getElementById("unsave-dialog-close");
        unsaveDialog.style.display = "block";

        dialogBtn.onclick = function() {
            unsaveDialog.style.display = "none";
        }

        // When the user clicks anywhere outside of the dialog, close it
        window.onclick = function(event) {
            if (event.target == dialogBtn) {
                unsaveDialog.style.display = "none";
            }
        }

        // When the user clicks on <span> (x), close the dialog
        span.onclick = function() {
            unsaveDialog.style.display = "none";
        }
        
        return false; 
    } else {
        return true;
    }


}
