import base64
from datetime import datetime
import re

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework import serializers, status
from django.utils import timezone
import logging

from rest_framework.exceptions import ValidationError

from .models import User, UserProfile, PersonalInformation, AcademicInformation, ContactInformation, College, Bonafide, \
    Subject, Semester, Semester_Registration, Hostel_Allotment, Hostel_No_Due_request, Hostel_Room_Allotment, \
    Guest_room_request, Complaint, Fees_model, Mess_fee_payment, Overall_No_Dues_Request, No_Dues_list, \
    Departments_for_no_Dues, VerifySemesterRegistration, TransferCertificateInformation, Notification, \
    Cloned_Departments_for_no_Dues, CollegeRequest, College_with_Ids, Branch, HostelRooms

User = get_user_model()
logger = logging.getLogger(__name__)


class YearMonthField(serializers.DateTimeField):
    def __init__(self, **kwargs):
        kwargs['input_formats'] = ['%Y-%m']
        super().__init__(**kwargs)

    def to_representation(self, value):
        if value:
            return value.strftime('%Y-%m')
        return None

    def to_internal_value(self, data):
        try:
            return datetime.strptime(data + '-01', '%Y-%m-%d').date()
        except ValueError:
            self.fail('invalid', format='YYYY-MM', input=data)


class YearField(serializers.Field):

    def to_representation(self, value):
        if value:
            return value.strftime('%Y')
        return None

    def to_internal_value(self, data):
        if isinstance(data, int):
            data = str(data)
        if not isinstance(data, str):
            self.fail('invalid', input=data)
        try:
            return datetime.strptime(data + '-01-01', '%Y-%m-%d').date()
        except ValueError:
            self.fail('invalid', input=data)


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
        fields = ('registration_number', 'role', 'college', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError(f"password and confirm password don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'college', 'password', 'registration_number', 'id', 'branch')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate(self, attrs):
        instance = self.instance
        new_role = attrs.get('role')
        if new_role:
            if new_role == 'hod':
                branch = attrs.get('branch', instance.branch if instance else None)
                if not branch:
                    raise serializers.ValidationError({'branch': 'Branch is required when the role is HOD.'})
        if 'password' in attrs:
            if attrs['password']:
                password2 = self.context['request'].data.get('password2')
                if attrs['password'] != password2:
                    raise serializers.ValidationError('Passwords do not match')
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(max_length=20,
                                                validators=[MinLengthValidator(6), MaxLengthValidator(11)])

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
    profile_picture = serializers.ImageField(allow_null=True, required=False)

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
    registration_year = YearField()
    college_name = serializers.CharField(source='user.college.college_name', read_only=True)

    class Meta:
        model = AcademicInformation
        exclude = ['id']
        read_only_fields = ['registration_number', 'user', 'college_name']


class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        exclude = ['id']
        read_only_fields = ['user']


class Tc_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TransferCertificateInformation
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
    tc_information = Tc_Serializer()
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        exclude = ['id']
        read_only_fields = ['user']

    def update(self, instance, validated_data):
        personal_info_data = validated_data.pop('personal_information', {})
        contact_info_data = validated_data.pop('contact_information', {})
        academic_info_data = validated_data.pop('academic_information', {})
        tc_info_data = validated_data.pop('tc_information', {})
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

        tc_info = instance.tc_information
        for attr, value in tc_info_data.items():
            setattr(tc_info, attr, value)
        tc_info.save()

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


class BonafideSerializer(serializers.ModelSerializer):
    supporting_document = Base64ImageField(required=False)

    college_details = serializers.SerializerMethodField(source='college', read_only=True)
    student_details = UserProfileSerializer(source='student', read_only=True)
    roll_no_details = serializers.CharField(source='roll_no.registration_number', read_only=True)

    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all(), write_only=True, required=False,
                                                 allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), write_only=True,
                                                 required=False, allow_null=True)
    roll_no = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Bonafide
        fields = '__all__'
        read_only_fields = ['student_details', 'college_details', 'bonafide_number', 'applied_date']

    def get_college_details(self, obj):
        if obj.college:
            return CollegeSerializer(obj.college).data

    def create(self, validated_data):
        request = self.context.get('request')
        supporting_document = validated_data.pop('supporting_document', None)
        user_profile = UserProfile.objects.get(user=request.user)
        college = user_profile.personal_information.user.college
        student = user_profile
        roll_no = user_profile.user
        validated_data['college'] = college
        validated_data['student'] = student
        validated_data['roll_no'] = roll_no
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


