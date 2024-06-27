from xhtml2pdf import pisa
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
import os
import logging  #noqa


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    if uri.startswith(settings.STATIC_URL):
        # Remove the STATIC_URL prefix from the URI
        uri_path = uri[len(settings.STATIC_URL):]
        
        # Use Django finders to locate the static file
        absolute_path = finders.find(uri_path)
        
        if absolute_path:
            # Check if the path is within the allowed static directory
            base_static_dir = os.path.realpath(settings.STATICFILES_DIRS[0])
            resolved_path = os.path.realpath(absolute_path)
            
            if resolved_path.startswith(base_static_dir):
                return resolved_path

    return None


# Generic pdf response populator. Takes a report title, a report template,
# and a dictionary of kwargs to pass to the template.
def populate_pdf_response(*, report_title, report_template, **kwargs):
  response = HttpResponse(content_type="application/pdf")
  response[
      "Content-Disposition"] = f'attachment; filename="{report_title}.pdf"'
  template_path = os.path.join(settings.BASE_DIR, report_template)
  
  html = render_to_string(
      template_path,
      {
          "title": report_title,
          "BASE_DIR": settings.BASE_DIR,
          **kwargs,
      },
  )
  pisa.CreatePDF(html, dest=response, link_callback=link_callback)
  return response

