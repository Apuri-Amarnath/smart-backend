from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegistrationView, UserLoginView, UserProfileView, UserLogoutView, update, CollegeViewSet, \
    BonafideViewSet, ChangePasswordView, SemesterViewSet, SubjectViewSet, TokenRefresh, SemesterRegistrationViewset, \
    HostelRoomAllotmentViewset, MessFeePaymentCreateViewset, HostelAllotmentViewset, MessFeeCreateSet, \
    UpdateMessFeeViewset, GetMessFeeViewset, HostelAllotmentStatusUpdateView, MessFeePaymentDetailView, \
    GuestRoomAllotmentViewSet, ComplaintViewSet, Overall_no_duesViewSet, Hostel_No_dueViewset, NoDuesListViewSet, \
    SemesterVerificationViewSet, NotificationsViewSet, CollegeRequestViewSet, CollegeSlugListView

router = DefaultRouter()
router.register(r'colleges', CollegeViewSet, basename='college-details')
router.register(r'bonafide', BonafideViewSet, basename='bonafide-details')
router.register(r'semester', SemesterViewSet, basename='semester')
router.register(r'subject', SubjectViewSet, basename='subjects')
router.register(r'semester-registrations', SemesterRegistrationViewset, basename='semester_registration')
router.register(r'hostel-room-allotments', HostelRoomAllotmentViewset, basename='hostel_room_allotment')
router.register(r'hostel-allotments', HostelAllotmentViewset, basename='hostel_allotment')
router.register(r'guest-room-allotments', GuestRoomAllotmentViewSet, basename='guest_room_allotment')
router.register(r'complaints', ComplaintViewSet, basename='complaints')
router.register(r'overall-no-dues', Overall_no_duesViewSet, basename='overall_no_dues')
router.register(r'hostel-no-dues', Hostel_No_dueViewset, basename='hostel_no_dues')
router.register(r'No-dues-list', NoDuesListViewSet, basename='no_dues_list')
router.register(r'mess-fees-payment', MessFeePaymentCreateViewset, basename='mess_fee_payment')
router.register(r'verify-semester-registration', SemesterVerificationViewSet, basename='verify_semester')
router.register(r'notification', NotificationsViewSet, basename='notifications')
router.register(r'college-requests', CollegeRequestViewSet, basename='college_requests')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('<slug:slug>/profile/', UserProfileView.as_view(), name='profile-college-wise'),
    path('update_server/', update, name='update'),
    path('token/refresh/', TokenRefresh.as_view(), name='token_refresh'),
    path('fees/create/', MessFeeCreateSet.as_view(), name='create_fee'),
    path('fees/update/<int:pk>/', UpdateMessFeeViewset.as_view(), name='update_fee'),
    path('fees/<int:pk>/', GetMessFeeViewset.as_view(), name='get-fee'),
    path('fees/', GetMessFeeViewset.as_view(), name='fees-list'),
    path('hostel-allotments/<int:pk>/update-status/', HostelAllotmentStatusUpdateView.as_view(),
         name='host_allotments_status_update'),
    path('', include(router.urls), ),
    path('college/<slug:slug>/', CollegeViewSet.as_view({'get': 'retrieve'}), name='college'),
    path('<slug:slug>/register/', UserRegistrationView.as_view(), name='register-college-wise'),
    path('colleges-slugs/', CollegeSlugListView.as_view(), name='college-slug-list')
]
