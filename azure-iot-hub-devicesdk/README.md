
Azure IoT Device SDK Installation
=================================

# Install

The wheel file distribution should be named like `azure_iot_hub_devicesdk-0.0.1-py2.py3-none-any.whl`
To install the file with extension `.whl` file please do

`pip install <filename>`

After this on doing `pip list` a package would be found in the list of installed packages named like
`azure-iot-hub-devicesdk` with a certain version like `0.0.1`.

The python interpreter can be invoked by doing `python` on the terminal. 
To invoke python's help please do `help()`

To list all the modules `modules` inside the help.

It should list a module named `azure`. We can type `azure` in thw prompt to get help on this package.
And to discover the packages underneath we can keep on doing `azure.iot` to know more.

For the purpose of writing the sample we know that the top level package is `azure`

# Samples

## Device Sample


In this sample we can create a device client. This device client will enable sending telemetry to the IoT Hub. 


* Create an authentication provider. Authentication provider can be created currently in 2 ways.

  * supplying the device specific connection string
  * supplying the shared access signature

* Create a device client using the authentication provider and a transport protocol. Currently the SDK only supports `mqtt`.
* Connect the device client.
* Send event from the device client. Send event can be invoked after

  * Verifying that the device client has been connected
  * Or sleeping for a little while to let the device client be connected.

### Code snippet

.. code-block:: python

    from azure.iot.hub.devicesdk.device_client import DeviceClient
    from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_connection_string

    conn_str = "<IOTHUB_DEVICE_CONNECTION_STRING>"
    auth_provider = from_connection_string(conn_str)
    simple_device = DeviceClient.from_authentication_provider(auth_provider, "mqtt")


    def connection_state_callback(status):
        print("connection status: " + status)
            if status == "connected":
                simple_device.send_event("caput draconis")

    simple_device.on_connection_state = connection_state_callback
    simple_device.connect()

## Module Sample

This is very similar to the device client. All the steps above remains same except that now we create a module client.

### Code snippet


Below code shows a different way of creating an authentication provider from a shared access signature and then using a module client. 

.. code-block:: python

    from azure.iot.hub.devicesdk.module_client import ModuleClient
    from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_shared_access_signature

    sas_token_string = "<IOTHUB_DEVICE_SAS_STRING>"

    auth_provider = from_shared_access_signature(str(sas_token_string))
    simple_module = ModuleClient.from_authentication_provider(auth_provider, "mqtt")

    def connection_state_callback(status):
        print("connection status: " + status)
            if status == "connected":
                simple_module.send_event("payload from module")

    simple_module.on_connection_state = connection_state_callback
    simple_module.connect()
