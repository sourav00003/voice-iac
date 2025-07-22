import os
from jinja2 import Environment, FileSystemLoader

def _generate_main_tf_from_template(context, output_path):
    template_dir = os.path.join(os.path.dirname(__file__), '../../../templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("ec2_only.tf.j2")

    rendered = template.render(context)

    with open(output_path, "w") as f:
        f.write(rendered)

    print("[SUCCESS] main.tf generated successfully for EC2-only (Option 1 or 2).")

def generate_ec2_only_option1_tf(context):
    print("[INFO] Proceeding with default VPC (Option 1)...")
    tf_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../terraform/main.tf'))
    _generate_main_tf_from_template(context, tf_output_path)

def generate_ec2_only_option2_tf(context):
    print("[INFO] Proceeding with existing VPC ID (Option 2)...")
    tf_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../terraform/main.tf'))
    _generate_main_tf_from_template(context, tf_output_path)
