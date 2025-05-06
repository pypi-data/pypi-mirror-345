from ..shared.client.client import Client
from .model import Model


def dto(m: list) -> Model:
    return Model(
        id=m.get('id'),
        name=m.get('name'),
        version=m.get('version'),
        description=m.get('description'),
        args=m.get('args'),
        video=m.get('video'),
        example_outputs=m.get('example_outputs'),
        alias=m.get('alias'),
    )


class Models(Client):
    def __init__(self, api_key: str,mm_url: str) -> None:
        super().__init__(api_key,mm_url)
    
    def list(self):
        """
        list - list all models
        """
        models = super().get("/api/v1/models")

        result = []
        for m in models:
            parsed = dto(m)
            result.append(parsed)
        return result

    def get_by_id(self, id: str):
        """
        get_by_id - get a model by id
        """
        model = super().get("/api/v1/models/%s" % id)
        return dto(model)

    def get_by_name(self, name: str):
        """
        get_by_name - get a model by name
        """
        try:
            path = "/api/v1/models/name/%s" % name
            model = super().get(path)
            return dto(model)
        except Exception as e:
            raise Exception('error getting model %s' % e)
