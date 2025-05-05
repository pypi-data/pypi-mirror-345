# TextTalk Communication Library

A Python library for sending SMS, email and WhatsApp messages. This package provides a simple and efficient interface for sending both individual and bulk messages across multiple communication channels.

## Features

- Send individual and bulk SMS messages
- Send individual and bulk email messages 
- Send individual and bulk WhatsApp messages
- Configurable through environment variables or direct configuration
- Comprehensive error handling
- Type hints for better IDE support
- Simple and intuitive API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chat
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You can configure the SMS client in two ways:

### 1. Using Environment Variables

Set the following environment variables:

```bash
export SMS_API_KEY='your_api_key'
export SMS_PARTNER_ID='your_partner_id'
export SMS_SHORTCODE='your_shortcode'
```

### 2. Using Direct Configuration

```python
from sms import SMSConfig

config = SMSConfig(
    api_key='your_api_key',
    partner_id='your_partner_id',
    shortcode='your_shortcode'
)
```

## Usage

### Basic Usage

```python
from sms import SMSClient

# Using environment variables
client = SMSClient()

# Send a single SMS
success = client.send_sms(
    to_number='+254713164545',
    message='Hello from TextTalk!'
)

# Send bulk SMS
success = client.send_bulk_sms(
    message='Hello from TextTalk!',
    to_numbers=['+254713164545', '+254713164546']
)
```

### With Custom Configuration

```python
from sms import SMSClient, SMSConfig

config = SMSConfig(
    api_key='your_api_key',
    partner_id='your_partner_id',
    shortcode='your_shortcode'
)

client = SMSClient(config)
```

## Error Handling

The library provides custom exceptions for better error handling:

```python
from sms import SMSClient, SMSException, ConfigurationError, MessageError

try:
    client = SMSClient()
    client.send_sms(to_number='+254713164545', message='Hello!')
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except MessageError as e:
    print(f"Message error: {e}")
except SMSException as e:
    print(f"General SMS error: {e}")
```

## API Reference

### SMSClient

#### `__init__(config: Optional[SMSConfig] = None)`

Initialize the SMS client with configuration.

#### `send_sms(to_number: str, message: str) -> bool`

Send a single SMS message.

**Parameters:**
- `to_number` (str): The recipient's phone number
- `message` (str): The message content

**Returns:**
- `bool`: True if the message was sent successfully

#### `send_bulk_sms(message: str, to_numbers: List[str]) -> bool`

Send SMS messages to multiple recipients.

**Parameters:**
- `message` (str): The message content
- `to_numbers` (List[str]): List of recipient phone numbers

**Returns:**
- `bool`: True if the messages were sent successfully

### SMSConfig

Configuration class for managing API credentials and settings.

**Parameters:**
- `api_key` (Optional[str]): API key for authentication
- `partner_id` (Optional[str]): Partner ID for the service
- `shortcode` (Optional[str]): Shortcode for sending messages

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
