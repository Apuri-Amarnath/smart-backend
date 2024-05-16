from rest_framework import serializers, status

from .models import User,UserProfile
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
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=10)
    class Meta:
        model = User
        fields = ['registration_number', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number',read_only=True)
    role = serializers.CharField(source='user.role',read_only=True)
    class Meta:
        model = UserProfile
        fields = ['role','registration_number','f_name','l_name','bio','education']
        read_only_fields = ['role','registration_number']
    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Empty JSON payload is not allowed.")
        return attrs