from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
  class Meta:
    model = Member
    fields = (
      'id',
      'image',
      'email',
      'type',
      'first_name',
      'last_name',
      'full_name',
      'sex',
      'telnumber',
      'birth_date',
      'password',
      'active_notification',
      'confirmed',
      'plat_form',
      'udid',
      'login_date',
      'banned',
      'banned_date',
      'is_valid_email',
      'is_edit_viewer',
      'api_key',
      'updated_at',
      'created_at',
    )
    read_only_fields = (
      'id',
      'login_date',
      'banned',
      'banned_date',
      'api_key',
      'updated_at',
      'created_at',
    )