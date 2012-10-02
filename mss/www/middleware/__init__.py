import traceback

from django.http import HttpResponse
from django.utils.html import escape

class CatchAjaxException(object):

    def process_exception(self, request, exception):
        if request.is_ajax():
            url = request.META['REQUEST_URI']
            error = """
	    var modal = $('<div>', { class: "modal hide fade" });
	    var modal_header = $('<div>', { class: "modal-header" });
	    var modal_title = $('<h3>');
	    var modal_body = $('<div>', { class: "modal-body" });
	    var modal_message = $('<pre>');
	    var modal_footer = $('<div>', { class: "modal-footer" });
	    var modal_close = $('<a>', { href: "#" });

	    modal_title.html("Error while calling %s");
	    modal_message.html("%s");
	    modal_close.html("Close");

	    modal_body.append(modal_message);
	    modal_header.append(modal_title);
	    modal_close.data("dismiss", "modal");
	    modal_footer.append(modal_close);
	    modal.append(modal_header);
	    modal.append(modal_body);
	    modal.append(modal_footer);

	    $(modal).modal('show');
            """ % (url, escape(traceback.format_exc()).replace('\n', '\\n'))

            return HttpResponse(error, mimetype="application/javascript")
