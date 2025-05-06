import os

from .deployments.deployments import Deployments
from .models.models import Models

_MM_URL = "https://api-qa.mediamagic.ai"

_API_KEY = os.getenv('X_STYLEY_KEY')
_MM_BASE_URL = os.getenv('MM_HOST_URL', _MM_URL)

class Styley:
    """
    Styley - is a vanity class, which simply
    combined the underlying libraries into one
    object with the api configured for each etc.
    """

    models: Models
    deployments: Deployments

    def __init__(self, api_key=_API_KEY, mm_url=_MM_BASE_URL):
        if not api_key:
            raise ValueError("X_STYLEY_KEY missing")
        if not mm_url:
            raise ValueError("MM_BASE_URL missing")
        self.models = Models(api_key=api_key,mm_url=mm_url)
        self.deployments = Deployments(api_key=api_key,mm_url=mm_url, models=self.models)
