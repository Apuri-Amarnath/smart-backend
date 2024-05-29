import os.path
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.models import User
from .models import User, UserProfile, College, Bonafide, PersonalInformation, AcademicInformation, ContactInformation
from .renderers import UserRenderer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, CollegeSerializer, \
    BonafideSerializer, PersonalInfoSerializer, AcademicInfoSerializer, ContactInformationSerializer, \
    ChangeUserPasswordSerializer, Csv_RegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import subprocess
import git
import csv
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ObjectDoesNotExist

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

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class TokenRefresh(APIView):
    renderer_classes = [UserRenderer]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            college_code = self.request.query_params.get('college_code')
            return self.queryset.get(college_code=college_code)
        except College.DoesNotExist:
            raise ValidationError({'error': 'College does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise ValidationError({'error': 'Only admin or teacher users can create colleges.'})
        serializer.save()

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise ValidationError({'error': 'Only admin or teacher users can create colleges.'})
        serializer.save()


class BonafideViewSet(viewsets.ModelViewSet):
    queryset = Bonafide.objects.all()
    serializer_class = BonafideSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            roll_no = self.request.query_params.get('roll_no')
            return self.queryset.get(roll_no=roll_no)
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
            roll_no = serializer.validated_data.get('roll_no')
            if Bonafide.objects.filter(roll_no=roll_no).exists():
                return Response({'error': 'Bonafide with this roll_no already exists.'},
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
