import json
import os
import sys
import boto3
from flask import request
from flask_socketio import emit, join_room, leave_room


from app import socketio
from services.auth_service import get_user
from services.email_service import send_reservation_response_email
from services.db_service import get_all_restaurants_by_owner_email, get_reservation_by_id, get_restaurant, get_restaurant_by_owner, get_table_by_id, get_user_by_id, update_reservation
from services.queue_service import delete_reservation_confirmation, get_reservation_confirmation


def broadcast_sns_messages():
    while True:
        reservation_request=get_reservation_confirmation()

        if(reservation_request is not None):
            reservation=get_reservation_by_id(json.loads(reservation_request["Body"].replace("'",'"'))["reservation"])
            print(f"reservation: {reservation}",file=sys.stderr)
            if reservation is None:
                print("reservation is empty",file=sys.stderr)
                continue

            if reservation["status"]!="pending":
                print("reservation is not pending",file=sys.stderr)
                continue

            customer=get_user_by_id(reservation["user_id"])
            if customer is None:
                print("customer not found",file=sys.stderr)
                continue

            restaurant=get_restaurant(reservation["restaurant_id"],as_json=False)[0]

            if restaurant is None:
                print("restaurant not found",file=sys.stderr)
                continue

            table=get_table_by_id(reservation["dining_table_id"])

            if table is None:
                print("table not found",file=sys.stderr)
                continue

            socketio.emit('reservation_request',{
                "restaurant_id":reservation.get("restaurant_id"),
                "reservation":reservation,
                "restaurant":restaurant.as_dict(),
                "table":table.as_dict(),
                "receipt_handle":reservation_request["ReceiptHandle"],
                "sender_email": customer.email
            },to=restaurant.id) #emit to the restaurant's room

@socketio.on('disconnect')
def disconnect():
    #I don't know if sockets can disconnect by themselves, but it's usually considered good practice to have a disconnect event

    if 'x-amzn-oidc-accesstoken' in request.headers:
        access_token = request.headers.get('x-amzn-oidc-accesstoken')
    elif "access_token" in request.cookies:
        access_token=request.cookies.get("access_token")
    else:
        return
    
    user=get_user(access_token)
    if user is None:
        return
    
    restaurant_ids=[restaurant.get('id') for restaurant in get_restaurant_by_owner(user.get('id'))]
    for restaurant_id in restaurant_ids:
        leave_room(restaurant_id)
        print(f"left room {restaurant_id}",file=sys.stderr)
    print("disconnected",file=sys.stderr)
        

@socketio.on('connect')
def connect():
    #since the only socket event is this one, we can just have the listen here
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

    restaurant_ids=[restaurant.get('id') for restaurant in get_restaurant_by_owner(user.get('id'))]
    print(f"restaurant ids: {restaurant_ids}",file=sys.stderr)
    for restaurant_id in restaurant_ids:
        join_room(restaurant_id)
        print(f"joined room {restaurant_id}",file=sys.stderr)

@socketio.on("confirm_reservation")
def confirm_reservation(data):
    print(data,file=sys.stderr)
    reservation_id=data["reservation_id"]
    restaurant_id=data["restaurant_id"]
    sender_email=data["sender_email"]
    receipt_handle=data["receipt_handle"]

    reservation=update_reservation(restaurant_id,reservation_id,"confirmed")

    if reservation is not None:
        socketio.emit("reservation_confirmed",{"reservation":reservation.as_dict()})

    #because I am using sandbox, I lack the permissions to delete messages
    #delete_reservation_confirmation(receipt_handle,queue_url=os.getenv("SQS_RESERVATION_RESQUESTS_QUEUE_URL"))
    
    #would work if we got authorization from AWS, but we don't
    #send_reservation_response_email("cancelled",sender_email,reservation_id)



@socketio.on("cancel_reservation")
def cancel_reservation(data):
    print(data,file=sys.stderr)
    reservation_id=data["reservation_id"]
    restaurant_id=data["restaurant_id"]
    sender_email=data["sender_email"]
    receipt_handle=data["receipt_handle"]

    reservation=update_reservation(restaurant_id,reservation_id,"cancelled")

    if reservation is not None:
        socketio.emit("reservation_cancelled",{"reservation":reservation.as_dict()})

    #because I am using sandbox, I lack the permissions to delete messages
    #delete_reservation_confirmation(receipt_handle,queue_url=os.getenv("SQS_RESERVATION_RESQUESTS_QUEUE_URL"))

    #would work if we got authorization from AWS, but we don't
    #send_reservation_response_email("cancelled",sender_email,reservation_id)
        