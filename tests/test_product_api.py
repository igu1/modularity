import json

def test_product_crud_no_org(client):
    # Create without org (using organization_id in data)
    # First need an organization since products have FK to organizations
    org_data = {'name': 'Prod Org', 'slug': 'prod-org'}
    _, org_resp, _ = client.post('/api/organizations', data=org_data)
    org_id = org_resp['id']

    product_data = {
        'name': 'Test Product',
        'organization_id': org_id,
        'price': 100,
        'stock': 10
    }
    status_code, data, _ = client.post('/api/products', data=product_data)
    assert status_code == 201
    product_id = data['id']

    # Get
    status_code, data, _ = client.get(f'/api/products/{product_id}')
    assert status_code == 200
    assert data['name'] == 'Test Product'

    # Update
    update_data = {
        'name': 'Updated Product',
        'organization_id': org_id,
        'price': 150
    }
    status_code, data, _ = client.put(f'/api/products/{product_id}', data=update_data)
    assert status_code == 200

    # Delete
    status_code, data, _ = client.delete(f'/api/products/{product_id}')
    assert status_code == 200

def test_product_multi_tenancy(client):
    # Create two organizations
    _, org1, _ = client.post('/api/organizations', data={'name': 'Org 1', 'slug': 'org1'})
    _, org2, _ = client.post('/api/organizations', data={'name': 'Org 2', 'slug': 'org2'})
    
    org1_id = org1['id']
    org2_id = org2['id']

    # Create product in Org 1 using Header
    client.post('/api/products', data={'name': 'P1', 'price': 10}, headers={'X-Organization-Slug': 'org1'})
    
    # Create product in Org 2 using Header
    client.post('/api/products', data={'name': 'P2', 'price': 20}, headers={'X-Organization-Slug': 'org2'})

    # List products for Org 1
    status_code, data, _ = client.get('/api/products', headers={'X-Organization-Slug': 'org1'})
    assert status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == 'P1'

    # Try to access P1 with Org 2 context (should fail/be unauthorized if we implemented it)
    # Get P1 ID first
    p1_id = data[0]['id']
    status_code, data, _ = client.get(f'/api/products/{p1_id}', headers={'X-Organization-Slug': 'org2'})
    assert status_code == 403
