import base64
import logging
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import List, Optional

def send_gmail(
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    token_path: str,
    html_body: bool = False,
    image_paths: Optional[List[str]] = None,
    attachment_paths: Optional[List[str]] = None
    ):

    """
    This function sends an email using the Gmail API.
    Args:
        sender: str: The email address of the sender.
        recipient: str: The email address of the recipient.
        subject: str: The subject of the email.
        body: str: The body of the email.
        token_path: str: The path to the credentials file.
        html_body: bool: Whether the body is HTML or plain text.
        image_paths: List[str]: A list of paths to images to attach to the email.
        attachment_paths: List[str]: A list of paths to files to attach to the email.
    Returns:
        None
    """
    
    # Initialize the message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html' if html_body else 'plain'))

    # Attach images
    if image_paths:
        for idx, image_path in enumerate(image_paths):
            try:
                with open(image_path, 'rb') as img:
                    mime_img = MIMEImage(img.read())
                    mime_img.add_header('Content-ID', f'<image{idx}>')
                    msg.attach(mime_img)
            except Exception as e:
                logging.error(f"Error attaching image {image_path}: {e}")
                raise

    # Attach other files
    if attachment_paths:
        for attachment_path in attachment_paths:
            try:
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{attachment_path.split("/")[-1]}"')
                    msg.attach(part)
            except Exception as e:
                logging.error(f"Error attaching file {attachment_path}: {e}")
                raise

    # Encode the message
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    message = {'raw': raw_message}

    # Send the email
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        service = build('gmail', 'v1', credentials=creds)
        service.users().messages().send(userId='me', body=message).execute()
        time.sleep(0.5) # api rate limit 2.5 emails per second (https://developers.google.com/gmail/api/reference/quota)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise