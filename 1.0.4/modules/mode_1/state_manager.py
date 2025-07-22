import boto3
import os
import yaml

def parse_backend_config():
    """
    Parses the backend.yaml file from the 'backend' folder in the project root.
    Returns a dictionary with backend configuration keys.
    """

    # Get absolute path to current file's directory (i.e., modules/mode_1)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Traverse up to project root: ../../.. from mode_1
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))

    # Build path to backend/backend.yaml
    backend_yaml_path = os.path.join(project_root, "backend", "backend.yaml")

    # Check existence
    if not os.path.exists(backend_yaml_path):
        print(f"[ERROR] backend.yaml not found in: {backend_yaml_path}")
        return {}

    # Load YAML content safely
    try:
        with open(backend_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            return {
                "bucket": config.get("bucket"),
                "key": config.get("key", "ec2/terraform.tfstate"),
                "region": config.get("region"),
                "dynamodb_table": config.get("dynamodb_table")
            }
    except Exception as e:
        print(f"[ERROR] Failed to read backend.yaml: {e}")
        return {}


#Deletes state file
def delete_state_file(bucket_name, state_key="ec2/terraform.tfstate"):
    s3 = boto3.client("s3")
    try:
        s3.delete_object(Bucket=bucket_name, Key=state_key)
        print(f"[S3] State file '{state_key}' deleted from bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Failed to delete S3 state file: {e}")


# Delete dynamodb lock
def cleanup_dynamodb_lock(prefix, table_name="voiceiac-tf-locks"):
    dynamodb = boto3.client("dynamodb")
    try:
        response = dynamodb.scan(TableName=table_name)
        items = response.get("Items", [])

        if not items:
            print(f"[DynamoDB] No locks found in table '{table_name}'.")
            return

        deleted = False
        for item in items:
            lock_id = item.get("LockID", {}).get("S", "")
            if lock_id.startswith(prefix):
                dynamodb.delete_item(
                    TableName=table_name,
                    Key={"LockID": {"S": lock_id}}
                )
                print(f"[DynamoDB] Deleted lock: {lock_id}")
                deleted = True

        if not deleted:
            print(f"[DynamoDB] No matching lock found with prefix '{prefix}'.")
        else:
            print(f"[DynamoDB] Cleanup complete for prefix '{prefix}'.")

    except Exception as e:
        print(f"Failed to delete DynamoDB lock(s): {e}")