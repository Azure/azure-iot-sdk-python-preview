import os


def are_envs_having_value():
    PROVISIONING_SERVICE_CONNECTION_STRING = os.getenv("PROVISIONING_SERVICE_CONNECTION_STRING")
    IOTHUB_CONNECTION_STRING = os.getenv("IOTHUB_CONNECTION_STRING")
    PROVISIONING_DEVICE_ENDPOINT = os.getenv("PROVISIONING_DEVICE_ENDPOINT")
    PROVISIONING_DEVICE_IDSCOPE = os.getenv("PROVISIONING_DEVICE_IDSCOPE")
    ca_cert = os.getenv("PROVISIONING_ROOT_CERT")
    ca_key = os.getenv("PROVISIONING_ROOT_CERT_KEY")

    if PROVISIONING_SERVICE_CONNECTION_STRING is None:
        print("PROVISIONING_SERVICE_CONNECTION_STRING is None")
    elif (
        "SharedAccessKey=Tigx8gkP+rkhM+WcMmBbj1N/BW25LGRc1u4mLM7in3k="
        in PROVISIONING_SERVICE_CONNECTION_STRING
    ):
        print("PROVISIONING_SERVICE_CONNECTION_STRING has correct value")
    else:
        print("PROVISIONING_SERVICE_CONNECTION_STRING has incorrect value")

    if IOTHUB_CONNECTION_STRING is None:
        print("IOTHUB_CONNECTION_STRING is None")
    else:
        print("IOTHUB_CONNECTION_STRING is not None")

    if PROVISIONING_DEVICE_ENDPOINT is None:
        print("PROVISIONING_DEVICE_ENDPOINT is None")
    else:
        print("PROVISIONING_DEVICE_ENDPOINT is not None")

    if PROVISIONING_DEVICE_IDSCOPE is None:
        print("PROVISIONING_DEVICE_IDSCOPE is None")
    else:
        print("PROVISIONING_DEVICE_IDSCOPE is not None")

    if ca_cert is None:
        print("ca_cert is None")
    else:
        print("ca_cert is not None")

    if ca_key is None:
        print("ca_key is None")
    else:
        print("ca_key is not None")


if __name__ == "__main__":
    are_envs_having_value()
