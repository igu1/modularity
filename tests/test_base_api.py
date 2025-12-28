import json

def test_health_api(client):
    status_code, data, _ = client.get('/api/health')
    assert status_code == 200
    assert data['success'] is True
    assert data['status'] == 'healthy'

def test_status_api(client):
    status_code, data, _ = client.get('/api/status')
    assert status_code == 200
    assert data['success'] is True
    assert 'system' in data

def test_organization_crud(client):
    # Create
    org_data = {
        'name': 'Test Org',
        'slug': 'test-org',
        'description': 'A test organization'
    }
    status_code, data, _ = client.post('/api/organizations', data=org_data)
    assert status_code == 201
    org_id = data['id']

    # List
    status_code, data, _ = client.get('/api/organizations')
    assert status_code == 200
    assert any(o['id'] == org_id for o in data)

    # Get
    status_code, data, _ = client.get(f'/api/organizations/{org_id}')
    assert status_code == 200
    assert data['name'] == 'Test Org'

    # Update
    update_data = {'name': 'Updated Org', 'slug': 'test-org'}
    status_code, data, _ = client.put(f'/api/organizations/{org_id}', data=update_data)
    assert status_code == 200

    # Verify update
    status_code, data, _ = client.get(f'/api/organizations/{org_id}')
    assert data['name'] == 'Updated Org'

    # Delete
    status_code, data, _ = client.delete(f'/api/organizations/{org_id}')
    assert status_code == 200

    # Verify delete
    status_code, data, _ = client.get(f'/api/organizations/{org_id}')
    assert status_code == 404
