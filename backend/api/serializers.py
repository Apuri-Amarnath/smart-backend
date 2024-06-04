import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinLengthValidator
from rest_framework import serializers, status

from .models import User, UserProfile, PersonalInformation, AcademicInformation, ContactInformation, College, Bonafide, \
    Subject, Semester

User = get_user_model()


class Csv_RegistrationSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        if not file.name.endswith('.csv'):
            return serializers.ValidationError('File must have .csv extension')
        return file


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('registration_number', 'role', 'password', 'password2',)
        extra_kwargs = {'password': {'write_only': True}}

    # validate password
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError(f"password and confirm password don't match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=20, validators=[MinLengthValidator(11)])

    class Meta:
        model = User
        fields = ['registration_number', 'password']


class ChangeUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, max_length=225)
    password2 = serializers.CharField(style={'input_type': 'password'}, max_length=225)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        user = self.context.get('user')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError(f"password and confirm password don't match")
        user.set_password(password)
        user.save()
        return attrs


class PersonalInfoSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = PersonalInformation
        exclude = ['id']
        read_only_fields = ['role', 'registration_number', 'user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'id': instance.user.id,
            'registration_number': instance.user.registration_number,
            'role': instance.user.role,
        }
        return representation

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Empty JSON payload is not allowed.")
        return attrs


class AcademicInfoSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)

    class Meta:
        model = AcademicInformation
        exclude = ['id']
        read_only_fields = ['registration_number', 'user']


class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        exclude = ['id']
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['registration_number', 'role']
        read_only_fields = ['registration_number', 'role']


class UserProfileSerializer(serializers.ModelSerializer):
    personal_information = PersonalInfoSerializer()
    contact_information = ContactInformationSerializer()
    academic_information = AcademicInfoSerializer()
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        exclude = ['id']
        read_only_fields = ['user']

    def update(self, instance, validated_data):
        personal_info_data = validated_data.pop('personal_information', {})
        contact_info_data = validated_data.pop('contact_information', {})
        academic_info_data = validated_data.pop('academic_information', {})
        user_data = validated_data.pop('user', {})

        # Update personal information
        personal_info = instance.personal_information
        for attr, value in personal_info_data.items():
            setattr(personal_info, attr, value)
        personal_info.save()

        # Update contact information
        contact_info = instance.contact_information
        for attr, value in contact_info_data.items():
            setattr(contact_info, attr, value)
        contact_info.save()

        # Update academic information
        academic_info = instance.academic_information
        for attr, value in academic_info_data.items():
            setattr(academic_info, attr, value)
        academic_info.save()

        return instance

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Empty JSON payload is not allowed.")
        return attrs


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'
        read_only_fields = ['roll_no']


class Base64ImageField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):

            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            return ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        elif isinstance(data, str):

            return ContentFile(base64.b64decode(data), name='temp')
        return data

    def to_representation(self, value):
        if value:
            return base64.b64encode(value).decode('utf-8')
        return None


class BonafideSerializer(serializers.ModelSerializer):
    supporting_document = Base64ImageField(required=False)

    college_details = CollegeSerializer(source='college', read_only=True)
    student_details = PersonalInfoSerializer(source='student', read_only=True)
    roll_no_details = serializers.CharField(source='roll_no.registration_number', read_only=True)

    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all(), write_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=PersonalInformation.objects.all(), write_only=True)
    roll_no = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Bonafide
        fields = '__all__'
        read_only_fields = ['student_details', 'college_details', 'bonafide_number', 'applied_date']

    def create(self, validated_data):
        supporting_document = validated_data.pop('supporting_document', None)
        instance = super().create(validated_data)
        if supporting_document:
            instance.supporting_document = supporting_document.read()
            instance.save()
        return instance

    def update(self, instance, validated_data):
        supporting_document = validated_data.pop('supporting_document', None)
        instance = super().update(instance, validated_data)
        if supporting_document:
            instance.supporting_document = supporting_document.read()
            instance.save()
        return instance

    def validate(self, attrs):
        student_value = attrs.get('student')
        roll_no_value = attrs.get('roll_no')
        if student_value != roll_no_value:
            raise serializers.ValidationError('student and roll_no should be the same')
        return attrs


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class SemesterSerializer(serializers.ModelSerializer):
    subject_codes = serializers.ListField(child=serializers.CharField(), write_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'semester_name', 'subjects', 'subject_codes', 'branch']

    def create(self, validated_data):
        subject_codes = validated_data.pop('subject_codes')
        subjects = Subject.objects.filter(subject_code__in=subject_codes)
        semester = Semester.objects.create(**validated_data)
        semester.subjects.add(*subjects)

        return semester

    def update(self, instance, validated_data):
        subject_codes = validated_data.pop('subject_code', None)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.semester_name = validated_data.get('semester_name', instance.semester_name)
        instance.save()

        if subject_codes is not None:
            subjects = Subject.objects.filter(subject_code__in=subject_codes)
            instance.subjects.set(subjects)

        return instance
