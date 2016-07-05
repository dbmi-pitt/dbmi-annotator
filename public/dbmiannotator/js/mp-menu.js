// show annotation table
function showAnnTable(){
    console.log("mp-menu - showAnnTable()");
    $('#tabs').tabs("option", "active", 0);

    $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 260}]
    });

    $('.editorsection').hide();
    $('.annotator-editor').hide();

    $('.btn-success').val("show");
    $('.btn-success').css("margin-bottom",230);
    $('.btn-home').css("margin-bottom",230);
    $('#menu').html("&nbsp Collapse");
    
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
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
        panels: [{size: '80%', min: 200}, {size: '20%', min: 260}]
    });
    $('.editorsection').show();
    $('.btn-success').val("show");
    $('.annotator-editor').show();
    $('.btn-success').css("margin-bottom",230);
    $('.btn-home').css("margin-bottom",230);
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
  function buttonshowright(){
    
    if($('.btn-success').val()=="hide") {

      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 260}]
      });
    
      $('#tabs').tabs("option", "active", 0);
      $('.editorsection').hide();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",230);
      $('.btn-home').css("margin-bottom",230);
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
        panels: [{size: '80%', min: 200}, {size: '20%', min: 260}]
      });
      $('.editorsection').show();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",230);
      $('.btn-home').css("margin-bottom",230);
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
