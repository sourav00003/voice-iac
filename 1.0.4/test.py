#from ansible.modules.ansible_runner import run_ansible
#
## Dry run for testing
#run_ansible(dry_run=True)


#from ansible.modules.inventory_generator import generate_inventory
#
#if __name__ == "__main__":
#    generate_inventory()

import os
import stat

# Absolute or relative path to the PEM file
pem_file = "custom-key.pem"

if not os.path.exists(pem_file):
    print(f"[ERROR] File not found: {pem_file}")
else:
    try:
        os.chmod(pem_file, stat.S_IRUSR)  # 0o400 => read-only for owner
        print(f"[SUCCESS] Permissions set to 400 for: {pem_file}")
    except PermissionError as e:
        print(f"[ERROR] Permission denied: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to change permissions: {e}")