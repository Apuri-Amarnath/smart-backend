import base64
from datetime import datetime
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
    Cloned_Departments_for_no_Dues, CollegeRequest, College_with_Ids

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

    # validate password
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
        fields = [ 'status', 'issue_date']
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


class SemesterRegistrationSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer(read_only=True)
    student_details = UserProfileSerializer(source='student', read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), write_only=True)

    class Meta:
        model = Semester_Registration
        fields = ['id', 'semester', 'student', 'student_details', 'applied_date', 'status']
        read_only_fields = ['id', 'student_details', 'semester']

    def create(self, validated_data):
        student = validated_data.pop('student')
        semester = Semester.objects.get(id=self.context['request'].data['semester'])
        registration = Semester_Registration.objects.create(student=student, semester=semester)
        return registration


class HostelAllotmentSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(write_only=True)
    latest_marksheet = Base64ImageField(required=False)

    class Meta:
        model = Hostel_Allotment
        fields = ['id', 'registration_number', 'latest_marksheet', 'status']
        read_only_fields = ['user']

    def validate(self, attrs):
        registration_number = attrs.get('registration_number')
        if Hostel_Allotment.objects.filter(
                user__registration_number=registration_number).exists():
            raise serializers.ValidationError(
                "Only 1 Request is allowed your request already Exists, Wait for approval")
        return attrs

    def create(self, validated_data):
        registration_number = validated_data.pop('registration_number')
        latest_marksheet = validated_data.pop('latest_marksheet', None)
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        status = validated_data.pop('status')

        hostel_allotment = Hostel_Allotment.objects.create(
            user=user,
            status=status
        )
        if latest_marksheet:
            hostel_allotment.latest_marksheet = latest_marksheet.read()
            hostel_allotment.save()

        return hostel_allotment

    def update(self, instance, validated_data):
        registration_number = validated_data.pop('registration_number', None)
        latest_marksheet = validated_data.pop('latest_marksheet', None)

        if registration_number:
            try:
                user = User.objects.get(registration_number=registration_number)
                instance.user = user
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if latest_marksheet:
            instance.latest_marksheet = latest_marksheet.read()
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['registration_number'] = instance.user.registration_number
        return representation


class HostelRoomAllotmentSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(write_only=True)
    registration_details = serializers.SerializerMethodField()

    class Meta:
        model = Hostel_Room_Allotment
        fields = ['registration_number', 'hostel_room', 'id', 'registration_details']
        read_only_fields = ['id']

    def get_registration_details(self, obj):
        return {
            'id': obj.registration_details.id,
            'registration_number': obj.registration_details.user.registration_number
        }

    def create(self, validated_data):
        registration_number = validated_data.pop('registration_number')
        hostel_room = validated_data.pop('hostel_room')

        try:
            hostel_allotment = Hostel_Allotment.objects.get(user__registration_number=registration_number)
        except Hostel_Allotment.DoesNotExist:
            raise serializers.ValidationError("Hostel allotment not found for the given registration number")
        if Hostel_Room_Allotment.objects.filter(registration_details=hostel_allotment).exists():
            raise serializers.ValidationError("A room has already been allotted to this registration number.")
        if Hostel_Room_Allotment.objects.filter(hostel_room=hostel_room).exists():
            raise serializers.ValidationError("A hostel room with the given number is already allotted.")

        hostel_room_allotment = Hostel_Room_Allotment.objects.create(
            registration_details=hostel_allotment,
            hostel_room=hostel_room
        )

        return hostel_room_allotment

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        registration_details = self.get_registration_details(instance)
        representation['registration_details'] = registration_details
        return representation


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
        fields = ['id', 'registration_details', 'registration_details_info', 'remarks', 'status']

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