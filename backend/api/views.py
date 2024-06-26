import os.path
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.models import User
from .models import User, UserProfile, College, Bonafide, PersonalInformation, AcademicInformation, ContactInformation, \
    Subject, Semester, Semester_Registration, Hostel_Allotment, Guest_room_request, Hostel_No_Due_request, \
    Hostel_Room_Allotment, Fees_model, Mess_fee_payment, Complaint, Overall_No_Dues_Request, No_Dues_list, \
    VerifySemesterRegistration
from .renderers import UserRenderer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, CollegeSerializer, \
    BonafideSerializer, PersonalInfoSerializer, AcademicInfoSerializer, ContactInformationSerializer, \
    ChangeUserPasswordSerializer, Csv_RegistrationSerializer, SubjectSerializer, SemesterSerializer, \
    SemesterRegistrationSerializer, HostelAllotmentSerializer, GuestRoomAllotmentSerializer, HostelNoDuesSerializer, \
    HostelRoomAllotmentSerializer, MessFeeSerializer, MessFeePaymentSerializer, HostelAllotmentStatusUpdateSerializer, \
    ComplaintSerializer, Overall_No_Due_Serializer, No_Due_ListSerializer, SemesterVerificationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
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
from .permissions import IsCaretakerOrAdmin, IsStudentOrAdmin, IsFacultyOrAdmin
from django.db.models import Case, When, IntegerField
import logging

# Set up logging
logger = logging.getLogger(__name__)


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
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['registration_number'] = user.registration_number

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class TokenRefresh(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        serializer = TokenRefreshView().get_serializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data['access']
        return Response({'access': str(access_token)}, status=status.HTTP_200_OK)


# Create your views here.
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if 'file' in request.data:
            file_serializer = Csv_RegistrationSerializer(data=request.data)
            if file_serializer.is_valid(raise_exception=True):
                csv_file = file_serializer.validated_data['file']
                file_path = self.save_uploaded_file(csv_file)
                response = self.handle_csv_user_creation(file_path)
                return response
        else:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                token = get_tokens_for_user(user)
                return Response({'token': token, 'message': 'User creation successful'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'user already exits', "error": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def save_uploaded_file(self, csv_file):
        upload_dir = settings.CSV_UPLOADS_DIR
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, csv_file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
        return file_path

    def handle_csv_user_creation(self, csv_file_path):
        if not os.path.exists(csv_file_path):
            return Response({'message': 'csv file not found'}, status=status.HTTP_400_BAD_REQUEST)
        user_created = []
        user_existing = []
        errors = []
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                registration_number = row.get('registration_number')
                if User.objects.filter(registration_number=registration_number).exists():
                    user_existing.append(registration_number)
                else:
                    serializer = UserRegistrationSerializer(data=row)
                    if serializer.is_valid():
                        user = serializer.save()
                        user_created.append(user.registration_number)
                    else:
                        errors.append(serializer.errors)

        return Response({'message': 'user creation process completed', 'users_created': user_created,
                         'user_existing': user_existing, 'error': errors},
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
                return Response({'token': token, 'message': 'Login successful', 'role': user.role},
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
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

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
    permission_classes = [IsAuthenticated, IsFacultyOrAdmin | IsStudentOrAdmin]

    def get_object(self):
        try:
            college_code = self.request.query_params.get('college_code')
            return self.queryset.get(college_code=college_code)
        except College.DoesNotExist:
            raise ValidationError({'error': 'College does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        if self.request.user.role not in ['admin', 'faculty']:
            raise PermissionDenied({'error': 'Only admin or staff users can add subjects data.'})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user.role not in ['admin', 'faculty']:
            raise PermissionDenied({'error': 'Only admin or staff users can add subjects data.'})
        return super().create(request, *args, **kwargs)


class BonafideViewSet(viewsets.ModelViewSet):
    queryset = Bonafide.objects.all()
    serializer_class = BonafideSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['roll_no__registration_number']

    def get_queryset(self):
        status_order = Case(
            When(status='applied', then=1),
            When(status='approved', then=2),
            When(status='rejected', then=3),
            When(status='pending', then=4),
            When(status='not-applied', then=5),
            output_field=IntegerField(),
        )
        return super().get_queryset().annotate(
            status_order=status_order
        ).order_by('status_order')

    def get_object(self):
        registration_number = self.request.query_params.get('roll_no__registration_number')
        if not registration_number:
            raise ValidationError({'error': 'Registration number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return self.queryset.get(roll_no__registration_number=registration_number)
        except Bonafide.DoesNotExist:
            raise ValidationError({'error': 'Details are not found.'}, status=status.HTTP_404_NOT_FOUND)

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


class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ['subject_name', 'subject_code', 'instructor']

    def create(self, request, *args, **kwargs):
        if self.request.user.role not in ['admin', 'faculty']:
            raise PermissionDenied({'error': 'Only admin or staff users can add subjects data.'})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user.role not in ['admin', 'faculty']:
            raise PermissionDenied({'error': 'Only admin or staff users can add subjects data.'})
        return super().create(request, *args, **kwargs)


class SemesterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['semester_name', 'branch']
    ordering_fields = '__all__'
    ordering = ['semester_name', ]

    def create(self, request, *args, **kwargs):
        if self.request.user.role not in ['admin', 'faculty']:
            raise ValidationError({'error': 'Only admin or staff users can create semester data.'})
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        if self.request.user.role not in ['admin', 'faculty']:
            raise ValidationError({'error': 'Only admin or staff users can update semester data.'})
        serializer.save()

    def perform_create(self, serializer):
        if self.request.user.role not in ['admin', 'faculty']:
            raise ValidationError({'error': 'Only admin or staff users can create semester data.'})
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SemesterRegistrationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['student__user__registration_number']
    renderer_classes = [UserRenderer]
    queryset = Semester_Registration.objects.all()
    serializer_class = SemesterRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()


class HostelAllotmentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStudentOrAdmin | IsCaretakerOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__registration_number', 'status']
    queryset = Hostel_Allotment.objects.all()
    serializer_class = HostelAllotmentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class HostelRoomAllotmentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCaretakerOrAdmin | IsStudentOrAdmin]
    renderer_classes = [UserRenderer]
    filter_backends = [filters.SearchFilter]
    search_fields = ['registration_details__user__registration_number']
    queryset = Hostel_Room_Allotment.objects.all()
    serializer_class = HostelRoomAllotmentSerializer

    def create(self, request, *args, **kwargs):
        if not (request.user.role == 'admin' or request.user.role == 'caretaker'):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            hostel_room_allotment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MessFeeCreateSet(APIView):
    queryset = Fees_model.objects.all()
    serializer_class = MessFeeSerializer
    permission_classes = [IsAuthenticated, IsCaretakerOrAdmin]

    def post(self, request, format=None):
        serializer = MessFeeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'data added succesfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateMessFeeViewset(APIView):
    permission_classes = [IsAuthenticated, IsCaretakerOrAdmin]

    def put(self, request, pk, format=None):
        if pk != 1:
            return Response({'error': 'invalid pk'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fee = Fees_model.objects.get(pk=pk)
        except Fees_model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MessFeeSerializer(fee, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'data updated succesfully'}, status=status.HTTP_202_ACCEPTED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetMessFeeViewset(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=1, format=None):
        if pk:
            try:
                fee = Fees_model.objects.get(pk=pk)
            except Fees_model.DoesNotExist:
                return Response({"message": "ID does not Exists"}, status.HTTP_404_NOT_FOUND)
            serializer = MessFeeSerializer(fee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            fee = Fees_model.objects.all()
            serializer = MessFeeSerializer(fee, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class MessFeePaymentCreateViewset(viewsets.ModelViewSet):
    renderer_classes = [UserRenderer]
    serializer_class = MessFeePaymentSerializer
    queryset = Mess_fee_payment.objects.all()
    permission_classes = [IsAuthenticated, IsCaretakerOrAdmin | IsStudentOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['registration_details__registration_details__user__registration_number']

    def get(self, request, *args, **kwargs):
        mess_fee_payments = Mess_fee_payment.objects.all()
        serializer = MessFeePaymentSerializer(mess_fee_payments, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = MessFeePaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessFeePaymentDetailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Mess_fee_payment.objects.get(pk=pk)
        except Mess_fee_payment.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        mess_fee_payment = self.get_object(pk)
        serializer = MessFeePaymentSerializer(mess_fee_payment)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        mess_fee_payment = self.get_object(pk)
        serializer = MessFeePaymentSerializer(mess_fee_payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        mess_fee_payment = self.get_object(pk)
        mess_fee_payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HostelAllotmentStatusUpdateView(APIView):
    serializer_class = HostelAllotmentStatusUpdateSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated, IsCaretakerOrAdmin]

    def get_object(self, pk):
        try:
            return Hostel_Allotment.objects.get(pk=pk)
        except Hostel_Allotment.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        hostel_allotment = self.get_object(pk)
        serializer = HostelAllotmentStatusUpdateSerializer(hostel_allotment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestRoomAllotmentViewSet(viewsets.ModelViewSet):
    serializer_class = GuestRoomAllotmentSerializer
    queryset = Guest_room_request.objects.all()
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    filter_backends = [SearchFilter]
    search_fields = ['user__registration_number']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'data': serializer.data, 'message': 'Complaint successfully created'},
                            status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Overall_no_duesViewSet(viewsets.ModelViewSet):
    serializer_class = Overall_No_Due_Serializer
    queryset = Overall_No_Dues_Request.objects.all()
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    renderer_classes = [UserRenderer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Overall_No_Dues_Request.objects.filter(user=user)
        return Overall_No_Dues_Request.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'Request was applied successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Hostel_No_dueViewset(viewsets.ModelViewSet):
    serializer_class = HostelNoDuesSerializer
    queryset = Hostel_No_Due_request.objects.all()
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    renderer_classes = [UserRenderer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 'Request was applied successfully'}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Hostel_No_Due_request.objects.filter(user=user)
        return Hostel_No_Due_request.objects.all()


class NoDuesListViewSet(viewsets.ModelViewSet):
    queryset = No_Dues_list.objects.all()
    serializer_class = No_Due_ListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['request_id__user__registration_number']


class SemesterVerificationViewSet(viewsets.ModelViewSet):
    queryset = VerifySemesterRegistration.objects.all()
    serializer_class = SemesterVerificationSerializer
    permission_classes = [IsAuthenticated, IsFacultyOrAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['status', 'registration_details_info__student_details__user__registration_number']

    def perform_create(self, serializer):
        serializer.save()
