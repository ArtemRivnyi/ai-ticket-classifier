"""
Tests for evaluation endpoints in routes/main.py
"""

def test_get_evaluation_results(client):
    response = client.get('/api/v1/evaluation-results')
    assert response.status_code == 200
    data = response.get_json()
    assert 'accuracy' in data
    assert 'total' in data
    assert 'correct' in data
    assert 'results' in data
    assert len(data['results']) > 0


def test_post_evaluation_run(client):
    response = client.post('/api/evaluation/run')
    assert response.status_code == 200
    data = response.get_json()
    assert 'accuracy' in data
    assert 'total' in data
    assert 'correct' in data
    assert 'results' in data
    assert len(data['results']) > 0
