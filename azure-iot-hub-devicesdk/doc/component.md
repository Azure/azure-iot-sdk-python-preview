![Alt text](https://g.gravizo.com/source/svg?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component1.plantuml)


### Working in same file

![Inline diagram](https://g.gravizo.com/source/inline_diag2?https://raw.githubusercontent.com/Azure/azure-iot-sdk-python-preview/diagrams/azure-iot-hub-devicesdk/doc/component.md?1)
<details> 
<summary></summary>
inline_diag2
@startuml;
actor User;
participant "First Class" as A;
participant "Second Class" as B;
participant "Last Class" as C;
User -> A: DoWork;
activate A;
A -> B: Create Request;
activate B;
B -> C: DoWork;
activate C;
C -> B: WorkDone;
destroy C;
B -> A: Request Created;
deactivate B;
A -> User: Done;
deactivate A;
@enduml
inline_diag2
</details>
