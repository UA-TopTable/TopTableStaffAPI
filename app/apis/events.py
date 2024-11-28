import os
import boto3
from flask import request
from flask_socketio import emit


from app import socketio
from services.auth_service import get_user
from services.email_service import send_reservation_response_email
from services.db_service import get_all_restaurants_by_owner_email, get_reservation_by_id, update_reservation
from services.queue_service import delete_reservation_confirmation, get_reservation_confirmation



@socketio.on('listen_for_reservation_requests')
def listen_for_confirm_reservations(data):

    if 'x-amzn-oidc-accesstoken' in request.headers:
        access_token = request.headers.get('x-amzn-oidc-accesstoken')
    elif "access_token" in request.cookies:
        access_token=request.cookies.get("access_token")
    else:
        emit("not authenticated")
        return


    user=get_user(access_token)
    if user is None:
        emit("not authenticated")
        return
    
    email=user.get('email')
    restaurant_ids=get_all_restaurants_by_owner_email(email)

    if restaurant_ids is None:
        reservation_request=get_reservation_confirmation(restaurant_ids)

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
    receipt_handle=data["receipt_handle"]

    reservation=update_reservation(restaurant_id,reservation_id,"confirmed")

    if reservation is not None:
        socketio.emit("reservation_confirmed",{"reservation":reservation.as_dict()})

    delete_reservation_confirmation(receipt_handle)
    send_reservation_response_email("confirmed",sender_email,reservation_id)



@socketio.on("cancel_reservation")
def cancel_reservation(data):
    reservation_id=data["reservation_id"]
    restaurant_id=data["restaurant_id"]
    sender_email=data["sender_email"]
    receipt_handle=data["receipt_handle"]

    reservation=update_reservation(restaurant_id,reservation_id,"cancelled")

    if reservation is not None:
        socketio.emit("reservation_cancelled",{"reservation":reservation.as_dict()})
        
    delete_reservation_confirmation(receipt_handle)
    send_reservation_response_email("cancelled",sender_email,reservation_id)
        