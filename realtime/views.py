from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from member.models import Member
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ESP32MessageReceiver(APIView):
    permission_classes = []
    
    def post(self, request):
        sender_id = request.data.get("sender_id")
        message = request.data.get("message")

        try:
            sender = Member.objects.get(pk=sender_id)
        except Member.DoesNotExist:
            return Response({"error": "Membre non trouvé"}, status=404)

        # channel_layer = get_channel_layer()
        # for follower in sender.followers.all():
        #     async_to_sync(channel_layer.group_send)(
        #         f"user_{follower.id}",
        #         {
        #             "type": "send_notification",
        #             "message": message,
        #             "from": sender.email
        #         }
        #     )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "test_group",  # Même nom que dans connect()
            {
                "type": "send_notification",
                "message": message,
                "from": sender.email
            }
        )


        return Response({"status": "message relayed"}, status=200)
