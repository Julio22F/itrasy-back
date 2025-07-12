from channels.generic.websocket import AsyncWebsocketConsumer
import json

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         user = self.scope["user"]
#         if user.is_authenticated:
#             self.group_name = f"user_{user.id}"
#             await self.channel_layer.group_add(self.group_name, self.channel_name)
#             await self.accept()
#         else:
#             await self.close()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'from': event['from']
#         }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Permettre la connexion sans authentification
        self.group_name = "test_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "from": event["from"]
        }))

