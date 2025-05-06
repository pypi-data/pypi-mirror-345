from .deployments import Deployments
from .model import CreateDeployment

import pytest
import os


_API_KEY = os.getenv("X_MEDIAMAGIC_KEY")


def test_can_create_deployment():
    deployment_client = Deployments(api_key=_API_KEY)
    deployment = deployment_client.create(deployment=CreateDeployment(
        name="test-deployment",
        model="pingponai/background-removal",
        args={
            'input_image_file': 'https://cdn.mediamagic.dev/media/eb341446-be53-11ed-b4a8-66139910f724.jpg',
        },
        output_format="png",
        output_width=1024,
        output_height=1024,
    ))
    assert deployment.job.credits_used > 0
    assert deployment.job.id is not None


def test_can_list_deployments():
    deployment_client = Deployments(api_key=_API_KEY)
    deployments = deployment_client.list(0, 10)
