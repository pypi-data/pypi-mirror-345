# MailTransport

MailTransport is a Python package designed to simplify email transport and management. It provides an easy-to-use interface for sending emails with support for advanced configurations, attachments, and error handling.

## Features

- Send emails with HTML content, plain text, or both.
- Add CC, BCC, and reply-to addresses.
- Attach files with automatic MIME type detection.
- Use templates with dynamic variables.
- Validate email addresses and handle errors gracefully.
- Easy integration with Python applications.

## Installation

Install the package using pip:

```bash
pip install mailtransport
```

## Quick Start

Here’s how you can get started with MailTransport:

### Import and Initialize

```python
from mailtransport import MailTransportClient

# Initialize the client with your API key
transport = MailTransportClient(api_key="your_api_key")
```

### Send Email


### Send a Simple Email

```python
from mailtransport import MailTransportClient

# Initialize the client with your API key
transport = MailTransportClient(api_key="your_api_key")

email_instance = transport.Mail(
    to_emails=['recipient@example.com'],
    from_email="noreply@company.com",
    html="<b>This is a test email</b>",
    subject="Test Email",
)
email_instance.send()
```

NB: For advanced usage with all the parameters, navigate to [Mailtransport docs](https://docs.mailtransportai.com/#tag/Send-Emails/paths/~1transport~1mails/post) to see full documentations

## Advanced Usage

### Sending Emails with Attachments

You can attach files to your email using the `attach_file` or `add_attachment` methods:

```python
email_instance = transport.Mail(
    to_emails=['recipient@example.com'],
    from_email="noreply@company.com",
    subject="Email with Attachment",
    html="<b>Please find the attachment below.</b>"
)

# Attach a file from the filesystem
email_instance.attach_file("path/to/file.pdf")

# Attach a file with custom content and MIME type
email_instance.add_attachment(
    filename="example.txt",
    content="This is the content of the file.",
    mimetype="text/plain"
)

email_instance.send()
```

### Using Templates with Variables

You can use templates and pass dynamic variables for personalized emails:

```python
email_instance = transport.Mail(
    to_emails=['recipient@example.com'],
    from_email="noreply@company.com",
    template_id="template_12345",
    variables={"name": "John Doe", "order_id": "123456"}
)

email_instance.send()
```

### Adding CC, BCC, and Reply-To Addresses

```python
email_instance = transport.Mail(
    to_emails=['recipient@example.com'],
    from_email="noreply@company.com",
    subject="Email with CC and BCC",
    html="<b>This email has CC and BCC recipients.</b>",
    cc=['cc@example.com'],
    bcc=['bcc@example.com'],
    reply_to="replyto@example.com"
)

email_instance.send()
```

## Identity Management

The `IdentityClient` allows you to manage identities (e.g., domains or email addresses) for your email transport.

### Create an Identity

```python
from mailtransport import MailTransportClient

# Initialize the client with your API key
transport = MailTransportClient(api_key="your_api_key")

response = transport.identity.create(domain_name="example.com")
print(response)
```

### Get an Identity

```python
identity_id = "12345"
response = transport.identity.get(identity_id)
print(response)
```

### List All Identities

```python
response = transport.identity.list()
print(response)
```


### Delete an Identity

```python
identity_id = "12345"
response = transport.identity.delete(identity_id)
print(response)
```

### Verify an Identity

```python
identity_id = "12345"
response = transport.identity.verify(identity_id)
print(response)
```

### Error Handling

MailTransport provides detailed error messages for failed email deliveries. Use try-except blocks to handle errors gracefully:

```python
from mailtransport.exceptions import MailTransportValidationError, MailTransportAPIError

try:
    email_instance.send()
except MailTransportValidationError as e:
    print(f"Failed to send email due to incoreect input details: {e}")
except MailTransportAPIErroras e:
    print(f"Failed to send email due to api errors: {e}")
```

## Methods Overview

### `MailClient.Mail()`

Creates a new email instance with the following parameters:

- `to_emails` (list or str): List of recipient email addresses.
- `from_email` (str): Sender's email address.
- `subject` (str): Subject of the email.
- `html` (str): HTML content of the email.
- `text` (str, optional): Plain text content of the email.
- `cc` (list, optional): List of CC email addresses.
- `bcc` (list, optional): List of BCC email addresses.
- `variables` (dict, optional): Variables for email templates.
- `template_id` (str, optional): Template ID for the email.
- `reply_to` (str, optional): Reply-to email address.
- `in_reply_to` (str, optional): Message ID this email is replying to.

### `MailClient.attach_file(path, mimetype=None)`

Attaches a file from the filesystem. The MIME type is automatically detected if not provided.

### `MailClient.add_attachment(filename, content, mimetype=None)`

Attaches a file with custom content and MIME type.

### `MailClient.send(fail_silently=False)`

Sends the email. If `fail_silently` is `False`, raises an exception on failure.

### `MailClient.is_valid_email(email)`

Validates a single email address.

### `MailClient.is_valid_email_list(email_list, type)`

Validates a list of email addresses.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For support or inquiries, please contact us at [support@mailtransportai.com](mailto:support@mailtransportai.com).

## Documentation

For full documentation, visit the [MailTransport Documentation](https://docs.mailtransportai.com).

---
Happy emailing with MailTransport!
