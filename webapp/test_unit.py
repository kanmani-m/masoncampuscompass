#unit tests
import pytest
from webapp import create_app

def test_config():
    app = create_app()
    assert app.config['TESTING'] is True
def test_home_page():
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
