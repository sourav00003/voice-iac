import boto3

def parse_backend_config(file_path="templates/main.tf.backup"):
    bucket = None
    key = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0].strip()

            if line.startswith("bucket"):
                bucket = line.split("=")[1].strip().strip('"')
            elif line.startswith("key"):
                value = line.split("=")[1].strip().strip('"')
                # Skip placeholder
                if "__KEY_NAME__" not in value:
                    key = value

    # Fallback default if placeholder still present
    if not key:
        key = "ec2/terraform.tfstate"

    return bucket, key

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