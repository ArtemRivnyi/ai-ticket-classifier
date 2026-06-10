import os
import re

files = [
    'tests/test_integration.py',
    'tests/test_final_coverage.py',
    'tests/test_evaluation_endpoint.py',
    'tests/test_coverage_boost.py'
]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # Replace mocker.patch('app.classifier', mock_classifier) with app.config['CLASSIFIER'] = mock_classifier
    content = content.replace('mocker.patch("app.classifier", mock_classifier)', 'app.config["CLASSIFIER"] = mock_classifier')
    
    # Replace mocker.patch('app.classifier') with mock_classifier = MagicMock(); app.config['CLASSIFIER'] = mock_classifier
    content = content.replace('mock_classifier = mocker.patch("app.classifier")', 'mock_classifier = mocker.MagicMock(); app.config["CLASSIFIER"] = mock_classifier')
    
    # Add `app` to the function arguments
    content = re.sub(r'def (test_[a-zA-Z0-9_]+)\((.*?mocker.*?)\):', lambda m: 'def ' + m.group(1) + '(' + (m.group(2) if 'app' in [arg.strip() for arg in m.group(2).split(',')] else m.group(2).replace('mocker', 'app, mocker')) + '):', content)
    
    with open(f, 'w') as file:
        file.write(content)
    print(f"Fixed {f}")
