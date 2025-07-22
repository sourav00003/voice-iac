def parse_sg_rules(file_path="custom_sg_rules.txt"):
    """
    Parses custom_sg_rules.txt and returns a list of security groups with ingress/egress rules.
    Structure:
    [
        {
            "name": "custom_sg",
            "description": "Custom_SG_for_EC2",
            "ingress": [{"port": 22, "protocol": "tcp", "cidr": "0.0.0.0/0"}],
            "egress": [{"port": 0, "protocol": "-1", "cidr": "0.0.0.0/0"}]
        }
    ]
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
            # Example line: SSH: 22 from 0.0.0.0/0
            parts = line.split()
            if len(parts) >= 4:
                port = parts[1]
                cidr = parts[-1]
                rule = {
                    "port": int(port.split("-")[0]) if port.isdigit() else 0,
                    "protocol": "tcp" if section == "ingress" else "-1",  # Default protocols
                    "cidr": cidr
                }
                current_sg[section].append(rule)

    if current_sg["name"]:
        security_groups.append(current_sg)

    return security_groups
