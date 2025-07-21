import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Member
from asgiref.sync import sync_to_async
from django.http import Http404

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.member_id = self.scope['url_route']['kwargs']['member_id']
        
        if self.member_id == "all":
            self.group_name = "all_members"
        else:
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
        if self.member_id == "all":
            return

        data = json.loads(text_data)
        lat = data.get('lat')
        lon = data.get('lon')

        member_obj = await sync_to_async(self.get_object)(pk=int(self.member_id))

        userInformation = {
            "id": member_obj.id,
            "email": member_obj.email,   
            "first_name": member_obj.first_name,
            "last_name": member_obj.last_name,
            "telnumber": member_obj.telnumber,   
        }

        message_to_send = {
            # 'type': 'localisation',
            'lat': lat,
            'lon': lon,
            'from': userInformation,
        }

        followers = await sync_to_async(self.get_followers)(self.member_id)

        for follower_id in followers:
            await self.channel_layer.group_send(
                f"member_{follower_id}",
                {
                    'type': 'send_notification',
                    'message': message_to_send
                }
            )

        await self.channel_layer.group_send(
            "all_members",
            {
                'type': 'send_notification',
                'message': message_to_send
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
        
        
    def get_object(self, pk=None, user=None):
        try:
            # return Member.objects.get(pk=pk)
            if pk is not None:
                return Member.objects.get(pk=pk)
            elif user is not None:
                return Member.objects.get(pk=user.id)
            else:
                raise Http404
            
        except Member.DoesNotExist:
            raise Http404
