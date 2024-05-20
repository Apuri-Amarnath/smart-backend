from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.models import User
from .models import UserProfile, College, Bonafide, PersonalInformation, AcademicInformation, ContactInformation
from .renderers import UserRenderer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, CollegeSerializer, \
    BonafideSerializer, PersonalInfoSerializer, AcademicInfoSerializer, ContactInformationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import git
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
            return HttpResponse("An error occurred while updating the code.")
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
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'message': 'User creation successful'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'user already exits', "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


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
                return Response({'token': token, 'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': {'non_fields_errors': ['registration number or password is Not valid']}},
                                status=status.HTTP_400_BAD_REQUEST)



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
            raise ValidationError({'error': 'Empty JSON payload is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {'status': 'success', 'message': 'User profile updated successfully.', 'user_profile': serializer.data},
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
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        if not self.request.data:
            raise ValidationError({'error': 'Empty JSON payload is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {'status': 'success', 'message': 'Details uploaded successfully.', 'Bonafide_data': serializer.data},
                status=status.HTTP_200_OK)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
