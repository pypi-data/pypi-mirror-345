import os
import typer
from flask_setup.methods import do_add_log

LOG_TYPE = 'modules'

def run_add_model_command(path, blueprint, model_name, fields):
    """
    Add a new model class to an existing blueprint.
    """
    bp_dir = os.path.join('app', blueprint)
    if not os.path.isdir(bp_dir):
        typer.echo(f'Blueprint {blueprint} does not exist')
        return

    # Prepare file paths
    model_file = os.path.join(bp_dir, 'model.py')
    template_file = os.path.join(path, 'generators', 'blueprint', 'model.py')

    # Read template
    with open(template_file, 'r') as f:
        template = f.read()

    # Process fields
    model_field_types = {
        "str":"String",
        "int":"Integer",
        "date":"DateTime",
        "float":"Float",
        "bool":"Boolean",
        "fk":"ForeignKey",
        "rel":"relationship",
    }
    model_fields = [f.lower() for f in fields if not (f.split(':')[-1].startswith('fk') or f.split(':')[-1].startswith('rel'))]
    fk_model_fields = [f.lower() for f in fields if f.split(':')[-1].startswith('fk')]
    rel_model_fields = [f.lower() for f in fields if f.split(':')[-1].startswith('rel')]
    field_names = [f.split(':')[0].lower() for f in fields if not f.split(':')[-1].startswith('rel')]

    # Generate code pieces
    if fields:
        extra_fields = "\n    ".join([f"{a.split(':')[0]} = db.Column(db.{model_field_types.get(a.split(':')[-1], 'String')})" for a in model_fields])
        if fk_model_fields:
            fk_fields = "\n    ".join([f"{a.split(':')[0]} = db.Column(db.Integer, db.ForeignKey('{a.split(':')[-1].split('=')[-1]}'))" for a in fk_model_fields])
            extra_fields += "\n    " + fk_fields
        if rel_model_fields:
            rel_fields = "\n    ".join([f"{a.split(':')[0]} = db.relationship('{a.split(':')[-1].split('=')[-1].title()}')" for a in rel_model_fields])
            extra_fields += "\n    " + rel_fields
        args = ", ".join(field_names)
        kwargs = ", ".join([f"{a}={a}" for a in field_names])
        optional_kwargs = ", ".join([f"{a}=None" for a in field_names])
        list_optional_kwargs = "\n        ".join([f"self.{a} = {a} or self.{a}" for a in field_names])
    else:
        extra_fields = ""
        args = ""
        kwargs = ""
        optional_kwargs = ""
        list_optional_kwargs = ""

    # Replace template placeholders
    content = template.replace('__Blueprint__', model_name).replace('__blueprint__', model_name.lower())
    content = content.replace('__additional_fields__', extra_fields)
    content = content.replace('__args__', args)
    content = content.replace('__kwargs__', kwargs)
    content = content.replace('__optional_kwargs__', optional_kwargs)
    content = content.replace('__list_optional_kwargs__', list_optional_kwargs)

    # Append or create model.py
    if os.path.exists(model_file):
        # skip import line when appending
        body = "\n".join(content.splitlines()[1:])
        with open(model_file, 'a') as f:
            f.write('\n\n' + body)
    else:
        with open(model_file, 'w') as f:
            f.write(content)

    # Log addition
    log = {
        "blueprint": blueprint,
        "model": model_name,
        "fields": [{"name":f.split(':')[0], "type":f.split(':')[-1]} for f in fields]
    }
    do_add_log(LOG_TYPE, log)
    typer.echo(f'Model {model_name} added to blueprint {blueprint} successfully')