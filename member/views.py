from django.db.models import Q, Sum, Max
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# from dentist_profile.models import DentistProfile

from utils.pagination_utils import (
  FilterPagination,
  get_queryset_from_request
)


from .models import Member
from .serializers import (
  MemberSerializer
)



from utils.member_utils import generate_password, generate_api_key
# from utils.email_utils import send_email_member_password

class MemberList(APIView):
  permission_classes = []

  @swagger_auto_schema(
    manual_parameters=FilterPagination.generate_pagination_params(),
    responses={200: MemberSerializer(many=True)}
  )
  def get(self, request, format=None):
    resultset = FilterPagination.get_paniation_data(
      request,
      Member,
      MemberSerializer,
      queries=None,
      order_by_array=('-id',)
    )
    return Response(resultset)


class MemberDetail(APIView):
  def get_object(self, pk):
    try:
      return Member.objects.get(pk=pk)
    except Member.DoesNotExist:
      raise Http404

  @swagger_auto_schema(
    responses={200: MemberSerializer(many=False)}
  )
  def get(self, request, pk, format=None):
    item = self.get_object(pk)
    serializer = MemberSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @swagger_auto_schema(
    request_body=MemberSerializer(many=False),
    responses={200: MemberSerializer(many=False)}
  )
  def put(self, request, pk, format=None):
    item = self.get_object(pk)
    serializer = MemberSerializer(item, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    item = self.get_object(pk)
    # Delete all patients
    item.dentist_patients.all().delete()
    item.delete()
    return Response(status=status.HTTP_200_OK)


class MemberCreate(APIView):
  @swagger_auto_schema(
      request_body=MemberSerializer(many=False),
      responses={200: MemberSerializer(many=False)}
  )
  def post(self, request, format=None):
    serializer = MemberSerializer(data=request.data, many=False)
    if serializer.is_valid():
      # Create new member with serializer
      new_item = Member.objects.create(**serializer.validated_data)

      #make authorization edit viewer 
      if new_item.type == "DENTIST":
        new_item.is_edit_viewer = False
      else:
        new_item.is_edit_viewer = True
      
      # Generate password
      new_item.password = generate_password()
      # Generate api key
      new_item.api_key = generate_api_key(new_item)
      if 'referent' in request.data:
        new_item.referent = request.data['referent']
      new_item.save()
      # Send email
      # send_email_member_password(new_item, True)
      new_serializer = MemberSerializer(new_item, many=False)
      return Response(new_serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
