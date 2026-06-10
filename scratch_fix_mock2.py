import os

files = [
    'tests/test_integration.py',
    'tests/test_final_coverage.py',
    'tests/test_evaluation_endpoint.py',
    'tests/test_coverage_boost.py'
]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    content = content.replace(
        'app.config["CLASSIFIER"] = mock_classifier',
        'mocker.patch.dict(app.config, {"CLASSIFIER": mock_classifier})'
    )
    
    with open(f, 'w') as file:
        file.write(content)
    print(f"Fixed {f}")
