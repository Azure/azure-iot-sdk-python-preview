![Alt text](https://g.gravizo.com/source/svg?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component1.plantuml)


### Other
![Alt text 2](https://g.gravizo.com/source/svg?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component2.plantuml)


### Working in same file

![Inline diagram](https://g.gravizo.com/source/inline_diag2?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component.md)
<details> 
<summary>Sample sequence diagram</summary>
inline_diag2
@startuml;
actor user;
participant "Authentication Provider" as auth;
user -> auth: Create authentication provider from connection string;
activate auth;
auth -> user: Authentication Provider Object;
deactivate auth;
@enduml
inline_diag2
</details>
