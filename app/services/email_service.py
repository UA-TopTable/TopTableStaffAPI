import os
import sys

from flask_mail import Message

from services.db_service import get_reservation_by_id, get_restaurant, get_user_by_id
from app import mail

confirmed_reservation_body_template="""
Hello, {}
Your reservation for {} at {} has been confirmed.

Reservation Code: {}
Greetings,
    TopTable
"""

cancelled_reservation_body_template="""
Hello, {}
Unfortunately, your reservation for {} at {} has been cancelled.
Please contact our staff for more details

Reservation Code: {}
Sincerely,
    TopTable
"""

def send_reservation_response_email(status,destination_email,reservation_id,origin_email=os.getenv("MAIL_USERNAME")):
    reservation=get_reservation_by_id(reservation_id)
    customer=get_user_by_id(reservation["user_id"]).as_dict()
    restaurant=get_restaurant(reservation["restaurant_id"])[0]

    if status=="confirmed":
        print("sending confirmation email",file=sys.stderr)
        msg=Message(
            sender=origin_email,
            subject="Reservation Confirmed",
            recipients=[destination_email],
            body=confirmed_reservation_body_template.format(  
                customer["full_name"],
                restaurant["name"],
                reservation["reservation_start_time"],
                reservation["reservation_code"],
                origin_email
            )
        )
    else:
        print("sending cancellation email",file=sys.stderr)
        msg=Message(
            sender=origin_email,
            subject="Reservation Cancelled",
            recipients=[destination_email],
            body=cancelled_reservation_body_template.format(
                customer["full_name"],
                restaurant["name"],
                reservation["reservation_start_time"],
                reservation["reservation_code"],
                origin_email
            )
        )

    mail.send(msg)