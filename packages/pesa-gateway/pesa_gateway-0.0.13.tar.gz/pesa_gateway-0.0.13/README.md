
## Usage Examples

### 1. M-Pesa Integration & Configuration

```python
from pesa_gateway import MPesaClient

client = MPesaClient(
    consumer_key="your_consumer_key",  # or use env MPESA_CONSUMER_KEY
    consumer_secret="your_consumer_secret",  # or use env MPESA_CONSUMER_SECRET
    shortcode="your_shortcode",  # or use env MPESA_SHORTCODE
    passkey="your_passkey",  # or use env MPESA_PASSKEY
    environment="sandbox"  # or use env MPESA_ENVIRONMENT ("sandbox" or "production")
)
```

### 2. STK Push (Lipa Na M-Pesa Online)

```python
response = client.stk_push_request(
    data={
        "amount": 100,
        "phone_number": "254713164545",
        "account_reference": "test",
        "transaction_description": "test",
        "callback_url": "https://example.com/callback",
    }
)
```

### 3. C2B (Customer to Business)

```python
# Register C2B URLs
client.customer_to_business_register_url(
    data={
        "shortcode": "your_shortcode",
        "response_type": "Completed",
        "confirmation_url": "https://yourdomain.com/confirmation",
        "validation_url": "https://yourdomain.com/validation"
    }
)

# Simulate C2B payment (for sandbox/testing)
client.simulate_c2b_payment(
    data={
        "shortcode": "your_shortcode",
        "command_id": "CustomerPayBillOnline",
        "amount": 100,
        "msisdn": "2547XXXXXXXX",
        "bill_ref_number": "INV123"
    }
)
```

### 4. B2B (Business to Business)

```python
response = client.business_to_business_payment(
    data={
        "amount": 1000,
        "party_a": "123456",
        "party_b": "000000",
        "account_reference": "B2BREF",
        "initiator": "test",
        "requester": "254700000000",
        "remarks": "Payment to supplier",
        "occassion": "test",
        "queue_timeout_url": "https://yourdomain.com/timeout",
        "result_url": "https://yourdomain.com/result"
    }
)
```

### 5. B2C (Business to Customer)

```python
response = client.business_to_customer_payment(
    data={
        "initiator": "test",
        "security_credential": "credential",
        "amount": 500,
        "party_a": "shortcode",
        "party_b": "2547XXXXXXXX",
        "remarks": "Salary payment",
        "queue_timeout_url": "https://yourdomain.com/timeout",
        "result_url": "https://yourdomain.com/result",
        "occasion": "test"
    }
)
```

### 6. Transaction Status Query

```python
status = client.query_transaction_status(
    data={
        "initiator": "test",
        "transaction_id": "LKXXXXXX",
        "remarks": "test",
        "occassion": "test",
        "result_url": "https://yourdomain.com/result",
        "queue_timeout_url": "https://yourdomain.com/timeout"
    }
)
```

### 7. Account Balance Query

```python
balance = client.account_balance(
    data={
        "remarks": "test",
        "initiator": "test",
        "queue_timeout_url": "https://yourdomain.com/timeout",
        "result_url": "https://yourdomain.com/result"
    }
)
```

### 8. Transaction Reversal

```python
reversal = client.reverse_transaction(
    data={
        "initiator": "test",
        "transaction_id": "LKXXXXXX",
        "amount": 100,
        "remarks": "Erroneous payment",
        "occassion": "test",
        "result_url": "https://yourdomain.com/result",
        "queue_timeout_url": "https://yourdomain.com/timeout"
    }
)
```

### 9. Dynamic QR Code Generation

```python
qr_code = client.generate_dynamic_qr_code(
    data={
        "merchant_name": "test",
        "ref_no": "test",
        "amount": 100,
        "trx_code": "PB",
        "cpi": "789621",
        "size": "300"
    }
)
```

### 10. Phone Number Validation

```python
from pesa_gateway.utils import validate_phone_number

is_valid = validate_phone_number("2547XXXXXXXX")
```
