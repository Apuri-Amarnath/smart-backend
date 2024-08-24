import os.path
import secrets
import smtplib
import string
from email.mime.text import MIMEText
from venv import logger

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets, parsers
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.models import User

from .emails import send_login_credentials, send_department_login_credentials
from .models import User, UserProfile, College, Bonafide, PersonalInformation, AcademicInformation, ContactInformation, \
    Subject, Semester, Semester_Registration, Hostel_Allotment, Guest_room_request, Hostel_No_Due_request, \
    Hostel_Room_Allotment, Fees_model, Mess_fee_payment, Complaint, Overall_No_Dues_Request, No_Dues_list, \
    VerifySemesterRegistration, Notification, Departments_for_no_Dues, CollegeRequest, College_with_Ids, Branch, \
    HostelRooms
from .renderers import UserRenderer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, CollegeSerializer, \
    BonafideSerializer, PersonalInfoSerializer, AcademicInfoSerializer, ContactInformationSerializer, \
    ChangeUserPasswordSerializer, Csv_RegistrationSerializer, SubjectSerializer, SemesterSerializer, \
    SemesterRegistrationSerializer, GuestRoomAllotmentSerializer, HostelNoDuesSerializer, \
    HostelRoomAllotmentSerializer, MessFeeSerializer, MessFeePaymentSerializer, \
    ComplaintSerializer, Overall_No_Due_Serializer, No_Due_ListSerializer, SemesterVerificationSerializer, \
    NotificationSerializer, Departments_for_no_dueSerializer, Cloned_Departments_for_no_dueSerializer, \
    CollegeRequestSerializer, CollegeSlugSerializer, CollegeRequestVerificationSerializer, Bonafide_Approve_Serializer, \
    CollgeIdCountSerializer, BranchSerializer, UserManagementSerializer, HostelRoomSerializer, \
    HostelAllotmentRequestSerializer, Approve_HostelNoDueSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
import subprocess
import git
import csv
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, filters
from .permissions import IsCaretakerOrAdmin, IsStudentOrAdmin, IsFacultyOrAdmin, IsDepartmentOrAdmin, IsOfficeOrAdmin, \
    IsOfficeOnlyOrAdmin, \
    IsAdmin, IsRegistrarOrAdmin, IsHODorAdmin
from django.db.models import Case, When, IntegerField, OuterRef
import logging

# Set up logging
looger = logging.getLogger(__name__)


@csrf_exempt
def update(request):
    if request.method == "POST":
        try:
            repo = git.Repo("/home/Amarnath013/smart-backend")
            origin = repo.remotes.origin
            origin.pull()
            logger.info("Successfully updated the code on PythonAnywhere.")
            return HttpResponse("Updated code on PythonAnywhere")
        except Exception as e:
            logger.error(f"Error updating code: {str(e)}")
            try:
                repo.git.stash()
                origin.pull()
                logger.info("Successfully updated the code on PythonAnywhere after stashing changes.")
                subprocess.run(["/bin/bash", "/home/Amarnath013/smart-backend/config.sh"], check=True)
                return HttpResponse("Updated code on PythonAnywhere after stashing changes")
            except Exception as e2:
                logger.error(f"Error updating code after stashing changes: {str(e2)}")
                return HttpResponse("An error occurred while updating the code, even after stashing changes.")
    else:
        return HttpResponse("This endpoint only supports POST requests.")


