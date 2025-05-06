from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Job:
    id: str
    credits_used: str
    results: List[str]
    status: str
    error: str
    deployment_id: str
    duration: int
    logs: str
    eta: int
    etr: int


@dataclass
class Deployment:
    id: str
    model: str
    job: Job
    status: str
    name: str
    job_id: str
    logs: str

@dataclass
class CreateDeployment:
    model: str
    args: Dict
    name: str
    output_format: Optional[str] = None
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    sync: bool = False

    def dict(self):
        return super().dict()

def request_dto(id: str, m: CreateDeployment) -> dict:
    return {
        'model_id': id,
        'args': m.args,
        'name': m.name,
        'output_format': m.output_format,
        'output_width': m.output_width,
        'output_height': m.output_height,
    }

def dto(m: dict) -> Deployment:
    return Deployment(
        id=m.get('id'),
        model=m.get('alias'),
        job=m.get('job'),
        status=m.get('status'),
        logs=m.get('logs'),
        job_id=m.get('job_id'),
        name=m.get('name'),
    )
