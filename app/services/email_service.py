import os

confirmed_reservation_body_template="""
Hello, {}
Your reservation for {} at {} has been confirmed.

Reservation Code: {}
Greetings,
    {}
"""

cancelled_reservation_body_template="""
Hello, {}
Unfortunately, your reservation for {} at {} has been cancelled.
Please contact our staff for more details

Reservation Code: {}
Sincerely,
    {}
"""

def send_reservation_confirmation_email(status,destination_email,reservation_id,origin_email=os.getenv("SQS_ORIGIN_EMAIL")):
    pass