# manually generate token
def get_tokens_for_user(user):
    college_name = None
    if user.college:
        college = College.objects.get(slug=user.college.slug)
        college_name = college.slug
    branch = None
    if user.role == 'hod':
        branch = user.branch
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['registration_number'] = user.registration_number
    refresh['college'] = college_name
    refresh['branch'] = branch

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class TokenRefresh(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data['access']
        return Response({'access': str(access_token)}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsOfficeOrAdmin]

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')

        if 'file' in request.data:
            file_serializer = Csv_RegistrationSerializer(data=request.data)
            if file_serializer.is_valid(raise_exception=True):
                csv_file = file_serializer.validated_data['file']
                file_path = self.save_uploaded_file(csv_file)
                response = self.handle_csv_user_creation(file_path, slug)
                return response
        if not slug:
            return Response({'error': 'Not a valid slug'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                with transaction.atomic():
                    college = College.objects.get(slug=slug)
                    college_with_ids = College_with_Ids.objects.get(college_name=college.slug)
                    user_data = request.data.copy()
                    user_data['college'] = college.id
                    registration_number = user_data.get('registration_number')
                    if User.objects.filter(registration_number=registration_number, college=college.id).exists():
                        return Response({'message': 'User already exists with this registration number and college'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    serializer = UserRegistrationSerializer(data=user_data)
                    if serializer.is_valid(raise_exception=True):
                        user = serializer.save()
                        token = get_tokens_for_user(user)
                        college_with_ids.id_count += 1
                        college_with_ids.save()
                        return Response({'token': token, 'message': 'User creation successful'},
                                        status=status.HTTP_201_CREATED)
            except College.DoesNotExist:
                return Response({'error': 'College not found'}, status.HTTP_404_NOT_FOUND)
            except CollegeRequest.DoesNotExist:
                return Response({'error': 'College request not found'}, status.HTTP_404_NOT_FOUND)

    def save_uploaded_file(self, csv_file):
        upload_dir = settings.CSV_UPLOADS_DIR
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, csv_file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
        return file_path

    def handle_csv_user_creation(self, csv_file_path, slug):
        if not os.path.exists(csv_file_path):
            return Response({'message': 'csv file not found'}, status=status.HTTP_400_BAD_REQUEST)
        user_created = []
        user_existing = []
        errors = []
        try:
            college = College.objects.get(slug=slug)
            college_with_ids = College_with_Ids.objects.get(college_name=college.slug)
        except College.DoesNotExist:
            return Response({'error': 'College not found'}, status=status.HTTP_404_NOT_FOUND)
        except College_with_Ids.DoesNotExist:
            return Response({'error': 'College request not found'}, status=status.HTTP_404_NOT_FOUND)

        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                row['college'] = int(college.id)
                registration_number = row.get('registration_number')
                if User.objects.filter(registration_number=registration_number, college=college).exists():
                    user_existing.append(registration_number)
                else:
                    serializer = UserRegistrationSerializer(data=row)
                    if serializer.is_valid(raise_exception=True):
                        try:
                            user = serializer.save()
                            user_created.append(user.registration_number)
                            college_with_ids.id_count += 1
                            college_with_ids.save()
                        except IntegrityError:
                            errors.append({'registration_number': registration_number,
                                           'error': 'User already exists with this registration number and college'})
                    else:
                        errors.append({'registration_number': registration_number, 'error': serializer.errors})

        response_data = {'message': 'user creation process completed', 'users_created': user_created,
                         'user_existing': user_existing, 'errors': errors}
        return Response(response_data,
                        status=status.HTTP_200_OK if not errors else status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            registration_number = serializer.data.get('registration_number')
            password = serializer.data.get('password')
            user = authenticate(registration_number=registration_number, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                college_data = None
                if user.college:
                    college_serailzer = CollegeSerializer(user.college)
                    college_data = college_serailzer.data.get('college_name')
                return Response(
                    {'token': token, 'message': 'Login successful', 'role': user.role, 'college': college_data},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': {'non_fields_errors': ['registration number or password is Not valid']}},
                    status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ChangeUserPasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': 'password change successfully'}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    renderer_classes = [UserRenderer]
    serializer_class = UserProfileSerializer
    permission_classes = [IsStudentOrAdmin]

    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            raise ValidationError({'detail': 'User profile not found.', 'code': 'user_not_found'},
                                  status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError({'error': 'Empty JSON payload is not allowed.'},
                                  status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {'status': 'success', 'message': 'User profile updated successfully.',
                 'user_profile': serializer.data},
                status=status.HTTP_200_OK)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [IsOfficeOrAdmin | IsStudentOrAdmin]

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        try:
            college = College.objects.get(slug=slug)
        except College.DoesNotExist:
            raise NotFound(detail='College not found')
        serializer = self.get_serializer(college)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if self.request.user.role != 'super-admin':
            raise PermissionDenied({'error': 'Only site-admin or staff users can add colleges'})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user.role != 'super-admin':
            raise PermissionDenied({'error': 'Only site-admin or staff users can update college data.'})
        return super().create(request, *args, **kwargs)


class BonafideViewSet(viewsets.ModelViewSet):
    queryset = Bonafide.objects.all()
    serializer_class = BonafideSerializer
    permission_classes = [IsStudentOrAdmin | IsRegistrarOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['roll_no__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        # print(slug)
        if slug:
            queryset = queryset.filter(college__slug__iexact=slug)
            # print(queryset)
        status_order = Case(
            When(status='applied', then=1),
            When(status='approved', then=2),
            When(status='rejected', then=3),
            When(status='pending', then=4),
            When(status='not-applied', then=5),
            output_field=IntegerField(),
        )
        return queryset.annotate(
            status_order=status_order
        ).order_by('status_order')

    def get_object(self):

        pk = self.kwargs.get('pk')
        if not pk:
            raise ValidationError({'error': 'Primary key is required.'})
        try:
            return self.queryset.get(pk=pk)
        except Bonafide.DoesNotExist:
            raise NotFound({'error': 'Details are not found.'})

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        if not self.request.data:
            raise ValidationError({'error': 'Empty JSON payload is not allowed.'},
                                  status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {'status': 'success', 'message': 'Details uploaded successfully.',
                 'Bonafide_data': serializer.data},
                status=status.HTTP_200_OK)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, serializer_class=Bonafide_Approve_Serializer,
            permission_classes=[IsRegistrarOrAdmin])
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Bonafide has been verified'}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsHODorAdmin]
    renderer_classes = [UserRenderer]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ['subject_name', 'subject_code', 'instructor']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id

        if self.request.user.role not in ['hod', 'super-admin']:
            raise PermissionDenied({'error': 'Only HOD or Admin users can add subject data.'})

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id

        if self.request.user.role not in ['hod', 'super-admin']:
            raise PermissionDenied({'error': 'Only HOD or Admin users can update subject data.'})

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class SemesterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsHODorAdmin]
    renderer_classes = [UserRenderer]
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['semester_name', 'branch', 'branch_name']
    ordering_fields = '__all__'
    ordering = ['semester_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if request.user.role not in ['hod', 'super-admin']:
            raise PermissionDenied({'errors': 'Only HOD or Admin users can create semester data.'})
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if request.user.role not in ['hod', 'super-admin']:
            raise PermissionDenied({'errors': 'Only HOD or Admin users can create semester data.'})
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        serializer.save()


class SemesterRegistrationViewset(viewsets.ModelViewSet):
    permission_classes = [IsStudentOrAdmin | IsHODorAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['student__user__registration_number']
    renderer_classes = [UserRenderer]
    queryset = Semester_Registration.objects.all()
    serializer_class = SemesterRegistrationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        if self.request.user.role == 'hod':
            branch = self.request.user.branch
            queryset = queryset.filter(semester__branch=branch)
        if self.request.user.role == 'student':
            queryset = queryset.filter(student__user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if request.user.role not in ['student']:
            raise PermissionDenied({'errors': 'Only students can register for semesters.'})
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()


class SemesterVerificationViewSet(viewsets.ModelViewSet):
    queryset = VerifySemesterRegistration.objects.all()
    serializer_class = SemesterVerificationSerializer
    permission_classes = [IsHODorAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [SearchFilter]
    search_fields = ['status', 'registration_details__student__user__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        if self.request.user.role == 'hod':
            branch = self.request.user.branch
            queryset = queryset.filter(registration_details__semester__branch=branch)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'semester verificaton successfull'}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()


class HostelAllotmentViewset(viewsets.ModelViewSet):
    permission_classes = [IsStudentOrAdmin | IsCaretakerOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__registration_number', 'status']
    queryset = Hostel_Allotment.objects.all()
    serializer_class = HostelAllotmentRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'data': serializer.data, 'message': 'Hostel allotment request is successfull'},
                            status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class HostelRoomAllotmentViewset(viewsets.ModelViewSet):
    permission_classes = [IsCaretakerOrAdmin | IsStudentOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter]
    search_fields = ['allotment_details__user__registration_number']
    queryset = Hostel_Room_Allotment.objects.all()
    serializer_class = HostelRoomAllotmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(allotment_details__user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if request.user.role not in ['admin', 'caretaker']:
            raise PermissionDenied({'errors': 'only admin and caretaker can allotment rooms'})
        if isinstance(data.get('allotment_details'), int):
            data['allotment_details'] = [data['allotment_details']]
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class HostelMessFeeViewSet(viewsets.ModelViewSet):
    queryset = Fees_model.objects.all()
    serializer_class = MessFeeSerializer
    permission_classes = [IsCaretakerOrAdmin | IsStudentOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if request.user.role not in ['admin', 'caretaker']:
            raise PermissionDenied({'errors': 'only caretaker can add the fee details'})
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'data added succesfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return Response({'error': 'invalid pk'}, status=status.HTTP_400_BAD_REQUEST)
        fee = get_object_or_404(Fees_model, pk=pk)
        if request.user.role not in ['admin', 'caretaker']:
            return Response({'errors': 'only caretaker can add the fee details'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(fee, data=request.data, partial=kwargs.get('partial'))
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response({'message': 'Data updated succesfully'}, status=status.HTTP_202_ACCEPTED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MessFeePaymentCreateViewset(viewsets.ModelViewSet):
    renderer_classes = [UserRenderer]
    serializer_class = MessFeePaymentSerializer
    queryset = Mess_fee_payment.objects.all()
    permission_classes = [IsCaretakerOrAdmin | IsStudentOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['registration_details__allotment_details__user__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(registration_details__allotment_details__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GuestRoomAllotmentViewSet(viewsets.ModelViewSet):
    serializer_class = GuestRoomAllotmentSerializer
    queryset = Guest_room_request.objects.all()
    permission_classes = [IsStudentOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [SearchFilter]
    search_fields = ['user__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(
                {'data': serializer.data, 'message': 'guest room allotment request was successfully created '},
                status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ComplaintViewSet(viewsets.ModelViewSet):
    renderer_classes = [UserRenderer]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()
    permission_classes = [IsStudentOrAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['user__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'data': serializer.data, 'message': 'Complaint successfully created'},
                            status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Overall_no_duesViewSet(viewsets.ModelViewSet):
    serializer_class = Overall_No_Due_Serializer
    queryset = Overall_No_Dues_Request.objects.all()
    permission_classes = [IsStudentOrAdmin | IsDepartmentOrAdmin]
    renderer_classes = [UserRenderer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        user = self.request.user
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'Request was applied successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Hostel_No_dueViewset(viewsets.ModelViewSet):
    serializer_class = HostelNoDuesSerializer
    queryset = Hostel_No_Due_request.objects.all()
    permission_classes = [IsStudentOrAdmin | IsCaretakerOrAdmin]
    renderer_classes = [UserRenderer]

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        if self.request.user.role != 'student':
            raise PermissionDenied({'error': 'only student can create a request'})
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'Request was applied successfully'}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        instance = self.get_object()
        if self.request.user.role not in ['caretaker', 'super-admin']:
            raise PermissionDenied({'error': 'You do not have permissions to edit this request'})
        serializer = Approve_HostelNoDueSerializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response({'message': 'Request was updated successfully'}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()


class NoDuesListViewSet(viewsets.ModelViewSet):
    queryset = No_Dues_list.objects.all()
    serializer_class = No_Due_ListSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    search_fields = ['request_id__user__registration_number']

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        user = self.request.user
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            if self.request.user.role == 'student':
                queryset = queryset.filter(request_id__user=user)
        return queryset

    @action(detail=True, methods=['patch'], url_path='departments/(?P<department_id>[^/.]+)',
            permission_classes=[IsDepartmentOrAdmin])
    def update_department(self, request, pk=None, department_id=None):
        try:
            no_dues_list_instance = self.get_object()
        except No_Dues_list.DoesNotExist:
            return Response({'error': 'No Due_list not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            department = no_dues_list_instance.cloned_departments.get(Department_id=department_id)
        except Departments_for_no_Dues.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        user_registration_number = request.user.registration_number
        if not user_registration_number.startswith("DEP"):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user_department_id = int(user_registration_number[3:5])
        except ValueError:
            return Response({'error': 'Invalid registration number format'}, status=status.HTTP_400_BAD_REQUEST)
        if user_department_id != int(department_id):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        department_data = request.data
        department_serializer = Cloned_Departments_for_no_dueSerializer(instance=department, data=department_data,
                                                                        partial=True)
        if department_serializer.is_valid():
            department_serializer.save()

            all_approved = all(
                dep.status == 'approved' for dep in no_dues_list_instance.cloned_departments.all()
            )
            if all_approved:
                no_dues_list_instance.status = 'approved'
                no_dues_list_instance.approved_date = timezone.now()
            else:
                no_dues_list_instance.status = 'pending'
                no_dues_list_instance.approved_date = None

            no_dues_list_instance.save()

            return Response(department_serializer.data)

        return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)


class NotificationsViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['user__registration_number']
    renderer_classes = [UserRenderer]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        request_user = request.user
        notification_user = instance.user
        if request_user != notification_user:
            raise PermissionDenied("You do not have permission to delete this notification.")
        self.perform_destroy(instance)
        return Response({"message": "Notifications has been cleared."}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=False, methods=['delete'])
    def delete_all_notification(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        notifications = Notification.objects.filter(id__in=ids, user=request.user)
        if not notifications.exists():
            return Response({'error': 'No Notifications found.'}, status=status.HTTP_400_BAD_REQUEST)
        count = notifications.count()
        notifications.delete()
        return Response({'message': 'Notifications deleted succesfully.'}, status=status.HTTP_200_OK)


class CollegeRequestViewSet(viewsets.ModelViewSet):
    queryset = CollegeRequest.objects.all()
    serializer_class = CollegeRequestSerializer

    renderer_classes = [UserRenderer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Request was successful', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        return super().list(request, args, kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        return super().retrieve(request, args, kwargs)


class CollegeSlugListView(generics.ListAPIView):
    queryset = College.objects.all()
    serializer_class = CollegeSlugSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']


class CollegeRequestVerificationView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    queryset = CollegeRequest.objects.all()
    serializer_class = CollegeRequestVerificationSerializer
    renderer_classes = [UserRenderer]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'message': 'Request was successfully verified'}, status.HTTP_200_OK)


class CollegeIDCountView(viewsets.ModelViewSet):
    queryset = College_with_Ids.objects.all()
    serializer_class = CollgeIdCountSerializer
    permission_classes = [IsOfficeOnlyOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter]
    search_fields = ['college_name']


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOfficeOrAdmin]
    renderer_classes = [UserRenderer]
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        college = get_object_or_404(College, slug=slug)
        data = request.data.copy()
        data['college'] = college.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            data.clear()
            return Response({'message': 'Branch was successfully created and HOD credentials are mailed'},
                            status=status.HTTP_201_CREATED)
        return Response({'error': 'serializer.errors'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()


class UserManagmentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [IsOfficeOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
            queryset = queryset.exclude(role="super-admin")
            queryset = queryset.exclude(id=self.request.user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        with transaction.atomic():
            college = get_object_or_404(College, slug=slug)
            college_with_id = College_with_Ids.objects.get(college_name=college.slug)
            user_data = request.data.copy()
            user_data['college'] = college.id
            registration_number = user_data.get('registration_number')
            if User.objects.filter(registration_number=registration_number, college=college.id).exists():
                return Response({'message': 'User already exists with this registration number in the college'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = UserRegistrationSerializer(data=user_data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                college_with_id.id_count += 1
                college_with_id.save()
                return Response({'message': 'User Creation successfull'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user_instance = self.get_object()
        data = request.data.copy()
        data.pop('college', None)

        serializer = self.get_serializer(user_instance, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'User Updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user_instance = self.get_object()
        data = request.data.copy()
        data.pop('college', None)

        serializer = self.get_serializer(user_instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'User Updated successfully', 'data':
            serializer.data}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        college = instance.college
        college_with_ids = College_with_Ids.objects.get(college_name=college.slug)
        with transaction.atomic():
            self.perform_destroy(instance)
            college_with_ids.id_count -= 1
            college_with_ids.save()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class HostelRoomRegistrationView(viewsets.ModelViewSet):
    queryset = HostelRooms.objects.all()
    serializer_class = HostelRoomSerializer
    permission_classes = [IsCaretakerOrAdmin]
    renderer_classes = [UserRenderer]

    def get_queryset(self):
        queryset = super().get_queryset()
        slug = self.kwargs.get('slug')
        if slug:
            college = get_object_or_404(College, slug=slug)
            queryset = queryset.filter(college_id=college.id)
        return queryset

    def create(self, request, *args, **kwargs):
        logger.debug("POST method started")
        slug = kwargs.get('slug')
        if 'file' in request.data:
            file_serializer = Csv_RegistrationSerializer(data=request.data)
            if file_serializer.is_valid(raise_exception=True):
                csv_file = file_serializer.validated_data['file']
                file_path = self.save_uploaded_file(csv_file)
                response = self.handle_csv_room_creation(file_path, slug)
                return response
        if not slug:
            return Response({'error': 'Not a valid slug'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                with transaction.atomic():
                    college = College.objects.get(slug=slug)
                    room_data = request.data.copy()
                    room_data['college'] = college.id
                    serializer = self.get_serializer(data=room_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({'message': 'Rooms created successfully'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)
            except College.DoesNotExist:
                return Response({'error': 'College not found'}, status=status.HTTP_400_BAD_REQUEST)

    def save_uploaded_file(self, csv_file):
        upload_dir = settings.CSV_UPLOADS_DIR
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, csv_file.name)
        with default_storage.open(file_path, 'wb') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
            return file_path

    def handle_csv_room_creation(self, csv_file_path, slug):
        if not os.path.exists(csv_file_path):
            return Response({'errors': 'csv file not found'}, status=status.HTTP_400_BAD_REQUEST)
        rooms_created = []
        rooms_existing = []
        errors = []
        try:
            college = College.objects.get(slug=slug)
        except College.DoesNotExist:
            return Response({'error': 'College not found'}, status=status.HTTP_400_BAD_REQUEST)

        with open(csv_file_path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                row['college'] = college.id
                serializer = HostelRoomSerializer(data=row)
                if serializer.is_valid(raise_exception=True):
                    try:
                        serializer.save()
                        rooms_created.append(serializer.data['room_no'])
                    except IntegrityError:
                        rooms_existing.append(serializer.data['room_no'])
                else:
                    errors.append({'room_no': row.get('room_no'), 'errors': serializer.errors['room_no']})
        response_data = {
            'message': 'Room creation proccss completed',
            'rooms_created': rooms_created,
            'rooms_existing': rooms_existing,
            'errors': errors,
        }
        return Response(response_data, status=status.HTTP_200_OK if not errors else status.HTTP_400_BAD_REQUEST)


class DepartmentIdCreationView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsOfficeOrAdmin]

    def generate_password(self, length=10):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        exclude = '/\\\'\"'
        filtered_password = ''.join(c for c in alphabet if c not in exclude)
        password = ''.join(secrets.choice(filtered_password) for i in range(length))
        return password

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if not slug:
            return Response({'error': 'Slug is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                college = College.objects.get(slug=slug)
                college_code = college.college_code
                default_password = self.generate_password()
                credentials = []
                for i in range(1, 19):
                    department_number = f"{i:02}"
                    registration_number = f"DEP{department_number}-{college_code}"
                    if User.objects.filter(registration_number=registration_number, college=college).exists():
                        continue
                    user_data = {
                        'registration_number': registration_number[:11],
                        'password': default_password,
                        'password2': default_password,
                        'role': 'department',
                        'college': college.id
                    }
                    serializer = UserRegistrationSerializer(data=user_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        credentials.append(registration_number, default_password, department_number)
                        to_email = college.college_email
                        send_department_login_credentials(to_email=to_email, credentials=credentials,
                                                          college_name=college.college_name)
                    else:
                        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Departments Created Successfully'}, status=status.HTTP_201_CREATED)

        except College.DoesNotExist:
            return Response({'error': 'College not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoDuesListUpdateView(APIView):
    permission_classes = [IsDepartmentOrAdmin]

    def patch(self, request, pk, department_id, slug):
        try:
            no_dues_list_instance = No_Dues_list.objects.get(id=pk)
        except No_Dues_list.DoesNotExist:
            return Response({'error': 'No Dues list not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            department = no_dues_list_instance.cloned_departments.get(Department_id=department_id)
        except No_Dues_list.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        user_registration_number = request.user.registration_number
        if not user_registration_number.startswith("DEP"):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Validate user department
        try:
            user_department_id = int(user_registration_number[3:5])  # Adjusted based on your requirement
        except ValueError:
            return Response({'error': 'Invalid registration number format'}, status=status.HTTP_400_BAD_REQUEST)

        if user_department_id != department_id:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Update the department
        department_data = request.data
        department_serializer = Cloned_Departments_for_no_dueSerializer(
            instance=department, data=department_data, partial=True
        )

        if department_serializer.is_valid():
            department_serializer.save()

            # Check if all departments are approved
            all_approved = all(dep.status == 'approved' for dep in no_dues_list_instance.cloned_departments.all())
            no_dues_list_instance.status = 'approved' if all_approved else 'pending'
            no_dues_list_instance.approved_date = timezone.now() if all_approved else None

            no_dues_list_instance.save()

            return Response(department_serializer.data, status=status.HTTP_200_OK)

        return Response(department_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
