import ipaddress

def is_valid_cidr(cidr_str):
    try:
        ipaddress.IPv4Network(cidr_str)
        return True
    except ValueError:
        return False

def parse_sg_rules(file_path="custom_sg_rules.txt"):
    """
    Parses custom_sg_rules.txt and returns a list of security groups with ingress/egress rules.
    """
    security_groups = []
    current_sg = {
        "name": None,
        "description": None,
        "ingress": [],
        "egress": []
    }

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("[ERROR] SG rules file not found.")
        return security_groups

    section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("Name:"):
            current_sg["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Description:"):
            current_sg["description"] = line.split(":", 1)[1].strip()
        elif line.startswith("Ingress:"):
            section = "ingress"
        elif line.startswith("Egress:"):
            section = "egress"
        elif section in ["ingress", "egress"]:
            # Handle 'all' case in egress
            if section == "egress" and line.lower() == "all":
                current_sg["egress"].append({
                    "port": 0,
                    "protocol": "-1",
                    "cidr": "0.0.0.0/0"
                })
                continue

            # Handle lines like: SSH: 22 from 0.0.0.0/0
            parts = line.split()
            if len(parts) >= 4 and "from" in parts:
                try:
                    port = parts[1]
                    cidr = parts[3]
                    if not is_valid_cidr(cidr):
                        print(f"[WARNING] Skipping invalid CIDR: {cidr}")
                        continue

                    rule = {
                        "port": int(port.split("-")[0]) if port.replace("-", "").isdigit() else 0,
                        "protocol": "tcp" if section == "ingress" else "-1",
                        "cidr": cidr
                    }
                    current_sg[section].append(rule)
                except Exception as e:
                    print(f"[WARNING] Skipping malformed line: {line}. Error: {e}")
                    continue

    if current_sg["name"]:
        security_groups.append(current_sg)

    return security_groups