class Bonafide_Approve_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Bonafide
        fields = ['status', 'issue_date']
        read_only_fields = 'issue_date'

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.issue_date = validated_data.pop('issue_date', instance.date.today())
        instance.save()
        return instance


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class SemesterSerializer(serializers.ModelSerializer):
    subject_codes = serializers.ListField(child=serializers.CharField(), write_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'semester_name', 'subjects', 'subject_codes', 'branch', 'college', 'branch_name']

    def validate(self, data):
        user = self.context['request'].user
        college = data.get('college')
        subject_codes = data.get('subject_codes', [])
        if user.role == 'hod':
            if user.branch != data.get('branch'):
                raise serializers.ValidationError("You can only add semesters and subjects to your own branch.")
        if subject_codes:
            subjects = Subject.objects.filter(subject_code__in=subject_codes)
            missing_subject_codes = set(subject_codes) - set(subjects.values_list('subject_code', flat=True))
            if missing_subject_codes:
                raise serializers.ValidationError(f"Subject codes not found: {', '.join(missing_subject_codes)}")
            invalid_subjects = Subject.objects.filter(subject_code__in=subject_codes).exclude(college_id=college.id)
            if invalid_subjects.exists():
                raise serializers.ValidationError("Subjects must belong to the same college as the semester.")
        return data

    def create(self, validated_data):
        subject_codes = validated_data.pop('subject_codes')
        subjects = Subject.objects.filter(subject_code__in=subject_codes)
        semester = Semester.objects.create(**validated_data)
        semester.subjects.add(*subjects)
        return semester

    def update(self, instance, validated_data):
        subject_codes = validated_data.pop('subject_codes', None)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.semester_name = validated_data.get('semester_name', instance.semester_name)
        instance.branch_name = validated_data.get('branch_name', instance.branch_name)
        instance.save()
        if subject_codes is not None:
            subjects = Subject.objects.filter(subject_code__in=subject_codes)
            instance.subjects.set(subjects)
        return instance


class SemesterRegistrationSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer(read_only=True)
    student_details = UserProfileSerializer(source='student', read_only=True)

    class Meta:
        model = Semester_Registration
        fields = ['id', 'semester', 'student_details', 'applied_date', 'status', 'college']
        read_only_fields = ['id', 'student_details', 'semester']

    def validate(self, attrs):
        user = self.context['request'].user.profile
        semester_id = self.context['request'].data.get('semester')
        college = attrs.get('college')
        try:
            semester = Semester.objects.get(id=semester_id, college=college)
        except Semester.DoesNotExist:
            raise serializers.ValidationError("Invalid semester or semester does not belong to the specified college.")
        if Semester_Registration.objects.filter(student=user, semester=semester).exists():
            raise serializers.ValidationError("Student is already registered for this semester.")

        attrs['semester'] = semester
        attrs['student'] = user
        return attrs

    def create(self, validated_data):
        registration = Semester_Registration.objects.create(**validated_data)
        return registration


class HostelAllotmentRequestSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(write_only=True)
    latest_marksheet = Base64ImageField(required=False)

    class Meta:
        model = Hostel_Allotment
        fields = ['id', 'registration_number', 'latest_marksheet', 'status', 'college', 'prefered_room_type', 'cgpa']
        read_only_fields = ['user']

    def validate(self, attrs):
        registration_number = attrs.get('registration_number')
        college = attrs.get('college')
        if Hostel_Allotment.objects.filter(
                user__registration_number=registration_number, user__college=college).exists():
            raise serializers.ValidationError(
                "Only 1 Request is allowed your request already Exists, Wait for approval")
        return attrs

    def create(self, validated_data):
        registration_number = validated_data.pop('registration_number')
        college = validated_data.pop('college')
        cgpa = validated_data.pop('cgpa')
        prefered_room_type = validated_data.pop('prefered_room_type')
        latest_marksheet = validated_data.pop('latest_marksheet', None)
        try:
            user = User.objects.get(registration_number=registration_number, college=college)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        hostel_allotment = Hostel_Allotment.objects.create(
            user=user,
            college=college,
            cgpa=cgpa,
            prefered_room_type=prefered_room_type
        )
        if latest_marksheet:
            hostel_allotment.latest_marksheet = latest_marksheet.read()
            hostel_allotment.save()

        return hostel_allotment

    def update(self, instance, validated_data):
        registration_number = validated_data.pop('registration_number', None)
        latest_marksheet = validated_data.pop('latest_marksheet', None)
        college = validated_data.pop('college', None)
        prefered_room_type = validated_data.pop('prefered_room_type', None)
        cgpa = validated_data.pop('cgpa', None)
        if registration_number:
            try:
                user = User.objects.get(registration_number=registration_number, college=college)
                instance.user = user
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
        if prefered_room_type:
            instance.prefered_room_type = prefered_room_type
        if cgpa:
            instance.cgpa = cgpa

        if latest_marksheet:
            instance.latest_marksheet = latest_marksheet.read()
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['registration_number'] = instance.user.registration_number
        return representation


class HostelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelRooms
        fields = ['id', 'room_no', 'current_occupancy', 'capacity', 'room_type', 'status', 'college']

    def validate(self, attrs):
        sharing = {'single': 1, 'double': 2, 'triple': 3}
        room_no = attrs.get('room_no')
        college = attrs.get('college')
        sharing_type = attrs.get('room_type')
        capacity = attrs.get('capacity')
        if HostelRooms.objects.filter(room_no=room_no, college=college).exists():
            raise serializers.ValidationError(f"Room already exists with {room_no}")
        expected_capacity = sharing.get(sharing_type)
        if expected_capacity is not None and capacity != expected_capacity:
            raise serializers.ValidationError(
                f"Capacity for {sharing_type} room type should be {expected_capacity} but got {capacity}")
        return attrs

    def update(self, instance, validated_data):
        instance.college = validated_data.get('college', instance.college)
        instance.room_no = validated_data.get('room_no', instance.room_no)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.room_type = validated_data.get('room_type', instance.room_type)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class MultiplePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if isinstance(data, int):
            data = [data]
        if not isinstance(data, list):
            raise serializers.ValidationError("Incorrect type. Expected a list of pk values.")
        return super().to_internal_value(data)

    def to_representation(self, value):
        return [obj.pk for obj in value]


