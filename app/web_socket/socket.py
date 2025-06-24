from socketio import AsyncServer

from app.services.socket import SocketService
from app.dependencies.dependencies import get_socket_service


sio: AsyncServer = AsyncServer(async_mode='asgi', cors_allowed_origins="*")


socket_service: SocketService = get_socket_service()


@sio.event
async def connect(sid: str, environ: dict, auth: dict):
    pass #logs will be added


@sio.event
async def user_connected(sid: str, user_id: str):
    socket_service.user_sockets[user_id] = sid
    socket_service.user_activities[user_id] = "Idle"

    await sio.emit(event="user_connected",data=user_id,skip_sid=sid)

    await sio.emit(event="users_online",data=list(socket_service.user_sockets.keys()),to=sid)

    await sio.emit(event="activities",data=list(socket_service.user_activities.items()))


@sio.event
async def update_activity(sid: str, data: dict):
    user_id, activity = data['userId'], data['activity']
    socket_service.user_activities[user_id] = activity

    await sio.emit(event="activity_updated",data={"userId": user_id,"activity": activity})


@sio.event
async def send_message(sid: str, data: dict):
    sender_id, receiver_id, content = data['senderId'], data['receiverId'], data['content']

    try:
        message: dict = await socket_service.handle_message(sender_id=sender_id,receiver_id=receiver_id,content=content)

        receiver_sid: None | str = socket_service.user_sockets.get(receiver_id)
        if receiver_sid :
            await sio.emit(event="receive_message",data=message,to=receiver_sid)

        await sio.emit(event="message_sent",data=message,to=sid)

    except Exception as err:
        err_msg: str = str(err)
        await sio.emit(event="message_error",data=err_msg,to=sid)


@sio.event
async def disconnect(sid: str):
    disconnected_user_id: None | str = None

    disconnected_user_id = socket_service.remove_user(sid=sid)

    if disconnected_user_id:
        await sio.emit(event="user_disconnected",data=disconnected_user_id)

