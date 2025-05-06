from dataclasses import dataclass


@dataclass
class Model:
    id: str
    name: str
    alias: str
    description: str
    example_outputs: list[str]
    args: list[dict]
    video: str
    version: str
