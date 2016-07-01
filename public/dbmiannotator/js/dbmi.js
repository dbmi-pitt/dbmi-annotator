$(document).ready(function () {
    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });
    //$('.secondsection').append("<p><a href='http://www.google.com'>Google</a></p>");
  });

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

//show right splitter directly
  function showright(){
      //open editor tab before editot is triggered
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

  //move from editor.js
  
  function editorload() {
      $("#firstsection").show();
      $("#altersection").hide();
      showEnzyme();
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

  $("#assertion_type").change(function changeFunc() {
      if($("#assertion_type option:selected").text()=="DDI clinical trial") { 
        $("#firstsection").hide(); 
        $("#altersection").show();
        var object = $("#Drug1 option:selected").text(); 
        $("#objectinalter").html("Object: "+object);
        var precipt = $("#Drug2 option:selected").text(); 
        $("#preciptinalter").html("Precipt: "+precipt);
        $("#back").show();
        var modal = $("#Modality:checked").val();
        $("#modalityinalter").html("Modality: "+modal);
        var evid = $("#Evidence_modality:checked").val();
        $("#evidenceinalter").html("Evidence: "+evid);
      
      } else {
        $("#altersection").hide();$("#forward").hide();
      }
  });

  $( "#relationship" ).change(function showEnzyme() {
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
      if($('#relationship').val()=="inhibits"||$('#relationship').val()=="substrate of") {
          $("#enzymesection1").show();
          $("#enzyme").show();
      }
      if($('#relationship').val()=="interact with") {
          $("#enzymesection1").hide();
          $("#enzyme").hide();
      }
  }

  function flipdrug() {
      var object = $("#Drug1 option:selected").text();
      var precip = $("#Drug2 option:selected").text();
      $("#Drug1 option").removeAttr("selected");
      $("#Drug2 option").removeAttr("selected");
      $("#Drug1 > option").each(function () {
          if ($(this).text() == precip){ 
            $(this).prop("selected", "selected");
          }
      });
      $("#Drug2 > option").each(function () {
          if ($(this).text() == object) 
            $(this).prop("selected", "selected");
      });
  }

  function backtofirst() {
      $("#firstsection").show(); 
      $("#altersection").hide();
      $("#forward").show();
      $("#back").hide();
  }

  function forwardtosecond() {
      $("#firstsection").hide(); 
      $("#altersection").show();
      $("#forward").hide();
      $("#back").show();
      var object = $("#Drug1 option:selected").text(); 
      $("#objectinalter").html("Object: "+object);
      var precipt = $("#Drug2 option:selected").text(); 
      $("#preciptinalter").html("Precipt: "+precipt);
      var modal = $("#Modality:checked").val();
      $("#modalityinalter").html("Modality: "+modal);
      var evid = $("#Evidence_modality:checked").val();
      $("#evidenceinalter").html("Evidence: "+evid);
  }

  function changeRole1(role) {
      $(".Role2").each(function(){ 
          if(this.value != role) 
            this.checked = true; 
          else 
            this.checked = false;
      });
  }

  function changeRole2(role) {
      $(".Role1").each(function(){ 
        if(this.value != role) 
          this.checked = true; 
        else this.checked = false;
      });
  }
