import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_xss_injection_app_name(client):
    # Test XSS in app_name
    malicious_input = '<script>alert("XSS")</script>'
    response = client.post('/update', data={
        'app_name': malicious_input,
        'description': 'Safe Desc',
        'person_name': 'Safe User'
    }, follow_redirects=True)
    # Jinja2 auto-escapes, so script should not execute
    assert b'<script>' not in response.data
    assert b'&lt;script&gt;' in response.data  # Escaped

def test_xss_injection_description(client):
    malicious_input = '<img src=x onerror=alert("XSS")>'
    response = client.post('/update', data={
        'app_name': 'Safe App',
        'description': malicious_input,
        'person_name': 'Safe User'
    }, follow_redirects=True)
    assert b'<img' not in response.data or b'onerror' not in response.data
    assert b'&lt;img' in response.data  # Escaped

def test_css_injection(client):
    malicious_input = '<style>body { background: red; }</style>'
    response = client.post('/update', data={
        'app_name': malicious_input,
        'description': 'Safe Desc',
        'person_name': 'Safe User'
    }, follow_redirects=True)
    # Check that malicious input is escaped in the title
    assert b'<title>&lt;style&gt;body { background: red; }&lt;/style&gt;</title>' in response.data

def test_js_injection_person_name(client):
    malicious_input = '"><script>alert("XSS")</script>'
    response = client.post('/update', data={
        'app_name': 'Safe App',
        'description': 'Safe Desc',
        'person_name': malicious_input
    }, follow_redirects=True)
    # Check that it's properly handled in author field
    assert b'<script>' not in response.data

def test_html_injection(client):
    malicious_input = '<b>Bold Text</b>'
    response = client.post('/update', data={
        'app_name': malicious_input,
        'description': 'Safe Desc',
        'person_name': 'Safe User'
    }, follow_redirects=True)
    # Since we display it, but Jinja escapes, it should be safe
    assert b'<b>' not in response.data
    assert b'&lt;b&gt;' in response.data