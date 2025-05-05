# AgentPaid Python SDK

Official Python SDK for the AgentPaid API.

## Installation

```bash
pip install Paid.ai-Client
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
