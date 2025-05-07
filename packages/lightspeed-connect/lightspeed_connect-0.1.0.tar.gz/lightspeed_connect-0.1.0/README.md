# Lightspeed Connect

A Python client for the Lightspeed Connect trading API.

- Supports placing and managing orders via WebSocket.
- Built for speed, extensibility, and clarity.
- Compatible with equities and options.

## ⚠️ Disclaimer

This library is unofficial and not affiliated with Lightspeed Financial Services Group LLC.  
Use at your own risk.


## 📦 Installation


```bash
pip install lightspeed-connect
```

## 🚀 Quickstart Example

```python
from lightspeed_connect import LightspeedClient, OrderSingle, Side, OrderType

# Initialize the client
client = LightspeedClient(
    url="wss://api-cert.lightspeed.com/v1/ws",  # Use certification or production endpoint
    api_key="your_api_key"
)

# Connect
client.connect()

# Create an order
order = OrderSingle(
    symbol="GOOGL",
    side=Side.BUY,
    order_qty=10,
    order_type=OrderType.LIMIT,
    price=2700.00
)

# Send the order
client.send_order(order)
```


## 🛠️ Features

- ✅ WebSocket-based connection
- ✅ Submit `OrderSingle` types
- ✅ Extendable for multileg and cancels
- ✅ Full UUID support
- ✅ Lightweight and dependency-minimal

## 📄 License

This project is licensed under the [MIT License](LICENSE).
