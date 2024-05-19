from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.views import APIView

from .models import UserProfile
from .renderers import UserRenderer
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import git


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


# Create your views here.
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'message': 'User creation successful'}, status=status.HTTP_201_CREATED)
        return Response({'message':'user already exits',"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
            raise ValidationError({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        if not self.request.data:
            raise ValidationError({'error':'Empty JSON payload is not allowed.'},status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response({'status':'success','message': 'User profile updated successfully.','user_profile': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status':'error','errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
