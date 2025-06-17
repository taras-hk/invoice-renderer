from jinja2 import Environment, FileSystemLoader


def create_invoice(**kwargs) -> str:
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template-1.html')
    return template.render(**kwargs)
