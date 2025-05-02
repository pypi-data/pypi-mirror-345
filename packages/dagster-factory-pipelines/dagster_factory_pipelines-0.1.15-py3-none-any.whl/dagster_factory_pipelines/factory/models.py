import os
import jinja2
from pydantic import BaseModel, model_validator
import yaml

#TODO rename models.py to ??

def read_configuration(file_name, render_obj = {"env":os.environ}):
    jinja_template = jinja2.Environment().from_string(open(file_name).read())
    rendered_output = jinja_template.render(render_obj)
    yaml_file = yaml.safe_load(rendered_output)
    return yaml_file


