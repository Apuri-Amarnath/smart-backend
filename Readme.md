# College Management System

## Overview

The College Management System is a comprehensive web application designed to manage various aspects of a college. This system includes features for handling user management, semester and hostel allotments, fee payments, complaints, notifications, and more. Built using Django and Django REST Framework, it ensures a seamless experience for admins, faculty, students, and caretakers.

## Features

### User Management
- Create, update, and manage user accounts with different roles (admin, faculty, student, caretaker)

### Semester Management
- CRUD operations for managing semesters and semester registrations

### Hostel Allotment
- Allocate and manage hostel rooms and allotments

### Fee Management
- Handle mess fee creation, updates, and payments

### Complaints and Notifications
- Manage student complaints and send notifications

### No Dues Management
- Track and update no dues status across various departments

### Branch and College Management
- Manage branches and college requests

### College ID Count
- Track the number of colleges with specific IDs

## Installation

### Clone the Repository
```bash
git clone https://github.com/your-username/college-management-system.git
cd college-management-system
```
### Create a Virtual Environment
```bash
python -m venv venv
```
### Activate the Virtual Environment
### On Windows:
```bash
venv\Scripts\activate
```
### On macOS/Linux:
```bash
source venv/bin/activate
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Apply Migrations
```bash
python manage.py migrate
```
### Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```
### Run the Development Server
```bash
python manage.py runserver
```
## API Endpoints

### Authentication
- **Login**: `POST /api/user/token/` - Obtain JWT tokens
- **Refresh Token**: `POST /api/user/token/refresh/` - Refresh JWT tokens

### Semester Management
- **Create Semester**: `POST /api/user/semester/`
- **Update Semester**: `PUT /api/user/semester/{id}/`
- **List Semesters**: `GET /api/user/semester/`
- **Retrieve Semester**: `GET /api/user/semester/{id}/`

### Hostel Allotment
- **Create Hostel Allotment**: `POST /api/user/hostel-allotments/`
- **Update Hostel Allotment**: `PUT /api/user/hostel-allotments/{id}/`
- **List Hostel Allotments**: `GET /api/user/hostel-allotments/`
- **Retrieve Hostel Allotment**: `GET /api/user/hostel-allotments/{id}/`

### Mess Fee
- **Create Mess Fee**: `POST /api/user/mess-fees/`
- **Update Mess Fee**: `PUT /api/user/mess-fees/{id}/`
- **Get Mess Fee**: `GET /api/user/mess-fees/{id}/`
- **List Mess Fees**: `GET /api/user/mess-fees/`

### Complaint Management
- **Create Complaint**: `POST /api/user/complaints/`
- **List Complaints**: `GET /api/user/complaints/`
- **Retrieve Complaint**: `GET /api/user/complaints/{id}/`

### Notifications
- **Create Notification**: `POST /api/user/notifications/`
- **List Notifications**: `GET /api/user/notifications/`
- **Delete Notification**: `DELETE /api/user/notifications/{id}/`
- **Delete All Notifications**: `DELETE /api/user/notifications/delete_all/`

### Branch and College Management
- **Create Branch**: `POST /api/user/branch/`
- **List Branches**: `GET /api/user/branch/`
- **List Colleges**: `GET /api/user/colleges/`
- **Retrieve College**: `GET /api/user/college/{slug}/`

### User Management
- **List Users**: `GET /api/user/user-management/`
- **Retrieve User**: `GET /api/user/user-management/{id}/`
- **Update User**: `PUT /api/user/user-management/{id}/`
- **Create User**: `POST /api/user/user-management/`

### College Management
- **Create College Request**: `POST /api/user/college-requests/`
- **List College Requests**: `GET /api/user/college-requests/`
- **Verify College Request**: `POST /api/user/college-requests/{id}/verify/`

### Dynamic URLs
- **Register College-wise**: `POST /api/user/{slug}/register/`
- **User Profile**: `GET /api/user/{slug}/profile/`
- **Bonafide Approval**: `PATCH /api/user/bonafide/{pk}/approve/`
- **Create Mess Fee**: `POST /api/user/fees/create/`
- **Update Mess Fee**: `PUT /api/user/fees/update/{pk}/`
- **Get Mess Fee**: `GET /api/user/fees/{pk}/`
- **List Mess Fees**: `GET /api/user/fees/`
- **Update Hostel Allotment Status**: `PATCH /api/user/hostel-allotments/{pk}/update-status/`
- **Add Branch to College**: `POST /api/user/{slug}/add-branch/`

## Permissions

- **IsAuthenticated**: Required for accessing most endpoints
- **IsAdmin**: Required for admin-specific operations
- **IsFacultyOrAdmin**: Allows faculty and admin users to access certain views
- **IsCaretakerOrAdmin**: Allows caretakers and admin users to access certain views
- **IsStudentOrAdmin**: Allows students and admin users to access certain views
- **IsOfficeOnlyOrAdmin**: Allows office staff and admin users to access certain views

## Development

### Run Tests

```bash
python manage.py test
