
import hashlib, json

def cache_key(payload: dict, model_name: str, schema_version: str="v1") -> str:
    blob = json.dumps({"payload": payload, "model": model_name, "schema": schema_version}, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
