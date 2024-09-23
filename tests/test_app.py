import pytest
from app import create_app
import json

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_generate_unittest(client):
    response = client.post('/api/generate_basic_test', json={'code': 'public class HelloWorld { public static void main(String[] args) { System.out.println("Hello, world!"); } }'})
    assert response.status_code == 200
    assert 'unittest' in response.json
    # write to file
    with open('test_generate_unittest.out', 'w') as f:
        result = response.json
        f.write(json.dumps(result))

