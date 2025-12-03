#!/usr/bin/env python3
"""Quick test of Flask routes without running a server."""

import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app

app = create_app()

# Test with Flask's test client
with app.test_client() as client:
    # Test root route
    print("Testing GET /...")
    response = client.get('/')
    print(f"  Status: {response.status_code}")
    print(f"  Content-Type: {response.content_type}")
    print(f"  Body (first 100 chars): {response.data[:100]}")
    
    # Test status endpoint
    print("\nTesting GET /status...")
    response = client.get('/status')
    print(f"  Status: {response.status_code}")
    print(f"  Data: {response.get_json()}")
    
    # Test generate endpoint
    print("\nTesting POST /generate...")
    response = client.post('/generate', json={'topic': 'test'})
    print(f"  Status: {response.status_code}")
