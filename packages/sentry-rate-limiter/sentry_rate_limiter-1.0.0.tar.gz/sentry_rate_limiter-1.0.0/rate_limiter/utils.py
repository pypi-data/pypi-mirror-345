from functools import lru_cache
import requests

@lru_cache(maxsize=1)
def get_ec2_instance_id():
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token", headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        ).text
        r = requests.get(
            "http://169.254.169.254/latest/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=0.5,
        )
    except requests.exceptions.RequestException:
        return "unknown"
    else:
        return r.text


@lru_cache(maxsize=1)
def get_ec2_instance_name():
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token", headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        ).text
        r = requests.get(
            "http://169.254.169.254/latest/meta-data/tags/instance/Name",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=0.5,
        )
    except requests.exceptions.RequestException:
        return "unknown"
    else:
        return r.text
