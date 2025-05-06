import requests
from email.mime.base import MIMEBase
import re
from pathlib import Path
from .exeptions import MailTransportValidationError, MailTransportAPIError
DEFAULT_ATTACHMENT_MIME_TYPE = "application/octet-stream"
import mimetypes

class MailClient:
    """
    A client for interacting with the MailTransport API.
    """
    
    def Mail(self,
             to_emails: list=None,
             from_email: str=None,
             subject: str=None,
             html: str=None,
             cc: list=[],
             bcc: list=[],
             text: str=None,
             variables: dict={},
             template_id: str=None,
             reply_to: list=None,
             headers: dict={},
             attachments: list = None,
             in_reply_to: str=None):

        if self.is_valid_email_list(to_emails, 'to_emails'):
            self.to = to_emails
        self.html = html
        self.subject = subject
        if self.is_valid_email_list(cc, 'cc'):    
            self.cc = cc
        if self.is_valid_email_list(bcc, 'bcc'):    
            self.bcc=bcc
        self.from_email = from_email
        self.attachments = attachments
        self.text = text
        self.variables = variables
        self.templateId = template_id
        self.replyTo = reply_to
        self.inReplyTo = in_reply_to
        self.headers = headers
        
        return self
    
    def is_valid_email(self, email):
        """
        Validates if a string is a valid email address.
        """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return isinstance(email, str) and re.match(email_regex, email) is not None

    def is_valid_email_list(self, email_list, type):
        """
        Validates if the input is a list of valid email addresses.
        """
        if isinstance(email_list, str):
            email_list = email_list.split(",")
        if not isinstance(email_list, list):
            raise MailTransportValidationError({"error": f"Email {type} must be a list or comma separated string"})
        if not all(self.is_valid_email(email) for email in email_list):
            raise MailTransportValidationError({"error": f"Email {type} is not a valid email"})
        return True
    
    def attach_file(self, path, mimetype=None):
        """
        Attach a file from the filesystem.

        Set the mimetype to DEFAULT_ATTACHMENT_MIME_TYPE if it isn't specified
        and cannot be guessed.

        For a text/* mimetype (guessed or specified), decode the file's content
        as UTF-8. If that fails, set the mimetype to
        DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        path = Path(path)
        with path.open("rb") as file:
            content = file.read()
            self.add_attachment(path.name, content, mimetype)
    
    def add_attachment(self, filename=None, content=None, mimetype=None):
        """
        Attach a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass, insert it directly
        into the resulting message attachments.

        For a text/* mimetype (guessed or specified), when a bytes object is
        specified as content, decode it as UTF-8. If that fails, set the
        mimetype to DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        if isinstance(filename, MIMEBase):
            if content is not None or mimetype is not None:
                raise ValueError(
                    "content and mimetype must not be given when a MIMEBase "
                    "instance is provided."
                )
            self.attachments.append(filename)
        elif content is None:
            raise ValueError("content must be provided.")
        else:
            mimetype = (
                mimetype
                or mimetypes.guess_type(filename)[0]
                or DEFAULT_ATTACHMENT_MIME_TYPE
            )
            basetype, subtype = mimetype.split("/", 1)

            if basetype == "text":
                if isinstance(content, bytes):
                    try:
                        content = content.decode()
                    except UnicodeDecodeError:
                        # If mimetype suggests the file is text but it's
                        # actually binary, read() raises a UnicodeDecodeError.
                        mimetype = DEFAULT_ATTACHMENT_MIME_TYPE

            self.attachments.append((filename, content, mimetype))

    def validate(self):
        if not self.to:
            raise MailTransportValidationError({"error": "to field is required"})
        if not self.subject and not self.templateId:
            raise MailTransportValidationError({"error": "subject is optional if templateId is present and the template has a subject"})
        if not self.html and not self.templateId and not self.text:
            raise MailTransportValidationError({"error": "Html or text is required if the templateId is not provided"})


    def raise_or_fail_silently(self, data, fail_silently):
        if fail_silently:
            return data
        raise MailTransportAPIError({"error": data})

    def send(self, fail_silently=False):
        """
        Send the email with attachments.
        """
        
        url = f"{self.base_url}/transport/mails"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        self.validate()
        data = {
            "to": self.to,
            "from_email": self.from_email,
            "subject": self.subject,
            "html": self.html,
            "cc": self.cc,
            "bcc": self.bcc,
            "text": self.text,
            "variables": self.variables,
            "templateId": self.templateId,
            "replyTo": self.replyTo,
            "inReplyTo": self.inReplyTo,
            "headers": self.headers
        }

        # Prepare files for upload
        files = [("attachments", (filename, content),) for filename, content, _ in self.attachments]

        # Send the request
        response = requests.post(url, headers=headers, data=data, files=files)

        # Handle the response
        try:
            ok = response.ok
            resp_data =response.json()
            if ok:
                return resp_data
            return self.raise_or_fail_silently(resp_data, fail_silently)
        except Exception as e:
            return self.raise_or_fail_silently(str(e), fail_silently)
