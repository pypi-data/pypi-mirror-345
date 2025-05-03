from _typeshed import Incomplete
from enum import Enum

class SmiKind(Enum):
    CHILD_SW_SMI = 0
    SW_SMI = 1
    USB_SMI = 2
    SX_SMI = 3
    IO_TRAP_SMI = 4
    GPI_SMI = 5
    TCO_SMI = 6
    STANDBY_BUTTON_SMI = 7
    PERIODIC_TIMER_SMI = 8
    POWER_BUTTON_SMI = 9
    ICHN_SMI = 10
    PCH_TCO_SMI = 11
    PCH_PCIE_SMI = 12
    PCH_ACPI_SMI = 13
    PCH_GPIO_UNLOCK_SMI = 14
    PCH_SMI = 15
    PCH_ESPI_SMI = 16
    ACPI_EN_SMI = 17
    ACPI_DIS_SMI = 18

class UefiService:
    name: Incomplete
    address: Incomplete
    def __init__(self, name: str, address: int) -> None: ...
    @property
    def __dict__(self): ...

class UefiGuid:
    value: Incomplete
    name: Incomplete
    def __init__(self, value: str, name: str) -> None: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def __dict__(self): ...

class UefiProtocol(UefiGuid):
    address: Incomplete
    guid_address: Incomplete
    service: Incomplete
    def __init__(self, name: str, address: int, value: str, guid_address: int, service: str) -> None: ...
    @property
    def __dict__(self): ...

class UefiProtocolGuid(UefiGuid):
    address: Incomplete
    def __init__(self, name: str, address: int, value: str) -> None: ...
    @property
    def __dict__(self): ...

class NvramVariable:
    name: Incomplete
    guid: Incomplete
    service: Incomplete
    def __init__(self, name: str, guid: str, service: UefiService) -> None: ...
    @property
    def __dict__(self): ...

class SmiHandler:
    address: Incomplete
    kind: Incomplete
    def __init__(self, address: int, kind: SmiKind) -> None: ...
    @property
    def place(self): ...
    @property
    def __dict__(self): ...

class ChildSwSmiHandler(SmiHandler):
    handler_guid: Incomplete
    def __init__(self, handler_guid: str | None, address: int) -> None: ...
    @property
    def __dict__(self): ...
