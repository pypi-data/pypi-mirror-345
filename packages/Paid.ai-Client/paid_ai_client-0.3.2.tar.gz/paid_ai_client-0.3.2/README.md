# AgentPaid Python SDK

Official Python SDK for the AgentPaid API.

## Installation

```bash
pip install paid-client
```

## Usage

```python
from paid_client import PaidClient

# Initialize the client
client = PaidClient(
    api_key='YOUR_API_KEY',
    api_url='YOUR_API_URL'  # Optional, defaults to production URL
)

# Example: Record usage
client.record_usage(
    'agent_id',
    'customer_id',
    'event_name',
    {'key': 'value'}
)
# Signals are automatically flushed:
# - Every 30 seconds
# - When the buffer reaches 100 events
# To manually flush:
client.flush()

# Example: Create a contact
contact = client.create_contact('org_id', {
    'customerId': 'customer_id',
    'firstName': 'John',
    'lastName': 'Doe',
    'email': 'john.doe@example.com',
    'phone': '+1234567890',
    'title': 'CTO',
    'department': 'Engineering'
})

# Example: Get a contact
contact = client.get_contact('org_id', 'contact_id')

# Example: List contacts
contacts = client.list_contacts('org_id')
# Or filter by customer
customer_contacts = client.list_contacts('org_id', customer_id='customer_id')

# Example: Create an order
order = client.create_order('org_id', {
    'customerId': 'customer_id',
    'name': 'Test Order',
    'OrderLine': [{
        'productId': 'product_id',
        'description': 'Test product line',
        'OrderLineAttribute': [{
            'productAttributeId': 'attribute_id',
            'pricing': {
                # ... pricing details
            }
        }]
    }]
})
```

## API Documentation

### Usage Recording
- `record_usage(agent_id: str, external_user_id: str, signal_name: str, data: Any) -> None`
- `flush() -> None`

### Orders
- `create_order(org_id: str, data: dict) -> Order`
- `get_order(org_id: str, order_id: str) -> Order`
- `list_orders(org_id: str) -> List[Order]`
- `update_order(org_id: str, order_id: str, data: dict) -> Order`
- `add_order_lines(org_id: str, order_id: str, lines: List[dict]) -> List[OrderLine]`
- `activate_order(org_id: str, order_id: str) -> None`

### Products
- `create_product(org_id: str, data: dict) -> Product`
- `get_product(org_id: str, product_id: str) -> Product`
- `list_products(org_id: str) -> List[Product]`
- `update_product(org_id: str, product_id: str, data: dict) -> Product`
- `delete_product(org_id: str, product_id: str) -> None`

### Customers
- `create_customer(org_id: str, data: dict) -> Customer`
- `get_customer(org_id: str, customer_id: str) -> Customer`
- `list_customers(org_id: str) -> List[Customer]`
- `update_customer(org_id: str, customer_id: str, data: dict) -> Customer`
- `delete_customer(org_id: str, customer_id: str) -> None`

### Contacts
- `create_contact(org_id: str, data: dict) -> Contact`
- `get_contact(org_id: str, contact_id: str) -> Contact`
- `list_contacts(org_id: str, customer_id: Optional[str] = None) -> List[Contact]`
