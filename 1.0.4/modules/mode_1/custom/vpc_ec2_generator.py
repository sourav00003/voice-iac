import os
from jinja2 import Environment, FileSystemLoader

def _generate_main_tf_from_template(context, output_path):
    template_dir = os.path.join(os.path.dirname(__file__), '../../../templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("vpc_ec2.tf.j2")

    rendered = template.render(context)

    with open(output_path, "w") as f:
        f.write(rendered)

    print("[SUCCESS] main.tf generated successfully for EC2 + Custom VPC (Option 3).")

def generate_vpc_ec2_option3_tf(context):
    print("[INFO] Proceeding with custom VPC creation (Option 3)...")
    tf_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../terraform/main.tf'))
    _generate_main_tf_from_template(context, tf_output_path)