import re

VALID_INSTANCE_TYPES = [
    "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large",
    "t3.nano", "t3.micro", "t3.small", "t3.medium", "t3.large",
    "t3a.micro", "t3a.small", "t3a.medium"
]

VALID_ACTIONS = [
    "create", "launch", "destroy", "terminate", "delete"
]

VALID_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ap-south-1", "ap-northeast-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
    "eu-central-1", "eu-west-1", "eu-west-2", "eu-north-1",
    "sa-east-1", "ca-central-1", "af-south-1", "me-south-1"
]

FUZZY_INSTANCE_ALIASES = {
    "t2micro": "t2.micro",
    "t2microinstance": "t2.micro",
    "t2mic": "t2.micro",
    "t3micro": "t3.micro",
    "t3mic": "t3.micro",
    "t2small": "t2.small",
    "t2medium": "t2.medium",
    "82micro": "t2.micro",         
    "80tomicro": "t2.micro",       
    "a2micro": "t2.micro",
    "eightytwomicro": "t2.micro",  
}

FUZZY_REGION_ALIASES = {
    "useast1": "us-east-1",
    "us-eastone": "us-east-1",
    "useastone": "us-east-1",
    "u s east one": "us-east-1",
    "u.s.east.1": "us-east-1",
    "us east": "us-east-1",
    "east us": "us-east-1",
    "apsouth1": "ap-south-1",
    "apsouth": "ap-south-1",
    "south asia": "ap-south-1",
    "mumbai": "ap-south-1"
    # Add more fuzzy mappings as needed
}



def normalize(text):
    return text.lower().replace(" ", "").replace(".", "").replace("-", "")


def extract_keywords(text):
    original_text = text
    normalized_text = normalize(text)

    action = None
    instance_type = None
    region = None
    volume_size = None


    # Match action
    for a in VALID_ACTIONS:
        if a in normalized_text:
            # Map synonyms like terminate/delete to "destroy"
            if a in ["destroy", "terminate", "delete"]:
                action = "destroy"
            else:
                action = "create"
            break

    # Match instance type
    for itype in VALID_INSTANCE_TYPES:
        if normalize(itype) in normalized_text:
            instance_type = itype
            break

    # Match region from VALID_REGIONS
    for region_option in VALID_REGIONS:
        if normalize(region_option) in normalized_text:
            region = region_option
            break
    
    # Fuzzy Instances
    if not instance_type:
        for fuzzy, real in FUZZY_INSTANCE_ALIASES.items():
            if fuzzy in normalized_text:
                instance_type = real
                print(f"[Fuzzy match] Interpreted instance type as: {real}")
                break

    if not region:
        for fuzzy, real in FUZZY_REGION_ALIASES.items():
            if fuzzy in normalized_text:
                region = real
                print(f"[Fuzzy match] Interpreted region as: {real}")
                break

    # Match volume size
    volume_match = re.search(r"(\d+)\s*gb", original_text.lower())
    if volume_match:
        volume_size = volume_match.group(1)

    return {
        "action": action,
        "instance_type": instance_type,
        "region": region,
        "volume_size": volume_size
    }
