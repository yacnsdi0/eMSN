from dataclasses import dataclass


@dataclass
class FlowRequest:
    id: str = ""
    switch: str = ""


@dataclass
class FlowAck:
    status: str = ""
