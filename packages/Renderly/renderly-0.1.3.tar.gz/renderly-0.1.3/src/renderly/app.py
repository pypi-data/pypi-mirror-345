import os
import json

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from request import Request
from response import Response

class App:

    def __init__(self, name="", project_dir="/templates", _404_template="404.template", app_context=None):
        self.name = name
        self.project_dir = project_dir
        self._404_template = _404_template

        self.template_lookup = TemplateLookup(directories=[project_dir])

        if isinstance(app_context, dict):
            self.app_context(app_context)
        elif isinstance(app_context, str):
            with open(app_context, 'r') as context_file:
                self.jina_env.app_context.update(json.load(context_file))
        else:
            self.app_context = {}

    def __call__(self, environ, start_response):
        """
        Handle Request
        """

        request = Request(environ)
        response = Response()

        if request.path == "/":
            request.path = "/index.template"
        elif not request.path.endswith(".template"):
            request.path += ".template"
        
        try:
            template = self.template_lookup.get_template(request.path)
        except TopLevelLookupException as e:
            template = self.template_lookup.get_template(self._404_template)

        context = dict(self.app_context)
        context.update({
            "request": request,
            "response": response,
            "APP_NAME": self.name
        })
                
        rendered = template.render(**context)

        start_response(*response())
        return rendered.encode()


