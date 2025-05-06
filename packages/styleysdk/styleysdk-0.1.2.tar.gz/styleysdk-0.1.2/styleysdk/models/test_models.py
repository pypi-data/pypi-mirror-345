from .models import Models
import pytest
import os


_API_KEY = os.getenv("X_MEDIAMAGIC_KEY")


def test_can_list_models():
    models_client = Models(_API_KEY)
    models = models_client.list()

    assert len(models) > 0


def test_can_get_model_by_id():
    models_client = Models(_API_KEY)
    models = models_client.list()
    
    model = {}
    for m in models:
        if m.name == 'Magic AI':
            model = m

    m = models_client.get_by_id(id=model.id)

    assert m.name == 'Magic AI'
