import os
import boto3
from flask_socketio import SocketIO

from services.db_service import get_all_restaurants_by_owner_email, get_reservation_by_id, update_reservation
from services.queue_service import poll_queue

socketio=SocketIO()

@socketio.on('listen_for_reservation_requests')
def listen_for_confirm_reservations(data):
    email=data["email"]
    restaurant_ids=get_all_restaurants_by_owner_email(email)

    if restaurant_ids is None:
        reservation_request=poll_queue(restaurant_ids)

        if reservation_request is not None:
            reservation=get_reservation_by_id(int(reservation_request["MessageAttributes"]["reservation_id"]["StringValue"]))

            if reservation is not None:
                socketio.emit('reservation_request',{
                    "restaurant_id":reservation.restaurant_id,
                    "reservation":reservation.as_dict(),
                    "receipt_handle":reservation_request["ReceiptHandle"],
                    "sender_email": reservation_request["MessageAttributes"]["senderEmail"]["StringValue"]
                })

@socketio.on("confirm_reservation")
def confirm_reservation(data):
    reservation_id=data["reservation_id"]
    restaurant_id=data["restaurant_id"]
    sender_email=data["sender_email"]

    reservation=update_reservation(restaurant_id,reservation_id,"confirmed")

    if reservation is not None:
        socketio.emit("reservation_confirmed",{"reservation":reservation.as_dict()})



@socketio.on("cancel_reservation")
def cancel_reservation(data):
    reservation_id=data["reservation_id"]
    restaurant_id=data["restaurant_id"]
    sender_email=data["sender_email"]

    reservation=update_reservation(restaurant_id,reservation_id,"cancelled")

    if reservation is not None:
        socketio.emit("reservation_cancelled",{"reservation":reservation.as_dict()})
        