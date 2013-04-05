/*
    (c) 2010-2012 Mandriva, http://www.mandriva.com/

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

$(document).ready(function() {
    // start the status bar
    setTimeout('updateStatus(true)', '500');

    // links with the disabled CSS class
    // are really disabled :o
    $('a.disabled').click(function(ev) {
        if ($(this).hasClass("disabled")) {
            ev.preventDefault();
            return false;
        }
    });
});

setLang = function(lang) {
    window.location = "/mss/lang/"+lang+"/";
}

scrollLog = function() {
    $('.log').each(function(i){ this.scrollTop = this.scrollHeight });
}

formatLog = function(JSONoutput) {
    output = "";
    if (JSONoutput) {
        for (i=0; i<JSONoutput.length; i++) {
            code = JSONoutput[i].code;
            text = JSONoutput[i].text;
            css = "";
            if (code == 1)
                css = "warning";
            else if(code == 2)
                css = "error";
            else if(code == 7)
                css = "info";
            else if(code == 8) {
                css = "info";
                text = "<strong>" + text + "</strong>";
            }
            output += '<span class="'+css+'">' + text + '</span>';
        }
    }
    return output;
}

isInt = function(someNumber) {
    var intRegex = /^\d+$/;
    if(intRegex.test(someNumber))
        return true;
    else
        return false;
}

String.prototype.format = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};
