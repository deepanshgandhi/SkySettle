import json

def load_policies(file_path: str):
    try:
        with open(file_path, "r") as f:
            policies = json.load(f)
        return policies
    except Exception as e:
        print(f"Error loading policies: {e}")
        return {}
