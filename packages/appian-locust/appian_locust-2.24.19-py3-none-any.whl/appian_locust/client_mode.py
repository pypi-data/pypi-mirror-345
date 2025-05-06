from enum import Enum


class ClientMode(Enum):
    TEMPO: str = "TEMPO"
    EMBEDDED: str = "EMBEDDED"
    SITES: str = "SITES"
    ADMIN: str = "ADMIN"
    DESIGN: str = "DESIGN"
    INTERFACE_DESIGN: str = "INTERFACE_DESIGN"
    PORTALS: str = "PORTALS"
    SAIL_LIBRARY: str = "SAIL_LIBRARY"
    DOCS_REPL: str = "DOCS_REPL"
    PROCESS_HQ: str = "PROCESS_HQ"
