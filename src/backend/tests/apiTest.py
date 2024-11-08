from backend.Api import Api


def test_get_blueprints():
    api = Api()
    steps = api.STORAGE.load_all_steps()
    assert True

def test_get_pipelines():
    api = Api()
    steps = api.STORAGE.load_all_pipelines()
    assert True
