from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from rest_framework import serializers, status

from .models import User,UserProfile,PersonalInformation,AcademicInformation,ContactInformation
User = get_user_model()
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ('registration_number', 'role', 'password','password2',)
        extra_kwargs = {'password': {'write_only':True}}
#validate password
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError(f"password and confirm don't match")
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=20,validators=[MinLengthValidator(11)])
    class Meta:
        model = User
        fields = ['registration_number', 'password']

class PersonalInfoSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number',read_only=True)
    role = serializers.CharField(source='user.role',read_only=True)
    class Meta:
        model = PersonalInformation
        exclude = ['id']
        read_only_fields = ['role', 'registration_number']

class AcademicInfoSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number',read_only=True)
    class Meta:
        model = AcademicInformation
        exclude = ['id']
        read_only_fields = ['registration_number']
class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        exclude = ['id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['registration_number', 'role']
class UserProfileSerializer(serializers.ModelSerializer):
    personal_information = PersonalInfoSerializer()
    contact_information = ContactInformationSerializer()
    academic_information = AcademicInfoSerializer()
    user = UserSerializer()

    class Meta:
        model = UserProfile
        exclude = ['id']
        read_only_fields = ['user']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            self.Meta.model.__name__: representation
        }
    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Empty JSON payload is not allowed.")
        return attrs
