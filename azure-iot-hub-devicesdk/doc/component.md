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
inline_diag2
</details>

## Another YUML Not sure if sequence diagram is possible
<img src="http://yuml.me/diagram/scruffy/class/[note: You can stick notes on diagrams too!{bg:cornsilk}],[Customer]<>1-orders 0..*>[Order], [Order]++*-*>[LineItem], [Order]-1>[DeliveryMethod], [Order]*-*>[Product], [Category]<->[Product], [DeliveryMethod]^[National], [DeliveryMethod]^[International]" >
