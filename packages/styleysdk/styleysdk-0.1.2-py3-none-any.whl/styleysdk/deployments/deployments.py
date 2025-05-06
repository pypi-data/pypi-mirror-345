from ..shared.client.client import Client
from .model import Deployment, dto, request_dto, CreateDeployment,Job
import time
from typing import List

from dataclasses import asdict

COMPLETE = 'complete'
FAILED = 'failed'
ETA = 180

class Deployments(Client):

    def __init__(self, api_key: str,mm_url: str, models) -> None:
        self.models = models
        super().__init__(api_key,mm_url)


    def get_by_id(self, id: str) -> Deployment:
        """
        get_by_id - get a deployment by its ID
        """
        deployment = super().get("/api/v1/deployments/%s" % id)
        return dto(deployment)
    

    def create(self, deployment: CreateDeployment) -> Deployment:
        """
        create - create a new Deployment
        """
        try:
            model = self.models.get_by_id(deployment.model)
            id = model.id
            request = request_dto(id, deployment)
            deployment = super().post("/api/v1/deployments", request)
            response=dto(deployment)
            status=response.status
            eta = ETA
            while status!=COMPLETE and status!=FAILED and eta > 0:
                time.sleep(10)
                job=self.get_job(response.job_id)
                status=job['status']
                eta -= 5
                response.status=status
                if 'logs' in job:
                    response.logs=job['logs']
                response.job=job
            return response
        except Exception as e:
            raise Exception('error creating deployment: %s' % e)


    def list(self) -> List[Deployment]:
        """
        list - list all of your deployments
        """
        deployments = super().get("/api/v1/deployments")
        return deployments
    
    def get_job(self, id:str) -> Job:
        """
        get_job - get job by ID
        """
        path="/api/v1/jobs/"+ id
        job = super().get(path)

        return job

    
