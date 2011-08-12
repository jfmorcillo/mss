/*
    (c) 2010 Mandriva, http://www.mandriva.com/

    $Id$

    This file is part of Mandriva Server Setup

    MSS is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    MSS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MSS; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
    MA 02110-1301, USA.
*/

var popupRequest = false;

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
    setTimeout('updateStatus(true)', '500');


    // show popup for elem
    // elem should have the "pop" or "popx" class
    // class popw make the popup dragable
    // popup text or method is stored in the alt attribute
    // popup title is stored in the title attribute
    $$(".pop", ".popx").each(function(elem){
        if(elem.readAttribute('alt')) {
            $(elem).observe('mouseover', function(evt) {

                // reset the popup contents
                $("popup").update("");
                // remove CSS classes
                resetPopupStyle();

                // abort on-going ajax call for popup
                if (popupRequest) {
                    popupRequest.abort();
                }

                // apply some popup magic style
                if ($(elem).hasClassName("error")) {
                    $("popup").addClassName("poperr");
                }
                else {
                    $("popup").addClassName("pop");
                }

                // add close button to popup
                // if we want a window popup
                if(elem.hasClassName("popw")) {
                    var a = new Element('img',
                        { src: '/site_media/img/close.png', class: 'close',
                          title: 'Close' });
                    a.observe('click', function(evt) {
                        $('popup').hide();
                        resetPopupStyle();
                    });
                    $("popup").appendChild(a)
                }

                // set up the popup contents
                var title = new Element('h1', { 'id': 'poptitle' });
                $("popup").appendChild(title)
                var content = new Element('div', { 'id': 'popcontent' });
                $("popup").appendChild(content)

                // simple text popup in alt
                if(elem.hasClassName("pop")) {
                    content.update(elem.readAttribute('alt'));
                }
                // execute ajax method specified in alt attr
                else if(elem.hasClassName("popx")) {
                    eval(elem.readAttribute('alt').toString());
                }

                // setup the popup title
                if (elem.readAttribute('title')) {
                    title.update(elem.readAttribute('title'));
                    // class popw make the popup draggable
                    if(elem.hasClassName("popw")) {
                        new Draggable('popup', { handle: 'poptitle' });
                    }
                }
                else {
                    title.hide();
                }

                // first popup placement
                $("popup").style.top = evt.clientY+window.scrollY+"px";
                rightOffset = $("popup").getOffsetParent().getWidth() - evt.clientX;
                if(rightOffset < 180) {
                    $("popup").style.left = evt.clientX - 180;
                }
                else {
                    $("popup").style.left = evt.clientX+"px";
                }
                // let's see the popup
                $("popup").show();
            });
            // don't hide or move popup
            // if it is a windows popup
            if(!elem.hasClassName("popw")) {
                $(elem).observe('mouseout', function() {
                    $("popup").hide();
                    resetPopupStyle();
                });
                $(elem).observe('mousemove', function(evt) {
                    $("popup").style.top = evt.clientY+window.scrollY+"px";
                    rightOffset = $("popup").getOffsetParent().getWidth() - evt.clientX;
                    if(rightOffset < 180) {
                        $("popup").style.left = evt.clientX - 180;
                    }
                    else {
                        $("popup").style.left = evt.clientX+"px";
                    }
                });
            }
        }
    });


});

resetPopupStyle = function() {
    // remove CSS classes
    $("popup").classNames().each(function(cls) {
        $("popup").removeClassName(cls);
    });
}

setLang = function(lang, url) {
    window.location = "/mss/lang/"+lang+"/?url="+url;
}

scrollLog = function() {
    $$('.log').each(function(i){ i.scrollTop = i.scrollHeight });
}

formatLog = function(JSONoutput) {
    output = "";
    for (i=0; i<JSONoutput.length; i++) {
        code = JSONoutput[i].code;
        text = JSONoutput[i].text;
        css="";
        if (code == 1)
            css="warning";
        else if(code == 2)
            css="error";
        else if(code == 7)
            css="info";
        else if(code == 8)
            css="info";
        output += '<span class="'+css+'">'+text+'</span>';
    }
    return output;
}
