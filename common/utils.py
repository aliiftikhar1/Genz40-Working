import threading
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
import os
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from twilio.rest import Client

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_otp(phone_number):
    """Send OTP via Twilio"""
    verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verifications.create(to=phone_number, channel="sms")
    return verification.status  # Expected: "pending"

def verify_otp(phone_number, otp_code):
    """Verify OTP via Twilio"""
    verification_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verification_checks.create(to=phone_number, code=otp_code)
    return verification_check.status  # Expected: "approved" if successful



class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send()


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.JPG']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def message_content(first_name, last_name, message):
    return first_name+' '+last_name+' '+message


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_custom_email(template_name, subject, message, recipient_list, from_email=None, html_message=None):
    """
    Sends an email using Django's send_mail function.

    Parameters:
    - subject: Subject of the email
    - message: Plain text message of the email
    - recipient_list: List of recipient email addresses
    - from_email: Sender's email address (defaults to settings.ADMIN_EMAIL)
    - html_message: HTML message of the email (optional)
    """
    if from_email is None:
        from_email = settings.ADMIN_EMAIL
        html_message = render_to_string(template_name, message)
        plain_message = strip_tags(html_message)
    send_mail(
        template_name,
        subject,
        plain_message,
        from_email,
        recipient_list,
        fail_silently=False,
        html_message=html_message,
    )