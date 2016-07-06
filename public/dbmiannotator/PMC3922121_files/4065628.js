jQuery(function($j) {
      var formState = {
          overrideBackends: false,
          backends: {}
      };
      
      // Name of the cookie
      var cookieName;
      
      // Mostly just for debugging, store the cookie string value here
      // rather than in the sub-function scope
      var cookieStr;
      
      // An object representation of the cookie.  This is converted from the
      // XML cookie value on init.  The form controls will manipulate this,
      // and when the user clicks "Go", this will be converted back into
      // XML.
      var cookieObj;

      ///////////////////////////////////////////////////////////////////////////////
      function cbChanged(event) {
          //console.info("Event caught: " + event);
          var target = $j(event.target);
          var id = target.attr("id");
          var value = target.attr("value");
          var checked = target.attr("checked");
          /*console.info("target id: '" + id + 
                       "', value: '" + value + 
                       "', checked: '" + checked + "'");*/
          
          
          if (id == "besetsel-cb") {
              if (checked) {
                  $j("#besetsel-sel").removeAttr("disabled");
                  besetSelFormToObj();
              }
              else {
                  $j("#besetsel-sel").attr("disabled", 1);
                  delete cookieObj.besetName;
              }
          }
          else if (id == "besetsel-sel") {
              besetSelFormToObj();
          }
          else {
              var m;
              if (m = id.match(/besetsel-be-(.*?)-cb/)) {
                  var backend = m[1];
                  //console.info(">>>backend checkbox:  " + backend);
                  if (checked) {
                      $j("#besetsel-be-" + backend + "-text").removeAttr("disabled");
                      beUrlFormToObj(backend);
                  }
                  else {
                      $j("#besetsel-be-" + backend + "-text").attr("disabled", 1);
                      delete cookieObj.backendUrls[backend];
                  }
              }
              else if (m = id.match(/besetsel-be-(.*?)-text/)) {
                  backend = m[1];
                  //console.info(">>>backend text:  " + backend);
                  beUrlFormToObj(backend);
              }
          }
          
          // PMC-11784 and PMC-11785.
          // This fixes a nasty IE bug.  It causes a slight flash when the user
          // clicks a checkbox, but it works.
          if (jQuery.browser.msie){
              target.hide();
              window.setTimeout( function(){ target.show();}, 0 );
          }
          
      }

      ///////////////////////////////////////////////////////////////////////////////
      // besetSelFormToObj()
      // This is called by a couple of event handlers and decodes the
      // currently selected BESet (in the drop-down form) and sets the
      // cookieObj.besetName accordingly.

      function besetSelFormToObj()
      {
          cookieObj.besetName = $j("#besetsel-sel").val();
      }

      ///////////////////////////////////////////////////////////////////////////////
      // beUrlFormToObj(backend)
      // This is similar, and takes care of reading the text value from the
      // form and stuffing it into the object

      function beUrlFormToObj(backend) {
          var value = $j("#besetsel-be-" + backend + "-text").attr("value");
          if (value) cookieObj.backendUrls[backend] = value;
      }

      ///////////////////////////////////////////////////////////////////////////////
      function init() {
          if ($j("#besetsel-form").length < 1)
          {
              return;
          }
          
          cookieName = $j("#besetsel-form").attr("cookieName");
          cookieObj = cookieXmlToJson(cookieName);
          initFormState();

          // Set event handers
          $j("#besetsel-form .besetsel-control").change(function(event) {
              cbChanged(event);
          });
          $j("#besetsel-go-button").click(function(event) {
              goButton(event);
          });
          $j("#besetsel-reset-button").click(function(event) {
              resetButton(event);
          });
          
          // This "pullout" might be empty, in the case of the BESet being
          // selected by path segment instead of cookie.  In that case, the
          // tab acts as a watermark, just to identify the BESet, and we
          // don't want to allow it to be "pulled out".  So we'll set the
          // width to 0 in that case.
          var w = $j("#besetsel-go-button").length > 0 ? "400px" : "0px";

          // Put it into the sidecontent pullout
          $j("#besetsel-form").sidecontent({
              /*classmodifier: "besetsel",*/
              attachto: "rightside",
              width: w,
              opacity: "0.8",
              pulloutpadding: "5",
              textdirection: "vertical",
              clickawayclose: 0,
              titlenoupper: 1
          });
          
          var pulloutColor = $j("#besetsel-form").attr("pulloutColor");
          //alert("color is " + pulloutColor);
          $j("#besetsel-form").data("pullout").css("background-color", pulloutColor || '#663854');
          
          if ($j("#besetsel-go-button").size() > 0) {
              $j("#besetsel-form").data("pullout").css({
                  "border-top": "ridge gray 5px",
                  "border-bottom": "ridge gray 5px",
                  "border-left": "ridge gray 5px"
              });
          }
      }

      ///////////////////////////////////////////////////////////////////////////////
      // goButton(event)
      // Handle the user-click of the "Go!" button.
      
      function goButton(event) {
          // Convert the object into XML
          var cookieXml = "<Backends><BESet" + ( cookieObj.besetName ? (" name='" + cookieObj.besetName + "'>") : ">" );
          for (var backend in cookieObj.backendUrls) {
              //console.info("+++ backend " + backend);
              cookieXml += 
                "<Backend name='" + backend + "'>" + xmlEscape(cookieObj.backendUrls[backend]) + "</Backend>";
          }
          cookieXml += "</BESet></Backends>";
          //console.info(cookieXml);
          
          // Set the cookie
          document.cookie = cookieName + "=" + encodeURIComponent(cookieXml) +
                            "; max-age=604800" +
                            "; path=/" +
                            "; domain=nih.gov";
          // Reload the page
          window.location.reload();
      }
      
      ///////////////////////////////////////////////////////////////////////////////
      // resetButton(event)
      // Handle the user-click of the "Reset" button.
      // Does the same thing as "Go!", but sets the cookie to the empty string.

      function resetButton(event) {
          // Clear the cookie
          document.cookie = cookieName + "=" + 
                            "; max-age=604800" +
                            "; path=/" +
                            "; domain=nih.gov";
          // Reload the page
          window.location.reload();
      }
      
      ///////////////////////////////////////////////////////////////////////////////
      function xmlEscape(str) {
          str = str.replace(/\&/g, '&amp;')
                   .replace(/\</g, '&lt;')
                   .replace(/\>/g, '&gt;')
                   .replace(/\"/g, '&quot;')
                   .replace(/\'/g, '&apos;');
          return str;
      }

      ///////////////////////////////////////////////////////////////////////////////
      // This function reads the cookie value and initializes the form state
      // Don't assume anything about the form state -- redo everything.
      function initFormState() {

          var besetName = cookieObj.besetName;

          if (!besetName) {
              $j("#besetsel-cb").removeAttr("checked");
              $j("#besetsel-sel").attr("disabled", 1);
          }
          else {
              var selBESet = $j("#besetsel-opt-" + besetName);
              if (selBESet.length != 0) {
                  $j("#besetsel-cb").attr("checked", 1);
                  $j("#besetsel-sel").removeAttr("disabled");
                  selBESet.attr("selected", 1);
              }
              else {
                  $j("#besetsel-cb").removeAttr("checked");
                  $j("#besetsel-sel").attr("disabled", 1);
              }
          }
          
          // Foreach backend in the form
          $j(".besetsel-be-cb").each(function(i) {
              var id = $j(this).attr("id");
              var beName = id.match(/besetsel-be-(.*?)-cb/)[1];
              //console.info("### backend, id is '" + id + "', beName is '" + beName + "'");
              if (!beName) return;
              
              // See if there's a corresponding element in the cookie
              if (!cookieObj.backendUrls ||
                  !cookieObj.backendUrls[beName]) {
                  //console.info("Didn't find " + beName);
                  $j("#besetsel-be-" + beName + "-cb").removeAttr("checked");
                  $j("#besetsel-be-" + beName + "-text").attr("disabled", 1);
              }
              else {
                  //console.info("Found " + beName);
                  $j("#besetsel-be-" + beName + "-cb").attr("checked", 1);
                  var textbox = $j("#besetsel-be-" + beName + "-text");
                  textbox.removeAttr("disabled");
                  textbox.attr("value", cookieObj.backendUrls[beName]);
              }
          });
      }
      
      ///////////////////////////////////////////////////////////////////////////////
      // This gets the value of the <snapshot>_beset cookie, which is in XML, and turns it
      // from this:
      //   <BESet name='test'>
      //     <BackendUrl backend='tagserver' url='bingo'/>
      //     ...
      //   </BESet>
      // Into this (note that everything is optional):
      //   { besetName: 'test',
      //     backendUrls: {
      //         tagserver: 'bingo', ... }
      //   }
      // If there is no cookie set or parsing fails, this returns {}.
      
      function cookieXmlToJson(cookieName) {
          var cookieObj = {
              backendUrls: {}
          };

          cookieStr = getCookie(cookieName);
          //console.info("cookie value is '" + cookieStr + "'");

          // Parse XML
          try {
              var cookieXml = $j(cookieStr);
          }
          catch(err) {
              return cookieObj;
          }
          
          var besetElem = cookieXml.find('BESet');
          if (besetElem.length == 0) {
              // No valid cookie value found.
              return cookieObj;
          }
          
          var besetName = besetElem.attr("name");
          if (besetName) {
              cookieObj.besetName = besetName; 
          }
          
          var backends = besetElem.find("backend");
          if (backends.length != 0) {
              backends.each(function (i) {
                  var e = $j(backends[i]);
                  cookieObj.backendUrls[e.attr("name")] = e.text();
                  //console.info("Setting " + e.attr("backend") + ": " + e.attr("url"));
              })
          }
          
          return cookieObj;
      }

      ///////////////////////////////////////////////////////////////////////////////
      function getCookie(name) {
          var allCookies = document.cookie;
          //console.info("allCookies = " + allCookies);
          var pos = allCookies.indexOf(name + "=");
          if (pos != -1) {
              var start = pos + (name + "=").length;
              var end = allCookies.indexOf(";", start);
              if (end == -1) end = allCookies.length;
              return decodeURIComponent(allCookies.substring(start, end)); 
          }
          return "";
      }
        
    init();
    
});



;
(function($)
{
	// This script was written by Steve Fenton
	// http://www.stevefenton.co.uk/Content/Jquery-Side-Content/
	// Feel free to use this jQuery Plugin
	// Version: 3.0.2
	
	var classModifier = "";
	var sliderCount = 0;
	var sliderWidth = "400px";
	
	var attachTo = "rightside";
	
	var totalPullOutHeight = 0;
	
	function CloseSliders (thisId) {
		// Reset previous sliders
		for (var i = 0; i < sliderCount; i++) {
			var sliderId = classModifier + "_" + i;
			var pulloutId = sliderId + "_pullout";
			
			// Only reset it if it is shown
			if ($("#" + sliderId).width() > 0) {

				if (sliderId == thisId) {
					// They have clicked on the open slider, so we'll just close it
					showSlider = false;
				}

				// Close the slider
				$("#" + sliderId).animate({
					width: "0px"
				}, 100);
				
				// Reset the pullout
				if (attachTo == "leftside") {
					$("#" + pulloutId).animate({
						left: "0px"
					}, 100);
				} else {
					$("#" + pulloutId).animate({
						right: "0px"
					}, 100);
				}
			}
		}
	}
	
	function ToggleSlider () {
		var rel = $(this).attr("rel");

		var thisId = classModifier + "_" + rel;
		var thisPulloutId = thisId + "_pullout";
		var showSlider = true;
		
		if ($("#" + thisId).width() > 0) {
			showSlider = false;
		}

        CloseSliders(thisId);
		
		if (showSlider) {
			// Open this slider
			$("#" + thisId).animate({
				width: sliderWidth
			}, 250);
			
			// Move the pullout
			if (attachTo == "leftside") {
				$("#" + thisPulloutId).animate({
					left: sliderWidth
				}, 250);
			} else {
				$("#" + thisPulloutId).animate({
					right: sliderWidth
				}, 250);
			}
		}
		
		return false;
	};

	$.fn.sidecontent = function (settings) {
	
		var config = {
			classmodifier: "sidecontent",
			attachto: "rightside",
			width: "300px",
			opacity: "0.8",
			pulloutpadding: "5",
			textdirection: "vertical",
			clickawayclose: false
		};
		
		if (settings) {
			$.extend(config, settings);
		}
		
		return this.each(function () {
		
			$This = $(this);
			
			// Hide the content to avoid flickering
			$This.css({ opacity: 0 });
			
			classModifier = config.classmodifier;
			sliderWidth = config.width;
			attachTo = config.attachto;
			
			var sliderId = classModifier + "_" + sliderCount;
			var sliderTitle = config.title;
			
			// Get the title for the pullout
			sliderTitle = $This.attr("title");
			
			// Start the totalPullOutHeight with the configured padding
			if (totalPullOutHeight == 0) {
				totalPullOutHeight += parseInt(config.pulloutpadding);
			}

			if (config.textdirection == "vertical") {
				var newTitle = "";
				var character = "";
				for (var i = 0; i < sliderTitle.length; i++) {
					character = sliderTitle.charAt(i).toUpperCase();
					if (character == " ") {
						character = "&nbsp;";
					}
					newTitle = newTitle + "<span>" + character + "</span>";
				}
				sliderTitle = newTitle;
			}
			
			// Wrap the content in a slider and add a pullout			
			$This.wrap('<div class="' + classModifier + '" id="' + sliderId + '"></div>').wrap('<div style="width: ' + sliderWidth + '"></div>');
            var pullout = $('<div class="' + classModifier + 'pullout" id="' + sliderId + '_pullout" rel="' + sliderCount + '">' + sliderTitle + '</div>').insertBefore($("#" + sliderId));
            
            // Store reference to the tab element in parent 
            $This.data('pullout', pullout);
			
			if (config.textdirection == "vertical") {
				$("#" + sliderId + "_pullout span").css({
					display: "block",
					textAlign: "center"
				});
			}
			
			// Hide the slider
			$("#" + sliderId).css({
				position: "absolute",
				overflow: "hidden",
				top: "0",
				width: "0px",
				zIndex: "1",
				opacity: config.opacity
			});
			
			// For left-side attachment
			if (attachTo == "leftside") {
				$("#" + sliderId).css({
					left: "0px"
				});
			} else {
				$("#" + sliderId).css({
					right: "0px"
				});
			}
			
			// Set up the pullout
			$("#" + sliderId + "_pullout").css({
				position: "absolute",
				top: totalPullOutHeight + "px",
				zIndex: "1000",
				cursor: "pointer",
				opacity: config.opacity
			})
			
			$("#" + sliderId + "_pullout").live("click", ToggleSlider);
			
			var pulloutWidth = $("#" + sliderId + "_pullout").width();
			
			// For left-side attachment
			if (attachTo == "leftside") {
				$("#" + sliderId + "_pullout").css({
					left: "0px",
					width: pulloutWidth + "px"
				});
			} else {
				$("#" + sliderId + "_pullout").css({
					right: "0px",
					width: pulloutWidth + "px"
				});
			}
			
			totalPullOutHeight += parseInt($("#" + sliderId + "_pullout").height());
			totalPullOutHeight += parseInt(config.pulloutpadding);
			
			var suggestedSliderHeight = totalPullOutHeight + 30;
			if (suggestedSliderHeight > $("#" + sliderId).height()) {
				$("#" + sliderId).css({
					height: suggestedSliderHeight + "px"
				});
			}
			
			if (config.clickawayclose) {
				$("body").click( function () {
					CloseSliders("");
				});
			}
			
			// Put the content back now it is in position
			$This.css({ opacity: 1 });
			
			sliderCount++;
		});
		
		return this;
	};
})(jQuery);
;
/* Override this file with one containing code that belongs on every page of your application */


;
jQuery(function($) {
    // Set event listener to scroll the nav poppers to the current page when opened
    $("#source-link-top, #source-link-bottom").bind(
        "ncbipopperopencomplete",
        function() {
            var dest = $(this).attr('href');
            var selected_link = $(dest).find('.current-toc-entry');

            if (selected_link.length > 0) 
            {
                $(dest).scrollTo(selected_link, { offset: -100, duration:  400 });
            }
        }
    );  
});


;
(function($){

    $(function() {    

        var theSearchInput = $("#term");
        var originalTerm = $.trim(theSearchInput.val());
        var theForm = jQuery("form").has(theSearchInput);
        var dbNode = theForm.find("#database");
        var currDb = dbNode.val();
        var sbConfig = {};
        try{
            sbConfig = eval("({" + theSearchInput.data("sbconfig") + "})");
        }catch(e){}
        var defaultSubmit =  sbConfig.ds == "yes";
        var searched = false;
        var dbChanged = null; //since db.change is triggered as a work around for JSL-2067 
        var searchModified = false; //this is used to allow searching when something esle changed on the page with out the term changing
    
        if(!$.ncbi)
            $.extend($,{ncbi:{}});
        if(!$.ncbi.searchbar)
            $.extend($.ncbi,{searchbar:{}});
            
        $.extend($.ncbi.searchbar,
            (function(){
                //*****************private ******************/
               function doSearchPing() {
                   try{
                    var cVals = ncbi.sg.getInstance()._cachedVals;
                    var searchDetails = {}
                    searchDetails["jsEvent"] = "search";
                    var app = cVals["ncbi_app"];
                    var db = cVals["ncbi_db"];
                    var pd = cVals["ncbi_pdid"];
                    var pc = cVals["ncbi_pcid"];
                    var sel = dbNode[0];
                    var searchDB = sel.options[sel.selectedIndex].value;
                    var searchText = theSearchInput[0].value;
                    if( app ){ searchDetails["ncbi_app"] = app.value; }
                    if( db ){ searchDetails["ncbi_db"] = db.value; }
                    if( pd ){ searchDetails["ncbi_pdid"] = pd.value; }
                    if( pc ){ searchDetails["ncbi_pcid"] = pc.value; }
                    if( searchDB ){ searchDetails["searchdb"] = searchDB;}
                    if( searchText ){ searchDetails["searchtext"] = searchText;}
                    ncbi.sg.ping( searchDetails );
                   }catch(e){
                       console.log(e);
                   }
                }
                function getSearchUrl(term){
                    var url = "";
                    if (typeof(NCBISearchBar_customSearchUrl) == "function") 
                            url = NCBISearchBar_customSearchUrl();
                    if (!url) {
                        var searchURI = dbNode.find("option:selected").data("search_uri");
                        url = searchURI ?  searchURI.replace('$',term) : 
                             "/" + dbNode.val() + "/" + ( term !="" ? "?term=" + term : "");
                        }
                    return url;
                }
            
                return {
                    //*****************exposed attributes and functions ******************/
                    'theSearchInput':theSearchInput,
                    'theForm':theForm,
                    'dbNode':dbNode,
                    'searched':searched,
                    'setSearchModified':function() { searchModified = true; },
                    'setSearchUnmodified':function() { searchModified = false; },
                    'searchModified':function(){return searchModified;},
                    'doSearch':function(e){
                           e.stopPropagation();
                           e.preventDefault();
                           //checking for the searched flag is necessary because the autocompelete control fires on enter key, the form submit also fires on enter key
                           if(searched == false){
                               searched = true;
                               theForm.find('input[type="hidden"][name^="p$"]').attr('disabled', 'disabled');
                               //$("input[name]").not(jQuery(".search_form *")).attr('disabled', 'disabled');
                               if (defaultSubmit)
                                   $.ncbi.searchbar.doSearchPing();
                               else {
                                   var term = $.trim(theSearchInput.val());
                                   if (dbChanged || searchModified || term !== originalTerm){
                                       $.ncbi.searchbar.doSearchPing();
                                       var searchUrl = $.ncbi.searchbar.getSearchUrl(encodeURIComponent(term).replace(/%20/g,'+'));
                                       var doPost = (term.length  > 2000) ? true : false; 
                                       if (doPost){
                                           if (e.data.usepjs){
                                               Portal.$send('PostFrom',{"theForm":theForm,"term":term,"targetUrl":searchUrl.replace(/\?.*/,'')});
                                           }
                                           else{
                                               theForm.attr('action',searchUrl.replace(/\?.*/,''));
                                               theForm.attr('method','post');
                                           }
                                       }
                                       else {
                                           window.location = searchUrl;
                                       }
                                   }
                                   else{ //if (term !== originalTerm){
                                       searched = false;
                                   }
                               }
                           }
                    },
                    'onDbChange':function(e){
                         if (dbChanged === null)
                             dbChanged = false;
                         else
                             dbChanged = true;
                         var optionSel = $(e.target).find("option:selected");
                         var dict = optionSel.data("ac_dict");
                         if (dict){
                             //theSearchInput.ncbiautocomplete("option","isEnabled",true).ncbiautocomplete("option","dictionary",dict);
                             theSearchInput.ncbiautocomplete({
                                    isEnabled: true,
                                    dictionary: dict
                                });
                             theSearchInput.attr("title","Search " + optionSel.text() + ". Use up and down arrows to choose an item from the autocomplete.");
                         }
                         else{
                           theSearchInput.ncbiautocomplete("turnOff",true);
                           theSearchInput.attr("title", "Search " + optionSel.text());
                         }
                         if (defaultSubmit)
                            theForm.attr('action','/' + dbNode.val() + '/');  
                    },
                    'doSearchPing':function(){
                        doSearchPing();
                    },
                    'getSearchUrl':function(term){
                        return getSearchUrl(term);
                    }
                    
                };//end of return 
             })() //end of the self executing anon
        );//end of $.extend($.ncbi.searchbar
    
         function initSearchBar(usepjs){
            //enable the controls for the back button
            theForm.find('input[type="hidden"][name^="p$"]').removeAttr('disabled');
             if (usepjs)
                 portalSearchBar();
         }
         
        
    
        function portalSearchBar(){
            
            Portal.Portlet.NcbiSearchBar = Portal.Portlet.extend ({
                init:function(path,name,notifier){
                    this.base (path, name, notifier);
                },
                send:{
                    "Cmd":null,
                    "Term":null
                },
                "listen":{
                    "PostFrom":function(sMessage,oData,sSrc){
                        this.postForm(oData.theForm,oData.term,oData.targetUrl);
                    }
                },
                "postForm":function(theForm,term,targetUrl){
                       //console.log('targetUrl = ' + targetUrl);
                       theForm.attr('action',targetUrl);
                       theForm.attr('method','post');
                       this.send.Cmd({
                            'cmd' : 'Go'
                        });
                           this.send.Term({
                            'term' : term
                        });
                        Portal.requestSubmit();
                },
                'getPortletPath':function(){
                    return this.realpath + '.Entrez_SearchBar';
                }
            });
    
        }//portalSearchBar
        


         //portal javascript is required to make a POST when the rest of the app uses portal forms 
         var usepjs = sbConfig.pjs == "yes"; 
         //console.log('sbConfig',sbConfig);
         initSearchBar(usepjs);
         
         dbNode.on("change",$.ncbi.searchbar.onDbChange);
        
        theForm.on("submit",{'usepjs':usepjs},$.ncbi.searchbar.doSearch);
        theSearchInput.on("ncbiautocompleteenter ncbiautocompleteoptionclick", function(){theForm.submit();});
        //a work around for JSL-2067
        dbNode.trigger("change");
        //iOS 8.02 changed behavior on autofocus, should probably check other mobile devices too
        if (sbConfig.afs == "yes" && !/(iPad|iPhone|iPod)/g.test(navigator.userAgent) ){ 
            window.setTimeout(function(){
                try{
                    var size= originalTerm.length;
                    if (size == 0 || /\s$/.test(originalTerm))
                        theSearchInput.focus()[0].setSelectionRange(size, size);
                    else
                        theSearchInput.focus().val(originalTerm + " ")[0].setSelectionRange(size+1, size+1);
                }
                catch(e){} //setSelectionRange not defined in IE8
            },1);
        }
        
        //set the query changed flag true after a few seconds, still prevents scripted clicking or stuck enter key
        window.setTimeout(function(){$.ncbi.searchbar.setSearchModified();},2000);
         
     });//End of DOM Ready

})(jQuery);

/*
a call back for the 'Turn off' link at the bottom of the auto complete list
*/
function NcbiSearchBarAutoComplCtrl(){
    jQuery("#term").ncbiautocomplete("turnOff",true);
    if (typeof(NcbiSearchBarSaveAutoCompState) == 'function')
        NcbiSearchBarSaveAutoCompState();
 }

 



;
(function ($){
    
    $.fn.waitUntilExists    = function (callback) {
        var selector = this.selector;
        var interval = window.setInterval(function () { 
            var found= $(selector);
            if (found.size() < 1)
            {
                return;
            }
            
            window.clearInterval(interval);
            found.each(callback);
        }, 10);
        
        return $(this.selector);
    }
    
    $('#pubmed_favoritesad').waitUntilExists(function () {
        
        /*JSL-1460: Temporary fix before JIG 1.12 is out*/
        $('#pubmed_favoritesad .ui-ncbisetswitch').addClass('ltd-hover');
        
        //Check if article is favorite
        checkFavStatus();
        
        //When drop-down arrow is clicked
        jQuery("#pubmed_favoritesad .ui-ncbisetswitch-button").live('click',function(){
            //console.log('fav down arrow clicked.');
            var link = this;
            jQuery.ui.jig.requiresLoginURL = "/account/signin/?inlinelogin=true&p$debugoutput=off";
            jQuery.ui.jig.requiresLogin( function(name, requiredLogin ){ 
                LoginCallBack(name, requiredLogin);
                
                //Fetch list of collections
                if(jQuery("#pubmed_favoritesad").hasClass('empty')){
                    try{
                        checkFavStatus();
                        jQuery("div.colloading").show();
                        fetchFavContent(link);
                    }catch(err){
                        console.log(err);
                    }
                }
            });
            
        });
        
        //Event handler for "create collection" link, using "send to" menu
        jQuery("#pubmed_favoritesad .ui-ncbisetswitch-create-collection").on('click', function(){
            jQuery("#dest_AddToCollections").click();
            jQuery("#submenu_AddToCollections .button_apply").click();
        });
        
        //Event handler for click on Favorite/Collection
        jQuery(".collink").on('click', function(event){
            toggleItem(event);
        });
        
        //Event handler repeated - why?
        //for the first click is missed otherwise
        jQuery(".collink").live('click', function(event){
            toggleItem(event);
        });
    });//end initFavorites


    function getAjaxUrl(actionName,IdsFromResult){
        var db = $('#pubmed_favoritesad').data('db') || 'pubmed',
            ajaxUrl = '/pubmed/?p$l=AjaxServer';
            
        ajaxUrl = ajaxUrl + '&p$rq=AjaxServer.DiscoAdC.DiscoSectionCol.Pubmed_FavoritesAdHelper:' + actionName + '&Db='+db;
        return ajaxUrl + (IdsFromResult ? '&IdsFromResult=' + IdsFromResult : '');
    }
    
    function makeAjaxCall(url,data,async){
        async = (typeof async == 'undefined') ? true : async;
        return $.ajax({
            url:url,
            timeout:10000,
            type:'POST',
            dataType:'html',
            async:async,
            data:data
        });
    }
    
    function checkFavStatus(){
        if(($("#myncbiusername").text() != '') && ($("#favList").hasClass('blind'))){
            var ajaxUrl = getAjaxUrl('FetchFav_XHR',$("#absid").val());
            var ajaxCall = makeAjaxCall(ajaxUrl,{},false);
           ajaxCall.done( function(data){
                try{
                    fetchFavResponder(eval('(' + data + ')'));
               }catch(e){
                   console.log(e);
               }
            });//end ajaxCall.done
        }
    }//end chechFavStatus
    
    function fetchFavResponder(JSONobj){
        if((JSONobj.mid == '') || (JSONobj.mid == '0')){
            return; 
        }
        
        if((($("#favList").attr('colid')=== undefined) || ($("#favList").attr('colid') == ''))
        && JSONobj.favid != ''){
            jQuery("#favList").attr('colid', JSONobj.favid);
        }
        
        if((JSONobj.status != undefined) && (JSONobj.status != '')){
            if(JSONobj.status == 'present'){
                jQuery('#favList').html(jQuery('#favList').html().replace('Add to Favorites', 'Favorite'));
                jQuery('#favList span.star').addClass('active');
            }else{
                if(jQuery('#favList').text().indexOf('Add to Favorites') == -1)
                    jQuery('#favList').html(jQuery('#favList').html().replace('Favorite', 'Add to Favorites'));
                jQuery('#favList span.star').removeClass('active');
            }
            jQuery("#favList").removeClass('blind');
        }    
    }//end fetchFavResponder
    
    //callback function for JIG login
    function LoginCallBack(name,requiredLogin){
    }
    
    function fetchFavContent(link){
        var ajaxUrl = getAjaxUrl('Favorites_FetchContent_XHR',$("#absid").val());
        
        function ajaxDoneC(_link){
            return function (data){
                try{
                    fetchFavContentResponder(eval('(' + data + ')'),_link);
               }catch(e){
                   console.log(e);
               }
            }
        }
       
        var ajaxCall = makeAjaxCall(ajaxUrl);
       ajaxCall.done(
          ajaxDoneC(link)
        );//end ajaxCall.done
        
        ajaxCall.always(function(){
           $("div.colloading").hide(); 
        });
        
    }//end fetchFavContent
    
    function fetchFavContentResponder(JSONobj,link){
    try{
        if((JSONobj.mid == '') || (JSONobj.mid == '0')){
	            //alert("Looks like you are not logged in. \nPlease refresh the page and try again.");
	            loginagain();
	            jQuery("div.colloading").hide();
	            jQuery(link).click();
	            return; 
	        }
	        if(JSONobj.content && JSONobj.content != ''){
                jQuery("#favUL").prepend(JSONobj.content);
                jQuery("#pubmed_favoritesad").removeClass('empty');
		    }
		    jQuery("div.colloading").hide();
		    
		    //For favorites collection
	        if((JSONobj.status != undefined) && (JSONobj.status != '')){
	            if(JSONobj.status == 'present'){
	                jQuery('#favList').html(jQuery('#favList').html().replace('Add to Favorites', 'Favorite'));
    	            jQuery('#favList span.star').addClass('active');
    	            jQuery('#favUL li.favorite').addClass('starred');
    	        }else if(JSONobj.status == 'absent'){
    	            if(jQuery('#favList').text().indexOf('Add to Favorites') == -1)
    	                jQuery('#favList').html(jQuery('#favList').html().replace('Favorite', 'Add to Favorites'));
    	            jQuery('#favList span.star').removeClass('active');
    	            jQuery('#favUL li.favorite').removeClass('starred');
    	        }
    	        jQuery("#favList").removeClass('blind');
	        }
	        
	        //JSL-1762 - Add pinger click event for Favorites pull-down
            function starredSet() { 
                var link = jQuery(this); 
                var isBeingSelected = !link.parent().hasClass("starred");
                link.attr("ref", "star=" + isBeingSelected );
            } 
            jQuery("#favUL a").click(starredSet); 
            
	        var theLinks = jQuery("#favUL")[0].getElementsByTagName("a");
            if(typeof ncbi !== "undefined" && typeof ncbi.sg  !== "undefined" && typeof ncbi.sg.scanLinks !== "undefined" ){
                 ncbi.sg.scanLinks( Array.prototype.slice.call(theLinks,0));
            } 
            
        }catch(error){
            console.log(error);
            jQuery("div.colloading").hide();
	    } 
    }//end fetchFavContentResponder
    
    function loginagain(){
        jQuery("#myncbiusername").hide().find("#mnu").text(''); 
	    jQuery("#sign_in").show();
	    jQuery("#sign_out").hide();
    }
    
    function toggleItem(event){
        event.preventDefault();
        //console.log('toggleItem');
        var link = $(event.target);
        var colname = link.text();
        var colid = link.attr('colid');
        if(colid == '') 
            colid = jQuery("#favList").attr('colid');
        jQuery.ui.jig.requiresLoginURL = "/account/signin/?inlinelogin=true&p$debugoutput=off";
        jQuery.ui.jig.requiresLogin( function(name, requiredLogin ){ 
	        LoginCallBack(name, requiredLogin);
	        
            //Fetch list of collections
            checkFavStatus();
            try{
                var ajaxUrl = getAjaxUrl('Toggle_XHR');
                
                var firstAuthor = jQuery("#maincontent .abstract .auths a")[0];
                var title = jQuery("#maincontent .abstract h1")[0];
                
                var ajaxDoneC = (function (_link){
                    return function (data){
                        try{
                            toggleResponder(eval('(' + data + ')'),_link);
                       }catch(e){
                           console.log(e);
                       }
                    }
                })(link);
                
                var ajaxCall = makeAjaxCall(ajaxUrl,{
                        'IdsFromResult' : jQuery("#absid").val(),
                        'Title': jQuery(title).text(),
                        'Author': jQuery(firstAuthor).text(),
                        'Date': jQuery("#absdate").val(),
                        'ColId': colid
                    });
               ajaxCall.done(
                  ajaxDoneC
                );//end ajaxCall.done
                
                ajaxCall.fail(function(){
                    ajaxFailC(link)
                });
                function ajaxFailC(_link){
                    return function(){
                        _link.addClass('collink');
                    }
                }
            }catch(err){
                console.log(err);
                link.addClass('collink');
            }
	    });
        
    }
    
    function toggleResponder(JSONobj, link){
	     try{
	        if((JSONobj.mid == '') || (JSONobj.mid == '0')){
	            //alert("Looks like you are not logged in. \nPlease refresh the page and try again.");
	            link.addClass('collink');
	            loginagain();
	            link.click();
	            return; 
	        }
	        
	        //For favorites collection
	        if((JSONobj.status != undefined) && (JSONobj.status != '') && 
	          (link.attr('colid') == jQuery("#favList").attr('colid'))){
	            if(JSONobj.status == 'added'){
	                jQuery('#favList').html(jQuery('#favList').html().replace('Add to Favorites', 'Favorite'));
    	            jQuery('#favList span.star').addClass('active');
    	            jQuery('#favUL li.favorite').addClass('starred');
    	        }else if(JSONobj.status == 'removed'){
	                if(jQuery('#favList').text().indexOf('Add to Favorites') == -1)
    	                jQuery('#favList').html(jQuery('#favList').html().replace('Favorite', 'Add to Favorites'));
    	            jQuery('#favList span.star').removeClass('active');
    	            jQuery('#favUL li.favorite').removeClass('starred');
    	        }
    	        jQuery("#favList").removeClass('blind');
	        }
	        //For other collections
	        else if (JSONobj.status != ''){
	            if(JSONobj.status == 'added')
    	            link.parent().addClass('starred');
    	        else if(JSONobj.status == 'removed')
    	            link.parent().removeClass('starred');
	        } 
	        //if no status is returned (smth's wrong)
	        else {
	            //console.log("no status returned");
	            //set the star back to original status
	            //if(uargs.colname == 'Favorites'){
	            if(link.text() == 'Favorites'){
    	            if(jQuery('#favList span.star').hasClass('active')){
    	                if(jQuery('#favList').text().indexOf('Add to Favorites') == -1)
        	                jQuery('#favList').html(jQuery('#favList').html().replace('Favorite', 'Add to Favorites'));
    	                jQuery('#favList span.star').removeClass('active');
    	            }else{
    	                jQuery('#favList').html(jQuery('#favList').html().replace('Add to Favorites', 'Favorite'));
    	                jQuery('#favList span.star').addClass('active')
    	            }
    	        }
	        }
		    link.addClass('collink');
	    }catch(error){
	        console.log(error);
	        link.addClass('collink');
	    }
	}

    
})(jQuery);




;
jQuery(function($) {
    $('div.portlet, div.section').each(function() {
        PageSectionInit(this);
    });
});    
    
function PageSectionInit(element) {
    var post_url = '/myncbi/session-state/',
        $ = jQuery,
        self = $(element),
        anchor = self.find('a.portlet_shutter'),
        content = self.find('div.portlet_content, div.sensor_content');

    // we need an id on the body, make one if it doesn't exist already
    // then set toggles attr on anchor to point to body
    var id = content.attr('id') || $.ui.jig._generateId('portlet_content');
    
    // Check if attribute is present
    if (anchor.attr('toggles'))
    {
        // Already initialized
        return;
    }
    
    anchor.attr('toggles', id);
    content.attr('id', id);

    // initialize jig toggler with proper configs, then remove some classes that interfere with 
    // presentation
    var togglerOpen = anchor.hasClass('shutter_closed')  ?  false  :  true; 

    anchor.ncbitoggler({
        isIcon: false,
        initOpen: togglerOpen 
    })
        .removeClass('ui-ncbitoggler-no-icon')
        .removeClass('ui-widget');

    // get rid of ncbitoggler css props that interfere with portlet styling, this is hack
    // we should change how this works for next jig release
    anchor.css('position', 'absolute')
        .css('padding', 0 );

    // trigger an event with the id of the node when closed
    anchor.bind( 'ncbitogglerclose', function() {
        anchor.addClass('shutter_closed');
        
        $.post(post_url, { section_name: anchor.attr('pgsec_name'), new_section_state: 'true' });
    });

    anchor.bind('ncbitoggleropen', function() {
        anchor.removeClass('shutter_closed');
        $.post(post_url, { section_name: anchor.attr('pgsec_name'), new_section_state: 'false' });
    });

    /* Popper for brieflink */
    self.find('li.brieflinkpopper').each( function(){
        var $this = $( this );
        var popper = $this.find('a.brieflinkpopperctrl') ;
        var popnode = $this.find('div.brieflinkpop');
        var popid = popnode.attr('id') || $.ui.jig._generateId('brieflinkpop');
        popnode.attr('id', popid);
        popper.ncbipopper({
            destSelector: "#" + popid,
            destPosition: 'top right', 
            triggerPosition: 'middle left', 
            hasArrow: true, 
            arrowDirection: 'right',
            isTriggerElementCloseClick: false,
            adjustFit: 'none',
            openAnimation: 'none',
            closeAnimation: 'none',
            delayTimeout : 130
        });
    });    
        
} // end each loop

;
(function( $ ){ // pass in $ to self exec anon fn
    // on page ready
    $( function() {
    
        // Initialize popper
        $('li.ralinkpopper').each( function(){
            var $this = $( this );
            var popper = $this;
            var popnode = $this.find('div.ralinkpop');
            var popid = popnode.attr('id') || $.ui.jig._generateId('ralinkpop');
            popnode.attr('id', popid);
            popper.ncbipopper({
                destSelector: "#" + popid,
                destPosition: 'top right', 
                triggerPosition: 'middle left', 
                hasArrow: true, 
                arrowDirection: 'right',
                isTriggerElementCloseClick: false,
                adjustFit: 'none',
                openAnimation: 'none',
                closeAnimation: 'none',
                delayTimeout : 130
            });
        }); // end each loop
        
    });// end on page ready

})( jQuery );


function historyDisplayState(cmd)
{
    var post_url = '/myncbi/session-state/';

    if (cmd == 'ClearHT')
    {
        if (!confirm('Are you sure you want to delete all your saved Recent Activity?'))
        {
            return;
        }
    }

    var ajax_request = jQuery.post(post_url, { history_display_state: cmd })
        .complete(function(jqXHR, textStatus) {    
        
            var htdisplay = jQuery('#HTDisplay');
            var ul = jQuery('#activity');

            if (cmd == 'HTOn') 
            { 
                // so that the following msg will show up
                htdisplay.removeClass();
                
                if (jqXHR.status == 408) 
                { 
                    htdisplay.html("<p class='HTOn'>Your browsing activity is temporarily unavailable.</p>");
                    return;
                }
                
                if (htdisplay.find('#activity li').length > 0)
                {
                    ul.removeClass('hide');    
                }
                else
                {
                    htdisplay.addClass('HTOn');
                }
                
            }         
            else if (cmd == 'HTOff') 
            {                         
                ul.addClass('hide'); 
                htdisplay.removeClass().addClass('HTOff');    // make "Activity recording is turned off." and the turnOn link show up             
            }
            else if (cmd == 'ClearHT') 
            { 
                if (htdisplay.attr('class') == '') 
                {                 
                    htdisplay.addClass('HTOn');  // show "Your browsing activity is empty." message                                  

                    ul.removeClass().addClass('hide'); 
                    ul.html('');
                }
            } 
        });

}


;
/*
  PMCVCitedRefBlocksJS
  
  This code is adapted from the JS that Aaron Cohen wrote, in PPMCArticlePageJS.
  I (cfm) use the term CRB (cited reference block) to refer to the portlets on
  an article page that are aligned with the paragraphs.
  
  This module performs two main functions:
  - Initializes and manages the CRBs, and the links within them.
    These come as div.pmc_para_cit elements from the backend.
  - Initializes and manages the poppers on the links within the
    body of the article (called body links).  There are two types:
      - Body links that have a corresponding CRB link.  These will,
        for the most part, correspond to citations to articles that
        are in PubMed. In these cases, the popper text gets cloned
        from the CRB links.
      - Body links that do not have a corresponding CRB link.  These
        are mostly citations that don't have a corresponding PubMed
        entry.  In these cases, the popper text gets cloned from the
        references section.

  CRB initial state:
  
    The CRBs should all be rendered on the page in their fully-expanded
    states, in the discovery column.  They should appear below any "fixed"
    portlets -- which are portlets of the normal kind, that appear 
    one-after-another at the top of the disco column.  They should have no
    special positioning.

    They should all have the class pmc_para_cit.  In the CSS, we initially
    set the visibility of these to "hidden", to prevent the flash of unstyled
    content.
      
  For reference, here are the jQuery data items that we save with the
  DOM elements:
  
    - CRB (div.pmc_para_cit)
        - myParagraph - reference to the jQuery wrapper object for the
          paragraph corresponding to this CRB.
        - myTop - integer - top of this CRB.  This is constant and is
          set during initialization.  If there's no para corresponding
          to this CRB (edge case), then this will be 0.
        - expandedHeight - int
        - collapsedHeight - int
        - collapsedNumLinks - int
        - isCollapsed - boolean
        - autoCollapseTimerId - int

    - Links in a CRB (div.pmc_para_cit li):
        - myCrb - ref. to the jQuery object for this link's containing CRB.
        - expandedHeight - int
        - myBodyLinks - reference to the jQuery object that holds the
          (one-to-many) body links that correspond to the *same citation*
          as this CRB link.  Note that this is *not* the complement of the
          body link's myCrbLink data member.  Here's the difference.  For
          a body link to have a myCrbLink pointing to this CRB link, it 
          must be in the paragraph corresponding to this CRB.  But, the
          CRB link's myBodyLinks lists *all* of the links in the body,
          regardless of paragraph, that correspond to the same citation.
          
        - isExtra - boolean.
        - isCollapsed - boolean

    - Body links:
        - myCrbLink - reference to the jQuery object for the
          CRB <li> corresponding to this citation link in the body.
        - ncbipopper - reference to the jQuery object for this link's
          popper.
*/

// We use an IIFE in order to not pollute the global namespace.
function CitedRefBlocks(container)
{    
    var $j = jQuery;
    
    // This constant can be set to control the maximum number of
    // links ever to show in a CRB.  But note that this is already 
    // coded in the xslt that generates the portlet on the server.
    // So we probably don't need this.  Anyway, it might be nice to
    // have.  So I'll keep it and set it to a high value.
    var MAX_LINKS_PER_CRB = 50;

    // Specify a time delay before the CRB will "auto-collapse".
    var AUTOCOLLAPSE_TIMEOUT = 4000; 

    // Attach the initialize() function to the window load event.
    // I used to think this was only necessary for Safari, but see 
    // PMC-14368, and this SE post:  
    // http://stackoverflow.com/questions/544993/official-way-to-ask-jquery-wait-for-all-images-to-load-before-executing-somethin
    //$j(window).load(initialize);

    //-------------------------------------------------------------
    // This initialize function runs when the DOM is ready.
    // All the other function definitions are nested inside this one,
    // so that they close over the local variables that are initialized
    // here.
    
    //function initialize() {
        
        // Get the list of all CRBs in the document
        var crbs = $j('div.pmc_para_cit');
        var numCrbs = crbs.length;


        // We need to hide all CRBs that interfere with one of the main 
        // discovery portlets.  We'll assume that these main portlets all 
        // appear at the top.  So we have to find out the bottom-most 
        // boundary of all of these.  This calculation is in a function,
        // because it gets re-computed every time one of those fixed
        // portlets expands or collapses.

        var fixedPortlets = $j('div.portlet').not('div.pmc_para_cit');
        var mainPortletsBottom = getMainPortletsBottom();
        
        // Attach a handler to all of these fixed portlets, that gets activate
        // whenever a shutter button clicks.  Since the shutter button click
        // causes the size to change, we have to re-hide/show CRBs as necessary.
        fixedPortlets.find("a.portlet_shutter")
            .click(fixedPortletShutterClick);

        // These will store the values of the inner and outer height
        // of a 'collapsed' (two_line) link.  But note that since the links
        // are initially in the expanded state, we have to defer grabbing these
        // values until the first time we collapse one of them.  
        // (linkHeight == -1) marks that we haven't gotten the values yet.
        var linkHeight = -1;
        var linkOuterHeight;
        
        // This points to the current expanded CRB, or to null if there isn't one.
        var currentExpandedCrb = null;

        // Set the hoverintent mouseover event handlers for all <li>s.
        // I tweaked sensitivity and interval so that it's not quite so 
        // sensitive -- I think otherwise users are likely to get annoyed.
        crbs.find('li').hoverIntent({
            over: hoverOverCrbLink, 
            out: hoverOutCrbLink,
            sensitivity: 1,
            interval: 150
        });

        // Set a mouse-over event on all CRBs to control an automatic timer.
        // The timer causes the CRB to re-collapse if the user hasn't had her
        // mouse over it for a while.
        crbs.mouseover(clearAutoCollapseTimerHandler);
        crbs.mouseleave(setAutoCollapseTimerHandler);

        // Set up the CRB loop driver.  The CRBs are initialized a few at a time in
        // a loop that's called once a millisecond.  This progressive rendering
        // improves responsiveness when the page first loads.
        
        // This is a pointer into the array of CRBs, that's used by the driver loop.
        var crbNum = 0;
        // How many CRBs to process with each iteration of the driver loop.
        var CRB_BATCH_SIZE = 3;

        // Next add poppers for every link in the body of the text.  This also
        // uses a driver loop.  Set it up here.  
        
        // We're interested in all links that have 'bibr' class, and that
        // have a @rid attribute.
        var allBodyLinks = $j('a.bibr[rid]');
        var numBodyLinks = allBodyLinks.length;
        // This acts as a pointer into the array of links, that's used by the
        // driver loop.
        var bodyLinkNum = 0;
        // How many links to process with each iteration of the driver loop.
        var BODY_LINK_BATCH_SIZE = 10;
        // This is the container div for the poppers that we'll create.  This
        // should be present in the document from the server.
        var blPopperDiv = $j('#body-link-poppers');
        
        // We'll keep track of all the poppers we create, indexed by the @rid
        // value of the link.  That way, we're reuse duplicate poppers.
        var blPoppers = {};

        // The driver loops are chained together.  The order should not matter.
        // At the end of both driver loops, then we set hoverIntent event handlers 
        // on the body links.  This step must be performed last.  That's because 
        // both the ncbipopper (set up by the body link driver loop) and the CRB 
        // functionality (which sets hover events to highlight the text and the 
        // corresponding links in the CRB) use hoverIntent; so the events 
        // conflict.  To fix it, I put calls to the ncbipopper open() and 
        // close() methods at the end of the CRB hover event handlers, thus 
        // chaining the handlers together. 
        crbDriverLoop();


        //-----------------------------------------------------------------
        // Here is the CRB driver loop, which handles a few CRBs, and then
        // queues itself up to execute again after one ms.
        function crbDriverLoop() {
            for (var i = 0; i < CRB_BATCH_SIZE; ++i) {
                if (crbNum >= numCrbs) break;
                positionOneCrb($j(crbs[crbNum]));
                crbNum++;
            }
            // Set up to call ourselves after one millisecond
            if (crbNum < numCrbs) {
                setTimeout(crbDriverLoop, 1);
            }
            // When this driver loop is done, it daisy-chains to the
            // body-link loop
            else {
                setTimeout(bodyLinkDriverLoop, 1);
            }
        };

        //-----------------------------------------------------------------
        // This is a similar driver loop for setting the poppers on all
        // of the body links.
        function bodyLinkDriverLoop() {
            for (var i = 0; i < BODY_LINK_BATCH_SIZE; ++i) {
                if (bodyLinkNum >= numBodyLinks) break;
                addBodyLinkPopper($j(allBodyLinks[bodyLinkNum]));
                bodyLinkNum++;
            }
            // Set up to call ourselves after one millisecond
            if (bodyLinkNum < numBodyLinks) {
                setTimeout(bodyLinkDriverLoop, 1);
            }
            
            // When this driver loop is done, it invokes a function that
            // sets all of the custom hoverIntent handlers on the body links.
            
            // PMC-15007 - Took this out.  It was causing the popper to go away whenever
            // you mouseout of the trigger link.  This was causing the flashing problem
            // described in that ticket.  But worse, it was preventing you from being able
            // to mouse over the popper without the popper going away.
            else {
                //setTimeout(setBodyLinkHoverHandlers, 1);
            }
        }

        //-----------------------------------------------------------------
        // This sets the hoverIntent handlers on all body links.  As mentioned
        // above, this must be done last.
        // PMC-15007 - this is not called.  See above.
        function setBodyLinkHoverHandlers() {
            $j('a.bibr[rid]')
                .hoverIntent({
                    over: hoverOverBodyLink, 
                    out: hoverOutBodyLink,
                    sensitivity: 1,
                    interval: 150
                });
        }

        //-----------------------------------------------------------------
        // This function absolutely positions one of the CRBs.  For progressive-
        // rendering, this gets called from the driver loop above.
        function positionOneCrb(jcrb)
        {
            // Get the paragraph to which this CRB corresponds
            var rid = jcrb.attr('rid');
            var p = $j('#' + rid);
            // If there is no paragraph, just hide the CRB and return
            if (p.length != 1) {
                jcrb.hide();
                jcrb.data('myTop', 0);
                return;
            }
            // Record this paragraph
            jcrb.data('myParagraph', p);


            // We'll compute the "visual top", which takes into account the
            // reported top, the top margin, and a fudge factor.
            var myTop = parseInt(p.position().top) + parseInt(p.css('marginTop')) - 7;
            jcrb.data('myTop', myTop);
            
            // Do some work for each link within this CRB
            var crbLinks = jcrb.find('li');
            crbLinks.each(function() {
                var li = $j(this);

                // Get the expanded heights of each of the <li>s.
                var h = li.height();


                // Find the matching links in the body (might be several)
                var referenceId = li.attr('reference_id');
                var bodyLinks = p.find('a.bibr[rid="' + referenceId + '"]');
                
                // Set a data pointer from the body links back to this CRB link
                bodyLinks.data('myCrbLink', li);
                
                // Now find myBodyLinks.  Note that this is *not* the same as the
                // bodyLinks above.  Here's the difference.  For
                // a body link to have a myCrbLink pointing to this CRB link, it 
                // must be in the paragraph corresponding to this CRB.  But, the
                // CRB link's myBodyLinks lists *all* of the links in the body,
                // regardless of paragraph, that correspond to the same citation.
                var myBodyLinks = $j('a.bibr[rid="' + referenceId + '"]');

                // Store these data in the CRB link
                li.data({
                    'myCrb': jcrb,   // reference from link back to containing CRB
                    'expandedHeight': h,
                    'myBodyLinks': myBodyLinks
                }); 
            });

            // Now collapse the CRB into its default resting state
            
            // First collapse each of the <li>s by adding the 'two_line' class.
            crbLinks.each(function() {
                var li = $j(this);
                li.removeClass('expanded')
                  .removeClass('highlight')
                  .addClass('two_line');
                li.data('isCollapsed', true);
                
                // If this is the first-ever 'two_line' link that we've seen, 
                // then record its heights
                if (linkHeight == -1) {
                    linkHeight = li.height();
                    linkOuterHeight = li.outerHeight(true);
                }
            });

            // Get the height of the paragraph.  This gives the maximum height
            // of the 'collapsed' CRB.  In other words, in the collapsed state,
            // the CRB should not extend below the bottom of the para.
            var pHeight = p.height();

            // The number of links in this CRB, as delivered from the server.
            var numLinks = crbLinks.length;

            // Calculate how many links will fit on this CRB, according to the
            // height of the paragraph.
            // Note that this is a little bit tricky.  When we figure out whether
            // or not we need to hide links, and, as a consequence, add the "see more"
            // link, then we *do not* take the height of the "see more" link into
            // account.  But, once we know that we need to hide links, and thus add
            // the "see more" link, then we need to take the height of that link into
            // account to figure out *how many links to hide*.
            var linksFit = Math.floor( pHeight / linkOuterHeight );

            // Maximum number of links to show here is based either on policy
            // (MAX_LINKS_PER_CRB) or on the number that will fit.
            var maxLinks = Math.min(MAX_LINKS_PER_CRB, linksFit);
            
            // See if we need to hide some.
            if (numLinks > maxLinks) {
                // We need to take off some links.  But first, let's add the "more"
                // link, and measure the total expanded height.

                // Add the "more" link.  This gets appended as the next sibling of
                // the <ul>.  Measure the height before and after, so we know how
                // much height this link contributes.
                var heightBefore = jcrb.height();

                var moreLink = $j("<a href='' class='seemore'>See more ...</a>");
                jcrb.find('div.portlet_content').append(moreLink);
                
                // Add the event handler.
                moreLink.click(moreLinkClick);
                
                // Measure the expanded height
                var expandedHeight = jcrb.height();
                
                // Figure out how much the "see more" link added
                var moreLinkHeight = jcrb.height() - heightBefore;
                
                // Based on this new information, figure out how many links we will
                // show (never go below 0).
                var linksToShow = 
                    Math.max(0, Math.floor( (pHeight - moreLinkHeight) / linkOuterHeight ));

                // Now hide the excess links.  For each, record that it is an extra.
                for (var i = linksToShow; i < numLinks; i++) {
                    $j(crbLinks[i])
                        .hide()
                        .data('isExtra', true);
                }

                // If we're showing no links, change "See more ..." to "See links ..."
                if (linksToShow <= 0) moreLink.text("See links ...");

                // Measure the height again and save as collapsedHeight
                var collapsedHeight = jcrb.height();

                // Now store a bunch of this data with the CRB DOM object
                jcrb.data({
                    'expandedHeight': expandedHeight,
                    'collapsedHeight': collapsedHeight,
                    'collapsedNumLinks': linksToShow
                });
            }

            // Whether or not we need to hide any links, initialize
            // the isCollapsed flag, and the autoCollapseTimerId.
            jcrb.data({
                'isCollapsed': true,
                'autoCollapseTimerId': -1
            });

            // Capture the width prior to repositioning.  Since we're changing
            // from position-static to position-absolute, we'll need to set
            // this to a fixed value.
            var width = jcrb.css('width');

            // The final thing we do is to position it next to the para,
            // and make it visible.
            jcrb.css( {
                'position': 'absolute',
                'visibility': 'visible',
                'width': width,
                'top': myTop 
            });

            // If it would interfere with one of the fixed portlets, hide it.
            if (myTop <= mainPortletsBottom) jcrb.hide();
        }

        //-----------------------------------------------------------------
        // This function handles the mouseover event when the user hovers 
        // over one of the CRB links items.
        function hoverOverCrbLink(event) {
            //console.info("hoverOverCrbLink");
            var link = $j(this);
            // Call expandLink with checkHidden false - we know its not 
            // hidden, because the user has his mouse over it.
            expandLink(link, false);
        }

        //-----------------------------------------------------------------
        // This gets called to highlight a particular link in a CRB.
        // It checkHidden is true, then this first checks to see if this
        // link's CRB is collapsed, and this link is hidden.  If so, then
        // this first expands the CRB.  
        // [Note that the 'checkHidden' feature is not used.  We originally
        // implemented this so that if the user hovers over a body link
        // corresponding to an "extra" CRB link, then that would cause the
        // CRB to expand to show it.  But David didn't like so much animation
        // going on in the disco column while the user is moving his mouse
        // around over the body.  Even though it's not used, I left the code in.]
        
        function expandLink(link, checkHidden) {
            //console.info("expandLink");
            var jcrb = link.data('myCrb');
            jcrb.addClass("stretched");
            // Set the z-index.  This ensures that when the CRBs are expanded, they
            // are layered on top of ones that are collapsed.
            jcrb.css('z-index', 1);
            
            // Enforce the policy that only one CRB is stretched at a time.
            collapseOtherCrbs(jcrb);
            
            // See if we need to expand the whole CRB (equivalent to "see more").
            if ( checkHidden && 
                 link.data('isExtra') &&
                 jcrb.data('isCollapsed') )
            {
                expandCrb(jcrb);
            }
            
            var h = link.data('expandedHeight');
            link.data('isCollapsed', false);

            // Animate the height change.  Whenever we do this, we have
            // to specify the exact numeric value of the final height.
            // When done, we set the CSS property back to 'auto'.
            link.animate(
                {'height': h},
                { 'complete': function() {
                    jcrb.css({height: "auto"});
                  },
                  'duration': 'fast'
                }
            );
            
            // Do this *after* kicking off the animation, because this is
            // what causes the actual height of the link to change.
            link.removeClass('two_line')
                .addClass('expanded');
            
            // This causes the link in the CRB, and all its corresponding
            // links in the body, to be highlighted with a special color.
            highlightLink(link);
        }


        //-----------------------------------------------------------------
        // This function handles the event when the user moves the mouse 
        // out of the <li> items.
        function hoverOutCrbLink(event) {
            //console.info("hoverOutCrbLink");
            var link = $j(this);
            unexpandLink(link);
        }

        //-----------------------------------------------------------------
        function unexpandLink(link) {
            //console.info("unexpandLink");
            var jcrb = link.data('myCrb');

            link.removeClass('expanded')
                .addClass('two_line');
            // Remove the highlight color from the link in the CRB and
            // all the corresponding links in the body.
            unhighlightLink(link);
            
            link.animate(
                {'height': linkHeight},
                { 'complete': function() {
                      link.data('isCollapsed', true);
                      // Check if we still need the 'stretched' class on the 
                      // CRB parent.
                      checkStretched(jcrb);
                      // Reset the height property to auto.
                      jcrb.css({height: "auto"});
                      
                  },
                  'duration': 'fast'
                }
            );
        }
        
        //-----------------------------------------------------------------
        // This function handles the hovering over a body link.  Note that
        // some of these will have corresponding CRB links, and some will
        // not.
        function hoverOverBodyLink(event) {
            //console.info("hoverOverBodyLink");
            var bodyLink = $j(this);

          /* PMC-15150 - reduce "christmas tree effect", don't highlight
            CRB when user hovers over body link.
            
            var crbLink = bodyLink.data('myCrbLink');
            if (crbLink) {
                highlightLink(crbLink);
                var jcrb = crbLink.data('myCrb');
                clearAutoCollapseTimer(jcrb);
            }
          */
            
            // If there's a popper associated with this, open it.
            // Both this and JIG's ncbipopper use hoverIntent, so we have
            // to chain these events together.
            var popper = bodyLink.data('ncbipopper');
            if (popper) popper.open();
        }

        //-----------------------------------------------------------------
        function hoverOutBodyLink(event) {
            //console.info("hoverOutBodyLink");
            var bodyLink = $j(this);
            var crbLink = bodyLink.data('myCrbLink');
            if (crbLink) {
                unhighlightLink(crbLink);
                var jcrb = crbLink.data('myCrb');
                setAutoCollapseTimer(jcrb);
            }
            
            // If there's a popper associated with this, close it
            var popper = bodyLink.data('ncbipopper');
            if (popper) popper.close();
        }

        //-----------------------------------------------------------------
        // This function highlights a CRB link, and all of the body
        // links that correspond to it.
        function highlightLink(link) {
            //console.info("highlightLink");
            link.addClass('highlight');
            link.data('myBodyLinks').addClass('highlight');
        }

        //-----------------------------------------------------------------
        // This function unhighlights a CRB link, and all of the body links
        // that correspond to it.
        function unhighlightLink(link) {
            //console.info("unhighlightLink");
            link.removeClass('highlight');
            link.data('myBodyLinks').removeClass('highlight');
        }

        //-----------------------------------------------------------------
        // This function removes, when necessary, the 'stretched' class on 
        // the CRB object.  If the jcrb isCollapsed is true, and all of
        // the links' isCollapsed are true, then clear this class.  Note 
        // that we don't check whether or not to *set* the class - that is 
        // done instantly whenever any of those things starts to expand.
        function checkStretched(jcrb) {
            //console.info("checkStretched");
            if (!jcrb.data('isCollapsed')) return;
            
            var hasExpandedLink = false;
            jcrb.find('li').each(function() {
                if (!$j(this).data('isCollapsed')) hasExpandedLink = true;
            });
            if (hasExpandedLink) return;
            
            jcrb.removeClass('stretched');
            jcrb.css('z-index', 0);
        }
        
        //-----------------------------------------------------------------
        // Click handler for the "see more" link at the bottom of the portlet.
        // Note that this might be either a "see more" or a "see less" click.
        function moreLinkClick(event) {
            //console.info("moreLinkClick");
            var moreLink = $j(this);
            var jcrb = moreLink.parents('div.pmc_para_cit');

            // If we're collapsed, then we need to expand
            if (jcrb.data('isCollapsed')) {
                expandCrb(jcrb);
            }
            else {
                collapseCrb(jcrb);
            }

            // Override the default action
            return false;
        }
        
        //-----------------------------------------------------------------
        // This function animates the expansion of a CRB to show all of the
        // links.  We will never call this unless this is a collapsible CRB.
        // (In other words, if all the links fit within the height of the
        // paragraph, then we'll guarantee that we'll never call this 
        // function.)
        
        function expandCrb(jcrb) {
            //console.info("expandCrb");
            
            // Make sure this CRB is now on top
            collapseOtherCrbs(jcrb);

            // Update the state variable
            jcrb.data('isCollapsed', false);
            currentExpandedCrb = jcrb;
        
            // Add the 'stretched' class to the outer div
            jcrb.addClass("stretched");
            jcrb.css('z-index', 1);
            
            // Change the label on the "more" link
            jcrb.find('.seemore').text("See less ...");
            
            // Animate the height change.
            var d = jcrb.data();
            jcrb.animate(
                {'height': d.expandedHeight},
                { 'complete': function() {
                      jcrb.css({height: "auto"});
                  },
                  'duration': 'fast'
                }
            );

            // Show all the links.  This is done *after* we kick off
            // the animation because this is the step that causes 
            // the actual height to change.
            var crbLinks = jcrb.find('ul li.two_line');
            var totalNumLinks = crbLinks.length;
            for (var i = d.collapsedNumLinks; i < totalNumLinks; ++i) {
                $j(crbLinks[i]).show();
            }
        }
        
        //-----------------------------------------------------------------
        // This function animates the collapse of the CRB into it's default 
        // resting state, including ensuring that all child links are in 
        // their two_line, collapsed state.  This gets called from two 
        // places: when the user clicks on "see less", and when the 
        // auto-collapse timer triggers.
        
        function collapseCrb(jcrb) {
            //console.info("collapseCrb");
            
            var d = jcrb.data();

            // Change the label on the link
            var linkText = d.collapsedNumLinks > 0 ? "See more ..." : "See links ...";
            jcrb.find('.seemore').text(linkText);

            // Get the link children
            var crbLinks = jcrb.find('ul li');
            var totalNumLinks = crbLinks.length;

            // Animate the height change.  We use the 'complete' option of 
            // the animation function to hide all of the excess links after
            // the animation is done.  If we hid them all right away, the 
            // height would change abruptly (no animation).
            jcrb.animate(
                { 'height': d.collapsedHeight },
                { 'complete': function() {
                      // For all links
                      crbLinks.each(function() {
                          var li = $j(this);
                          
                          // Put the link into its collapsed state
                          li.removeClass('expanded')
                            .removeClass('highlight')
                            .addClass('two_line');
                          li.data('isCollapsed', true);

                          // Hide 'overflow' links
                          if (li.data('isExtra')) li.hide();
                      });
                      
                      // Now put the CRB object itself into the collapsed state
                      jcrb.data('isCollapsed', true);
                      jcrb.removeClass('stretched');
                      jcrb.css('z-index', 0);
                      
                      // Reset the height property to auto.
                      jcrb.css({height: "auto"});
                  },
                  'duration': 'fast'
                }
            );
            
            currentExpandedCrb = null;
        }

        //-----------------------------------------------------------------
        // This function sets a timer on a CRB object so that it will
        // reclose after a fixed period of time after the last time that
        // the user has moved his/her mouse out of the div.  This is set 
        // up as a handler for mouseleave events.  Note that it the CRB 
        // is already collapsed, this does nothing.

        // Handler for the mouse-out event for the whole CRB div.
        function setAutoCollapseTimerHandler(event) {
            //console.info("setAutoCollapseTimerHandler");
            setAutoCollapseTimer($j(this));
        }
        
        // This does the work.  It is also called from the handler for 
        // the mouse-out event on a corresponding body link.
        function setAutoCollapseTimer(jcrb) {        
            //console.info("setAutoCollapseTimer");
            if (jcrb.data('isCollapsed')) return;
            
            // Set the timer
            var timerId = window.setTimeout(function() { 
                collapseCrb(jcrb); 
            }, AUTOCOLLAPSE_TIMEOUT);
            
            // Record it as a data attribute on this object
            jcrb.data('autoCollapseTimerId', timerId);
        }

        //-----------------------------------------------------------------
        // This function clears the auto-collapse timer.  It is set up as
        // a handler for the mouseover event.
        
        // Handler for the mouse-over event for the whole CRB div.
        function clearAutoCollapseTimerHandler(event) {
            //console.info("clearAutoCollapseTimerHandler");
            clearAutoCollapseTimer($j(this));
        }
        
        // This does the work.  It is also called from the handler for 
        // the mouse-over event on a corresponding body tag.
        function clearAutoCollapseTimer(jcrb) {
            //console.info("clearAutoCollapseTimer");
            var timerId = jcrb.data('autoCollapseTimerId');
            if (timerId == -1) return;
            
            window.clearTimeout(timerId);
            jcrb.data('autoCollapseTimerId', -1);
        }

        //-----------------------------------------------------------------
        // This function is used to collapse all of the *other* CRBs.
        // It is invoked whenever we highlight a link or expand a CRB.
        // This makes sure that the focus is always on only one at a time.
        function collapseOtherCrbs(jcrb) {
            //var cstr = (currentExpandedCrb) ?
            //    (", currentExpandedCrb = " + currentExpandedCrb.attr('id')) :
            //    "";
            //console.info("collapseOtherCrbs; jcrb = " + jcrb.attr('id') + cstr);
            
            /* This used to loop through all of the CRBs, collapsing all of
              them except myId.  But now I just keep track of the (at most
              one) CRB that's currently expanded, and collapse that. 
            var myId = jcrb.attr('id');

            crbs.each(function() {
                var thisCrb = $j(this);
                if (thisCrb.attr('id') != myId) {
                    collapseCrb(thisCrb);
                }
            });
            */
            //console.info("Checking, currentExpandedCrb = " + currentExpandedCrb);
            if (currentExpandedCrb && currentExpandedCrb.attr('id') != jcrb.attr('id')) {
                collapseCrb(currentExpandedCrb);
            }
        }

        //-----------------------------------------------------------------
        // This function is set as an event handler when the user clicks
        // on any of the shutter buttons on any of the fixed portlets at the
        // top.  When these fixed portlets change size, we have to go
        // through all the CRBs again and hide/show depending on whether
        // or not they are interfering.
        // But, because the portlet size change is animated, the new size
        // won't be known for a while, so this in turn sets a timer that
        // invokes hideInterfering().
        
        function fixedPortletShutterClick(event) {
            setTimeout(hideInterfering, 200);
        }
        
        //-----------------------------------------------------------------
        // hideInterfering iterates through all of the CRBs and hides any
        // that would interfere with any of the fixed portlets at the top.
        // It is called every time the user clicks a shutter button on one 
        // of the fixed portlets.
        
        function hideInterfering() {
            var mainPortletsBottom = getMainPortletsBottom();
            crbs.each(function() {
                var jcrb = $j(this);
                if (jcrb.data('myTop') <= mainPortletsBottom) {
                    jcrb.hide();
                }
                else {
                    jcrb.show();
                }
            });
        }

        //-----------------------------------------------------------------
        // This function gets the y-coordinate of the bottom of the lowest
        // of the fixed portlets.
        
        function getMainPortletsBottom() {
            var bottom = 0;
            fixedPortlets.each(function() {
                var p = $j(this);
                var top = parseInt(p.position().top) + parseInt(p.css('marginTop'));
                var thisBottom = top + p.height();
                bottom = Math.max(bottom, thisBottom);
            });
            return bottom;
        }
        
        //-----------------------------------------------------------------
        // This function adds a popper to one of the links in the body.
        // It is called by the driver loop above.  The link is guaranteed
        // to have the 'bibr' class, and a @rid attribute.
        var popperCount = 0;
        function addBodyLinkPopper(link) {
            // If we never found a container for our poppers in the source
            // document, then we can't do anything.
            if (blPopperDiv.length < 1) return;
            
            var rid = link.attr('rid');
            // Some id's from the backend have special characters, so we
            // need to escape them whenever they're used as jQuery selectors.
            // See PMC-6384 and http://tinyurl.com/2qfqgc.
            var ridEscaped = rid.replace(/:/g, "\\:")
                                .replace(/\./g, "\\.")
                                .replace(/·/g, "\\·");

            var popperId = "body-link-popper-" + rid; // + "-" + popperCount;
            var popperIdEscaped = "body-link-popper-" + ridEscaped; // + "-" + popperCount;
            popperCount++

            // If we've already made a popper for this particular reference,
            // let's use that.
            var popper = blPoppers[rid];
            
            // Otherwise, we need to make one.
            if (!popper) {
                //console.info("Adding pooper for body link, rid = " + rid);
                
                popper = $j("<div/>", { 
                    'id': popperId,
                    'class': 'body-link-popper',
                    'style': 'display: none'
                });
                
                // If this link has a corresponding CRB link, then we'll
                // use that for the popper text
                var myCrbLink = link.data('myCrbLink');
                if (myCrbLink) {
                    // Get the popper text from the CRB link
                    //console.info("Got a CRB link, rid = " + rid);
                    popper.append(myCrbLink.children("a").contents().clone());
                    popper.append(myCrbLink.children(".alt-note").children().clone());
                    
                    // Find the pubmed link, if exists
                    var $pmidLink = myCrbLink.find("a[href *= 'pubmed']");
                    //console.info("myCrbLink = %o", myCrbLink);
                    //console.info("pmidLink = %o", $pmidLink);
                    var pubmedLink = $pmidLink.length > 0
                        ? "[<a href='" + $pmidLink.attr('href') + "'>PubMed</a>] "
                        : "";
                    popper.append("<p>" + pubmedLink + "[" + 
                        "<a href='" + link.attr("href") + "'>Ref list</a>]</p>");
                }
                
                // Otherwise we'll copy the text from the references section.
                else {
                    // Find the text for this popup from the element pointed to by 
                    // @rid.  This will be in the reference section of the article.
                    //console.info("Not a CRB link, rid = " + rid);
                    var refElem = $j('#' + ridEscaped);
                    
                    // Check to make sure that we found something
                    if (refElem.length > 0) {
    
                        var citeText = refElem.html();
                        var popText = $j.trim(citeText);
        
                        // If the @href element of the current <a> tag (currElem)
                        // has a '#' portion, meaning that it is a link to the
                        // reference list in this same article, then indicate 
                        // that in the popup text.
                        if (link.attr("href").charAt(0) == '#') {
                            popText += ' [<a href="' + link.attr("href") + '">Ref list</a>]';
                        }
                    }
                    popper.append(popText);
                }
                
                // Put this new popper into the container div.
                blPopperDiv.append(popper);
                
                // And record it for posterity.
                blPoppers[rid] = popper;
            }
            
            // FIXME:
            // It would be nice if I could pass the configuration parameters
            // to JIG as a JS object; but it doesn't work.
            //var popperConfig = {
            //    'destSelector': ('#' + popperId) 
            //};
            // Note that I have to set a fixed width here.  "auto" doesn't work.
            // Nor does setting it in the CSS file.
            
            // FIXME:  This is a little debug feature that lets you enable the
            // popper's autoAdjust feature.  Because of JSL-1519, I have it
            // turned off by default.
            var loc = window.location.href;
            var qs = loc.substring(loc.indexOf("?") + 1);
            var qsParams = qs.split(/&/);
            var numQsParams = qsParams.length;
            var gotAutoAdjust = false;
            for (var i = 0; i < numQsParams; ++i) {
                if (qsParams[i] == "__autoadjust") gotAutoAdjust = true;
            }

            gotAutoAdjust = true;
            var adjustFitStr = gotAutoAdjust ? 'autoAdjust' : 'none';

            link.ncbipopper({ 
                destSelector: "#" + popperIdEscaped,
                isTriggerElementCloseClick: false,
                hasArrow: true, 
                width: "30em", 
                adjustFit: adjustFitStr,
                triggerPosition: "top right"
            });
        }
    //} /* end of initialize() */
}


;
jQuery(function($) {
    DiscoveryColumnAjaxLoader('/pmc/discovery/', '#ajax-portlets');    
});

function DiscoveryColumnAjaxLoader(url, target)
{
    var $ = jQuery,
        loading_indicator = '/portal/portal3rc.fcgi/4018218/img/3631476',
        container = $(target);
        
    container
        .html('<img src="'+loading_indicator+'" align="absmiddle" alt="Loading..."/> Loading portlets...')
        .load(url, container.data(), function(response, status, xhr) {

            if (status == "error") 
            {
                container.html("");
                return;
            }
            
            // Once loaded
            
            container.find('div.portlet').each(function() {
                PageSectionInit(this);
            });
            
            jQuery.ui.jig.scan(this);
            
            // @TODO make sections collapsible
            
            CitedRefBlocks();
            
            
        });   
            
}

