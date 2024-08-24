from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegistrationView, UserLoginView, UserProfileView, UserLogoutView, update, CollegeViewSet, \
    BonafideViewSet, ChangePasswordView, SemesterViewSet, SubjectViewSet, TokenRefresh, SemesterRegistrationViewset, \
    HostelRoomAllotmentViewset, MessFeePaymentCreateViewset, HostelAllotmentViewset, \
    GuestRoomAllotmentViewSet, ComplaintViewSet, Overall_no_duesViewSet, Hostel_No_dueViewset, NoDuesListViewSet, \
    SemesterVerificationViewSet, NotificationsViewSet, CollegeRequestViewSet, CollegeSlugListView, \
    CollegeRequestVerificationView, CollegeIDCountView, BranchViewSet, UserManagmentViewSet, HostelRoomRegistrationView, \
    HostelMessFeeViewSet, DepartmentIdCreationView, NoDuesListUpdateView

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
router.register(r'no-dues-list', NoDuesListViewSet, basename='no_dues_list')
router.register(r'mess-fees-payment', MessFeePaymentCreateViewset, basename='mess_fee_payment')
router.register(r'verify-semester-registration', SemesterVerificationViewSet, basename='verify_semester')
router.register(r'branch', BranchViewSet, basename='branch')
router.register(r'user-management', UserManagmentViewSet, basename='user_management')
router.register(r'hostel-room-registrations', HostelRoomRegistrationView, basename='hostel_room_registrations')
router.register(r'hostel-mess-fee', HostelMessFeeViewSet, basename='hostel_mess_fee')

urlpatterns = [
    ## basic urls
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update_server/', update, name='update'),
    path('token/refresh/', TokenRefresh.as_view(), name='token_refresh'),
    path('notification/', NotificationsViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='notifications'),
    path('notification/delete_all_notification/', NotificationsViewSet.as_view({'delete': 'delete_all_notification'}),
         name='delete_all_notification'),
    path('colleges-slugs/', CollegeSlugListView.as_view(), name='college-slug-list'),
    path('college-requests/', CollegeRequestViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='college-requests'),
    path('college-requests/<int:pk>/verify/', CollegeRequestVerificationView.as_view(), name='college-request-verify'),
    path('college/<slug:slug>/', CollegeViewSet.as_view({'get': 'retrieve'}), name='single-college-details'),
    path('id-count/', CollegeIDCountView.as_view({'get': 'list'}), name='college-Idcount'),
    ## dynamic urls
    # path('<slug:slug>/add-branch/',)
    path('<slug:slug>/no-dues-list/<int:pk>/departments/<int:department_id>/',
         NoDuesListUpdateView.as_view(),
         name='update-department'),
    path('<slug:slug>/register/', UserRegistrationView.as_view(), name='register-college-wise'),
    path('<slug:slug>/profile/', UserProfileView.as_view(), name='profile'),
    path('<slug:slug>/bonafide/<int:pk>/approve/', BonafideViewSet.as_view({'patch': 'approve'}),
         name='bonafide-approve'),
    path('<slug:slug>/generate-department/', DepartmentIdCreationView.as_view(), name='generate-department'),
    re_path(r'^(?P<slug>[\w-]+)/', include(router.urls), ),
]