class HostelRoomAllotmentSerializer(serializers.ModelSerializer):
    allotment_details = serializers.PrimaryKeyRelatedField(
        queryset=Hostel_Allotment.objects.all(), many=True,
    )
    hostel_room = serializers.PrimaryKeyRelatedField(
        queryset=HostelRooms.objects.all(),
    )

    class Meta:
        model = Hostel_Room_Allotment
        fields = ['id', 'allotment_details', 'hostel_room','college']

    def validate(self, data):
        allotment_details = data['allotment_details']
        hostel_room = data['hostel_room']

        if not HostelRooms.objects.filter(id=hostel_room.id).exists():
            raise serializers.ValidationError({'hostel_room': 'Hostel room does not exist'})

        for allotment in allotment_details:
            if not Hostel_Room_Allotment.objects.filter(id=allotment.id).exists():
                raise serializers.ValidationError({'allotment_details': 'Invalid allotment details'})
            if Hostel_Room_Allotment.objects.filter(allotment_details=allotment.id).exists():
                raise serializers.ValidationError({'allotment_details': 'Allotment is already existing '})

        if hostel_room.current_occupancy + len(allotment_details) > hostel_room.capacity:
            raise serializers.ValidationError({'hostel_room': 'Hostel room does not have enough capacity'})

        return data

    def create(self, validated_data):
        allotment_details_ids = validated_data.pop('allotment_details')
        hostel_room = validated_data.pop('hostel_room')
        hostel_room_allotment = Hostel_Room_Allotment.objects.create(hostel_room=hostel_room, **validated_data)
        for allotment in allotment_details_ids:
            hostel_room_allotment.allotment_details.add(allotment)
            allotment.status = 'approved'
            allotment.save()
        hostel_room.current_occupancy += len(allotment_details_ids)
        if hostel_room.current_occupancy >= hostel_room.capacity:
            hostel_room.status = 'occupied'
        else:
            hostel_room.status = 'available'
        hostel_room.save()

        return hostel_room_allotment

    def update(self, instance, validated_data):
        allotment_details = validated_data.pop('allotment_details', None)
        hostel_room = validated_data.pop('hostel_room', None)

        instance.hostel_room = hostel_room
        instance.save()
        if allotment_details:
            instance.allotment_details.clear()
            for allotment in allotment_details:
                instance.allotment_details.add(allotment)
                allotment.status = 'approved'
                allotment.save()
        hostel_room.current_occupancy = instance.allotment_details.count()
        if hostel_room.current_occupancy >= hostel_room.capacity:
            hostel_room.status = 'occupied'
        else:
            hostel_room.status = 'available'
        hostel_room.save()
        return instance
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['allotment_details'] = HostelAllotmentRequestSerializer(instance.allotment_details.all(), many=True).data
        data['hostel_room'] = HostelRoomSerializer(instance.hostel_room).data
        return data


class HostelNoDuesSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source="user.registration_number", read_only=True)

    class Meta:
        model = Hostel_No_Due_request
        fields = '__all__'
        read_only_fields = ['registration_number', 'requested_date', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class GuestRoomAllotmentSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source="user.registration_number", read_only=True)

    class Meta:
        model = Guest_room_request
        fields = '__all__'
        read_only_fields = ['registration_number', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class ComplaintSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source="user.registration_number", read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['registration_number', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class MessFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fees_model
        fields = '__all__'


class MessFeePaymentSerializer(serializers.ModelSerializer):
    registration_details = serializers.PrimaryKeyRelatedField(queryset=Hostel_Room_Allotment.objects.all())
    from_date = YearMonthField()
    to_date = YearMonthField()

    class Meta:
        model = Mess_fee_payment
        fields = ['id', 'registration_details', 'from_date', 'to_date', 'fee_type', 'total_fees']

    def create(self, validated_data):
        registration_details_data = validated_data.pop('registration_details')

        mess_fee_payment = Mess_fee_payment.objects.create(
            registration_details=registration_details_data,
            **validated_data
        )
        return mess_fee_payment

    def validate_registration_details(self, value):
        if not Hostel_Room_Allotment.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("The provided registration details do not exist.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        registration_details = HostelRoomAllotmentSerializer(instance.registration_details).data
        representation['registration_details'] = registration_details

        return representation


class HostelAllotmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel_Allotment
        fields = ['id', 'status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class Departments_for_no_dueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments_for_no_Dues
        fields = ['id', 'Department_name', 'status', 'approved_date', 'applied_date', 'department_id']


class Cloned_Departments_for_no_dueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloned_Departments_for_no_Dues
        fields = '__all__'
        read_only_fields = ['no_dues_list', 'Department_name', 'Department_id', 'applied_date']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.no_dues_list.save()
        return instance


class Overall_No_Dues_RequestSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)

    class Meta:
        model = Overall_No_Dues_Request
        fields = '__all__'
        read_only_fields = ['registration_number', 'user']

    def validate(self, data):
        user = self.context['request'].user
        if Overall_No_Dues_Request.objects.filter(user=user).exists():
            raise ValidationError('A request for no dues already exists for this user.')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class No_Due_ListSerializer(serializers.ModelSerializer):
    cloned_departments = Cloned_Departments_for_no_dueSerializer(many=True, required=False, read_only=True)
    requested_data = serializers.SerializerMethodField()

    class Meta:
        model = No_Dues_list
        fields = '__all__'

    def get_requested_data(self, instance):
        request_id = instance.request_id
        return {
            'id': request_id.id,
            'registration_number': request_id.user.registration_number,
            'name': request_id.name,
            'branch': request_id.branch,
            "father_name": request_id.father_name,
            "category": request_id.category,
            "self_declaration": request_id.self_declaration,
            "status": request_id.status,
            "session": request_id.session,
        }

    def create(self, validated_data):
        cloned_departments_data = validated_data.pop('cloned_departments', None)
        instance = super().create(validated_data)

        if cloned_departments_data:
            for department_data in cloned_departments_data:
                Cloned_Departments_for_no_Dues.objects.create(no_dues_list=instance, **department_data)
        return instance

    def update(self, instance, validated_data):
        cloned_departments_data = validated_data.pop('cloned_departments', None)
        instance = super().update(instance, validated_data)

        if cloned_departments_data:
            instance.cloned_departments.all().delete()
            for department_data in cloned_departments_data:
                Cloned_Departments_for_no_Dues.objects.create(no_dues_list=instance, **department_data)
        return instance


class Overall_No_Due_Serializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)

    class Meta:
        model = Overall_No_Dues_Request
        fields = '__all__'
        read_only_fields = ['registration_number', 'user']

    def validate(self, data):
        user = self.context['request'].user

        if Overall_No_Dues_Request.objects.filter(user=user).exists():
            raise ValidationError('A request for no dues already exists for this user.')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        overall_no_dues_instance = super().create(validated_data)
        No_Dues_list.objects.create(request_id=overall_no_dues_instance)

        return overall_no_dues_instance


class SemesterVerificationSerializer(serializers.ModelSerializer):
    registration_details = serializers.PrimaryKeyRelatedField(
        queryset=Semester_Registration.objects.all(),
        write_only=True
    )
    registration_details_info = SemesterRegistrationSerializer(read_only=True, source='registration_details')

    class Meta:
        model = VerifySemesterRegistration
        fields = ['id', 'registration_details', 'registration_details_info', 'remarks', 'status', 'college']

    def create(self, validated_data):
        instance = VerifySemesterRegistration.objects.create(**validated_data)
        instance.registration_details.status = instance.status
        instance.registration_details.save()
        return instance

    def update(self, instance, validated_data):
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        instance.registration_details.status = instance.status
        instance.registration_details.save()
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)
    time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'time', 'registration_number']
        read_only_fields = ['registration_number', 'time']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        local_time = timezone.localtime(instance.time, timezone=timezone.get_fixed_timezone(330))
        data['time'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
        return data


class CollegeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeRequest
        fields = '__all__'
        read_only_fields = ['is_verified']

    def validate(self, data):
        college_name = data.get('college_name')
        if CollegeRequest.objects.filter(college_name=college_name).exists():
            raise ValidationError('A request already exists for this college')
        return data


class CollegeRequestVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeRequest
        fields = ['is_verified']

    def validate(self, data):
        instance = self.instance
        if instance and instance.is_verified and data.get('is_verified') is True:
            raise serializers.ValidationError("The 'is_verified' field cannot be changed once it is set to True.")
        return data


class CollegeSlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['slug', 'id']


class CollgeIdCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = College_with_Ids
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

    def validate(self, data):
        branch_name = data.get('branch_name')
        college = data.get('college')
        if Branch.objects.filter(branch_name=branch_name, college=college).exists():
            raise serializers.ValidationError("A branch with this name already exists in the selected college.")
        return data

    def create(self, validated_data):
        branch = Branch.objects.create(**validated_data)
        branch.save()
        return branch
