import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Member
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.member_id = self.scope['url_route']['kwargs']['member_id']
        self.group_name = f"member_{self.member_id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        lat = data.get('lat')
        lon = data.get('lon')
        num = data.get('num')

        # Obtenir les followers
        followers = await sync_to_async(self.get_followers)(self.member_id)

        for follower_id in followers:
            await self.channel_layer.group_send(
                f"member_{follower_id}",
                {
                    'type': 'send_notification',
                    'message': {
                        'type': message_type,
                        'lat': lat,
                        'lon': lon,
                        'num': num,
                        'from': self.member_id,
                    }
                }
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    def get_followers(self, member_id):
        try:
            member = Member.objects.get(pk=member_id)
            return list(member.following.all().values_list('id', flat=True))
        except Member.DoesNotExist:
            return []
