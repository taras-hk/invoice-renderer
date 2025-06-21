from jinja2 import Environment, FileSystemLoader


def create_invoice(template_path: str, **kwargs) -> str:
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)
    return template.render(**kwargs)
