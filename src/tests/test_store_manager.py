"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # 1. Créez un article (`POST /products`)
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                          data=json.dumps(product_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['product_id'] > 0 
    product_id = data['product_id']

    # 2. Ajoutez 5 unités au stock de cet article (`POST /stocks`)
    stock_data = {
        'product_id': product_id,
        'quantity': 5
    }
    response = client.post('/stocks',
                          data=json.dumps(stock_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    print(f"Stock initial: 5 unités")
    
    # 3. Vérifiez le stock (GET /stocks/:id)
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 201
    stock_before = response.get_json()
    assert stock_before['quantity'] == 5
    print(f"Vérification stock: {stock_before['quantity']} unités")
    
    # 4. Faites une commande de 2 unités (POST /orders)
    order_data = {
        'user_id': 1,
        'items': [{'product_id': product_id, 'quantity': 2}]
    }
    response = client.post('/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    order_id = response.get_json()['order_id']
    print(f"Commande créée avec ID: {order_id}")
    
    # 5. Vérifiez le stock après la commande (GET /stocks/:id)
    response = client.get(f'/stocks/{product_id}')
    stock_after_order = response.get_json()
    print(f"Stock après commande: {stock_after_order['quantity']} unités")
    assert stock_after_order['quantity'] == 3  # 5 - 2 = 3
    
    # 6. ÉTAPE EXTRA: Supprimez la commande
    response = client.delete(f'/orders/{order_id}')
    assert response.status_code == 200
    print(f"Commande supprimée")
    
    response = client.get(f'/stocks/{product_id}')
    stock_after_delete = response.get_json()
    print(f"Stock après suppression: {stock_after_delete['quantity']} unités")
    assert stock_after_delete['quantity'] == 5
    