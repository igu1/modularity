import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateEngine:
    def __init__(self, modules_path: str):
        self.modules_path = modules_path
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.modules_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render(self, module_name: str, template_name: str, **context) -> str:
        # Templates are expected to be in src/modular_system/modules/<module_name>/templates/<template_name>
        # FileSystemLoader is initialized with src/modular_system/modules/
        template_path = os.path.join(module_name, 'templates', template_name)
        template = self.jinja_env.get_template(template_path)
        return template.render(**context)
