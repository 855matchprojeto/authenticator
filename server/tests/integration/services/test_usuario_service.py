from server.tests.integration import db_docker_container, cwd_to_root, create_db_upgrade
from fastapi.testclient import TestClient


# def test_test(test_client: TestClient):
#     response = test_client.post(
#         'users',
#         json={
#           "nome": "string",
#           "username": "string",
#           "password": "string",
#           "email": "user@example.com"
#         }
#     )
#     assert True
#
