#integration tests
# import pytest
# from webapp import create_app, db

# @pytest.fixture
# def app():
#     app = create_app('testing')
#     with app.app_context():
#         db.create_all()
#         yield app
#         db.session.remove()
#         db.drop_all()

# def test_valid_submission(app):
#     client = app.test_client()
#     response = client.post('/submit', data={'name': 'John Doe', 'email': 'john.doe@example.com'})