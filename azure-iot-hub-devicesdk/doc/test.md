### Working in same file
![Inline diagram](https://g.gravizo.com/source/inline_diag3?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component.md)
<details> 
<summary>Sample sequence diagram</summary>
inline_diag3
@startuml;
actor user;
participant "Authentication Provider Factory" as authfac;
participant "Authentication Provider" as auth;
user -> authfac: supply connection string;
activate authfac;
authfac -> auth : factory method call
activate auth;
auth -> authfac : Authentication Provider Object;
deactivate auth;
authfac -> user: Authentication Provider Object;
deactivate authfac;

participant "Device Client" as client;
activate client;
user -> client: create client (auth provider, protocol);
client -> client : class call
client -> user : a device client

@enduml
inline_diag3
</details>
