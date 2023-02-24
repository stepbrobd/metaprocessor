import metaprocessor.config


def run() -> int:
    config = {
        "general": {"timezone_offset": int()},
        "regex": {"patient_id": str(), "session_id": str(), "device_id": str()},
        "aws": {"api_endpoint": str(), "region": str(), "access_key_id": str(), "aws_secret_access_key": str(), "bucket": str()},
    }

    config["general"]["timezone_offset"] = int(input("Timezone Offset: "))
    config["regex"]["patient_id"] = input("Patient ID Regex: ")
    config["regex"]["session_id"] = input("Session ID Regex: ")
    config["regex"]["device_id"] = input("Device ID Regex: ")
    config["aws"]["endpoint"] = input("AWS API Endpoint: ")
    config["aws"]["region"] = input("AWS Region: ")
    config["aws"]["access_key_id"] = input("AWS Access Key ID: ")
    config["aws"]["aws_secret_access_key"] = input("AWS Secret Access Key: ")
    config["aws"]["bucket"] = input("AWS Bucket: ")

    metaprocessor.config.write_config(config)

    return 0
