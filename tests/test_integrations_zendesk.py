import json

from app import app


def test_zendesk_webhook_success(client, mocker, headers):
    mock_classifier = mocker.Mock()
    mock_classifier.classify.return_value = {
        'category': 'Network Issue',
        'confidence': 0.91,
        'priority': 'high',
        'provider': 'gemini',
    }
    app.config['CLASSIFIER'] = mock_classifier

    payload = {
        'ticket_id': 123,
        'subject': 'VPN broken',
        'description': 'Users cannot access VPN since morning',
        'requester_email': 'user@example.com',
    }

    response = client.post(
        '/api/v1/integrations/zendesk',
        data=json.dumps(payload),
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'processed'
    assert data['zendesk']['ticket_id'] == 123
    assert 'ai_classifier' in data['zendesk']['tags']


def test_zendesk_webhook_validation_error(client, mocker, headers):
    mock_classifier = mocker.Mock()
    app.config['CLASSIFIER'] = mock_classifier
    response = client.post(
        '/api/v1/integrations/zendesk',
        data=json.dumps({'ticket_id': 1}),
        headers=headers,
    )
    assert response.status_code == 400


def test_zendesk_webhook_no_classifier(client, headers):
    app.config['CLASSIFIER'] = None
    payload = {
        'ticket_id': 1,
        'subject': 'Test',
        'description': 'Test',
    }
    response = client.post(
        '/api/v1/integrations/zendesk',
        data=json.dumps(payload),
        headers=headers,
    )
    assert response.status_code == 503

