from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegistrationView, UserLoginView, UserProfileView, UserLogoutView, update, CollegeViewSet, \
    BonafideViewSet

router = DefaultRouter()
router.register(r'college', CollegeViewSet, basename='college-details')
router.register(r'bonafide', BonafideViewSet, basename='bonafide-details')
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('update_server/', update, name='update'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls),)
]
