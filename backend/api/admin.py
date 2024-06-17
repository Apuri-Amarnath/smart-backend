import base64

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.utils.html import format_html

from .models import Semester, Subject, User, UserProfile, PersonalInformation, ContactInformation, AcademicInformation, \
    College, Bonafide, Semester_Registration, Hostel_Allotment, Hostel_Room_Allotment, Hostel_No_Due_request, \
    Guest_room_request, Complaint, Fees_model, Mess_fee_payment, Overall_No_Dues_Request,No_Dues_list

class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('registration_number', 'role')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('registration_number', 'password', 'is_active', 'is_admin', 'role')


class UserModelAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('registration_number', 'role', 'is_admin')
    list_filter = ('is_admin', 'role')
    fieldsets = (
        (None, {'fields': ('registration_number', 'password')}),
        ('Personal info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_admin',)}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('registration_number', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('registration_number',)
    ordering = ('registration_number',)
    filter_horizontal = ()


class BonafideAdmin(admin.ModelAdmin):
    list_display = ['college', 'student', 'roll_no', 'issue_date', 'status', 'supporting_document_display']

    def supporting_document_display(self, obj):
        if obj.supporting_document:
            # Encode the binary data to base64
            encoded_document = base64.b64encode(obj.supporting_document).decode('utf-8')
            # Return the HTML for displaying the image
            return format_html('<img src="data:image/png;base64,{}" width="100" />', encoded_document)
        return "No Image"

    supporting_document_display.short_description = 'Supporting Document'


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)
# ... and, since we're not using Django's built-in permissions,
admin.site.register(UserProfile)
admin.site.register(PersonalInformation)
admin.site.register(AcademicInformation)
admin.site.register(ContactInformation)
admin.site.register(College)
admin.site.register(Bonafide, BonafideAdmin)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(Semester_Registration)
admin.site.register(Hostel_Allotment)
admin.site.register(Hostel_Room_Allotment)
admin.site.register(Hostel_No_Due_request)
admin.site.register(Complaint)
admin.site.register(Guest_room_request)
admin.site.register(Fees_model)
admin.site.register(Mess_fee_payment)
admin.site.register(Overall_No_Dues_Request)
admin.site.register(No_Dues_list)