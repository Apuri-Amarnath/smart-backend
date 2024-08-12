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
- **Login**: `POST /api/token/` - Obtain JWT tokens

### Semester Management
- **Create Semester**: `POST /api/semesters/`
- **Update Semester**: `PUT /api/semesters/{id}/`
- **List Semesters**: `GET /api/semesters/`
- **Retrieve Semester**: `GET /api/semesters/{id}/`

### Hostel Allotment
- **Create Hostel Allotment**: `POST /api/hostel-allotments/`
- **Update Hostel Allotment**: `PUT /api/hostel-allotments/{id}/`
- **List Hostel Allotments**: `GET /api/hostel-allotments/`
- **Retrieve Hostel Allotment**: `GET /api/hostel-allotments/{id}/`

### Mess Fee
- **Create Mess Fee**: `POST /api/mess-fees/`
- **Update Mess Fee**: `PUT /api/mess-fees/{id}/`
- **Get Mess Fee**: `GET /api/mess-fees/{id}/`
- **List Mess Fees**: `GET /api/mess-fees/`

### Complaint Management
- **Create Complaint**: `POST /api/complaints/`
- **List Complaints**: `GET /api/complaints/`
- **Retrieve Complaint**: `GET /api/complaints/{id}/`

### Notifications
- **Create Notification**: `POST /api/notifications/`
- **List Notifications**: `GET /api/notifications/`
- **Delete Notification**: `DELETE /api/notifications/{id}/`
- **Delete All Notifications**: `DELETE /api/notifications/delete_all/`

### Branch and College Management
- **Create Branch**: `POST /api/branches/`
- **List Branches**: `GET /api/branches/`
- **List Colleges**: `GET /api/colleges/`

### User Management
- **List Users**: `GET /api/users/`
- **Retrieve User**: `GET /api/users/{id}/`
- **Update User**: `PUT /api/users/{id}/`
- **Create User**: `POST /api/users/`

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
