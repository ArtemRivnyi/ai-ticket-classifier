"""
Additional tests to improve coverage
"""
import pytest
from unittest.mock import MagicMock, patch


def test_run_evaluation_with_real_dataset(client, headers, mocker):
    """Test evaluation with actual dataset file"""
    # Mock classifier
    mock_classifier = MagicMock()
    mock_classifier.classify.return_value = {
        'category': 'Network Issue',
        'priority': 'high',
        'provider': 'gemini'
    }
    mocker.patch('app.classifier', mock_classifier)
    
    response = client.post('/api/evaluation/run', headers=headers)
    
    # Should work if test_dataset.csv exists
    if response.status_code == 200:
        data = response.get_json()
        assert 'accuracy' in data
        assert 'total' in data
    else:
        # File not found is also acceptable
        assert response.status_code == 404


def test_batch_csv_with_pandas_error(client, headers, mocker):
    """Test CSV batch when pandas fails to read CSV"""
    from io import BytesIO
    import pandas as pd
    
    # Mock pandas to raise exception
    mocker.patch('pandas.read_csv', side_effect=pd.errors.ParserError("Invalid CSV"))
    
    csv_content = b"ticket\ntest"
    
    response = client.post(
        '/api/v1/classify/batch-csv',
        data={'file': (BytesIO(csv_content), 'test.csv')},
        headers=headers,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_batch_csv_missing_ticket_column(client, headers, mocker):
    """Test CSV batch when ticket column is missing"""
    from io import BytesIO
    import pandas as pd
    
    # Mock pandas to return DataFrame without ticket column
    mock_df = pd.DataFrame({'wrong_column': ['test']})
    mocker.patch('pandas.read_csv', return_value=mock_df)
    
    csv_content = b"wrong_column\ntest"
    
    response = client.post(
        '/api/v1/classify/batch-csv',
        data={'file': (BytesIO(csv_content), 'test.csv')},
        headers=headers,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_batch_csv_partial_success(client, headers, mocker):
    """Test CSV batch with some successful and some failed classifications"""
    from io import BytesIO
    
    # Mock classifier that fails on second call
    mock_classifier = MagicMock()
    mock_classifier.classify.side_effect = [
        {'category': 'Network Issue', 'priority': 'high', 'provider': 'gemini'},
        Exception("Classification failed"),
        {'category': 'Billing Bug', 'priority': 'medium', 'provider': 'gemini'}
    ]
    mocker.patch('app.classifier', mock_classifier)
    
    csv_content = b"ticket\nVPN down\nTest error\nBilling issue"
    
    response = client.post(
        '/api/v1/classify/batch-csv',
        data={'file': (BytesIO(csv_content), 'test.csv')},
        headers=headers,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 3
    assert data['successful'] == 2
    assert data['failed'] == 1
