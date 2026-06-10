import pytest
import json
from app import app
import os


from extensions import db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()





def test_about_page(client):
    """Test about page renders"""
    response = client.get("/about")
    assert response.status_code == 200
    assert b"AI Ticket Classifier" in response.data


def test_evaluation_page(client):
    """Test evaluation page renders"""
    response = client.get("/evaluation")
    assert response.status_code == 200
    assert b"Model Evaluation" in response.data
