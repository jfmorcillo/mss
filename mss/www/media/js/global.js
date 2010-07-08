Event.observe(window, 'load', function() {
    // back function for back button
    if ($("back")) {
        $("back").observe('click', function() {
            history.back();
        });
    }
    // disable all input field for elem with class "disabled"
    $$(".disabled input").each(function(i){ i.disabled = true; });
    
    // start the status bar
    //setTimeout('updateStatus(true)', '500');
    
    // show popup for elem
    // elem should have the "pop" class
    // popup text is stored in the alt attribute
    $$(".pop").each(function(elem){
        if(elem.readAttribute('alt')) {
            $(elem).observe('mouseover', function(evt) {
                if ($(elem).hasClassName("error")) {
                    $("popup").addClassName("poperr");
                }
                else {
                    $("popup").addClassName("pop");
                }
                $("popup").update(elem.readAttribute('alt'));
                $("popup").style.left = evt.clientX+"px";
                $("popup").style.top = evt.clientY+window.scrollY+"px";
                $("popup").show();
            });
            $(elem).observe('mouseout', function() {
                $("popup").hide();
                $("popup").removeClassName("poperr");
                $("popup").removeClassName("pop");
            });
            $(elem).observe('mousemove', function(evt) {
                $("popup").style.left = evt.clientX+"px";
                $("popup").style.top = evt.clientY+window.scrollY+"px";
            });
        }
    });
});

setLang = function(lang, url) {
    window.location = "/mss/lang/"+lang+"/?url="+url;
}

