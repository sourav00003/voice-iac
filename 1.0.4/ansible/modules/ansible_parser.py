import yaml
import os
from jinja2 import Environment, FileSystemLoader
from ansible.modules.allowed_packages import is_service, is_utility

def parse_custom_ansible_yaml(yaml_path="yaml/custom_ansible.yaml"):
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"[ERROR] YAML file not found: {yaml_path}")

    with open(yaml_path, 'r') as f:
        try:
            yaml_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise Exception(f"[ERROR] Failed to parse YAML: {e}")

    if not yaml_data or "software_needed" not in yaml_data:
        raise ValueError("[ERROR] YAML must contain 'software_needed' key")

    software = yaml_data.get("software_needed", [])

    utilities = []
    services = []
    skipped = []

    for pkg in software:
        pkg = pkg.strip().lower()
        if is_service(pkg):
            services.append(pkg)
        elif is_utility(pkg):
            utilities.append(pkg)
        else:
            skipped.append(pkg)

    return {
        "services": services,
        "utilities": utilities,
        "skipped": skipped
    }


def generate_ansible_playbook_from_yaml(yaml_path="yaml/custom_ansible.yaml", output_path="ansible/playbook/site.yaml"):
    parsed_data = parse_custom_ansible_yaml(yaml_path)

    TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../templates"))
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    template = env.get_template("playbook.j2")

    rendered_playbook = template.render(
        services=parsed_data["services"],
        utilities=parsed_data["utilities"]
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(rendered_playbook)

    print(f"[SUCCESS] Ansible playbook created at: {output_path}")
    if parsed_data["skipped"]:
        print(f"[WARNING] Skipped unsupported packages: {parsed_data['skipped']}")
