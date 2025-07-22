import os
import ipaddress

def is_valid_cidr(cidr_str):
    try:
        ipaddress.IPv4Network(cidr_str)
        return True
    except ValueError:
        return False

def parse_custom_sg_rules(file_path="custom_sg_rules.txt", vpc_id="default"):
    if not os.path.exists(file_path):
        print("[ERROR] SG rules file not found.")
        return []

    security_groups = []
    current_sg = None
    section = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Remove inline comments and strip
        line = line.split("#")[0].strip()

        if not line:
            continue

        if line.startswith("Name:"):
            if current_sg and current_sg.get("name"):
                if vpc_id:
                    current_sg["vpc_id"] = vpc_id
                security_groups.append(current_sg)

            current_sg = {
                "name": line.split(":", 1)[1].strip(),
                "description": "",
                "ingress": [],
                "egress": []
            }
            section = None

        elif line.startswith("Description:"):
            if current_sg:
                current_sg["description"] = line.split(":", 1)[1].strip()

        elif line.lower().startswith("ingress:"):
            section = "ingress"

        elif line.lower().startswith("egress:"):
            section = "egress"

        elif section in ["ingress", "egress"]:
            try:
                # Handle rule: HTTP: 80 from 0.0.0.0/0
                if section == "ingress" and "from" in line:
                    parts = line.split()
                    description = parts[0].replace(":", "")
                    port = int(parts[1])
                    cidr = parts[3]

                    if not is_valid_cidr(cidr):
                        raise ValueError("Invalid CIDR block")

                    current_sg["ingress"].append({
                        "description": description,
                        "from_port": port,
                        "to_port": port,
                        "protocol": "tcp",
                        "cidr_blocks": [cidr]
                    })

                # Handle rule: 80 to 0.0.0.0/0
                elif section == "egress" and "to" in line:
                    parts = line.split()
                    port = int(parts[0])
                    cidr = parts[2]

                    if not is_valid_cidr(cidr):
                        raise ValueError("Invalid CIDR block")

                    current_sg["egress"].append({
                        "description": f"Port {port}",
                        "from_port": port,
                        "to_port": port,
                        "protocol": "tcp",
                        "cidr_blocks": [cidr]
                    })

            except Exception as e:
                print(f"[WARNING] Skipping malformed rule: {line}. Error: {e}")

    if current_sg and current_sg.get("name"):
        if vpc_id:
            current_sg["vpc_id"] = vpc_id
        security_groups.append(current_sg)

    return security_groups
