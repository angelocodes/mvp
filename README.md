# Analytical Method Validation MVP

A comprehensive Django-based web application for managing ICH Q2(R1) compliant analytical method validation in pharmaceutical laboratories. This system supports HPLC and UV assay techniques with full workflow management, audit trails, and PDF report generation.

## Features

### Core Functionality
- **User Authentication & Role Management**
  - Session-based authentication with Django
  - Three user roles: Analyst, Reviewer, and QA
  - Role-based access control (RBAC)

- **Project Management**
  - Create and manage validation projects
  - Support for HPLC and UV techniques
  - ICH Q2(R1) guideline compliance
  - Complete workflow from draft to approval

- **Validation Steps (ICH Q2 Compliant)**
  - **Linearity**: Regression analysis with r² ≥ 0.99 requirement
  - **Accuracy**: Recovery testing at 80%, 100%, and 120% levels
  - **Precision**: Repeatability with %RSD calculations
  - **LOD/LOQ**: Detection and quantification limits determination

- **Workflow Management**
  - Four-stage validation workflow
  - Automatic workflow advancement on successful validation
  - Review and approval gates
  - Project locking after approval

- **Audit Trail**
  - Complete audit logging for all actions
  - Immutable audit records
  - QA-only audit log access
  - Filter and export capabilities

- **Reporting**
  - PDF report generation using ReportLab
  - Downloadable validation reports
  - Professional formatting

### Technical Features
- Modern, responsive UI with gradient designs
- Real-time form validation
- Interactive modals for data entry
- Toast notifications for user feedback
- Mobile-friendly responsive design
- Professional color scheme and typography

## Technology Stack

- **Backend**: Django 5.x + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **PDF Generation**: ReportLab
- **Statistical Calculations**: NumPy
- **Frontend**: Vanilla JavaScript with modern CSS
- **Authentication**: Django Session Authentication

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mvp
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Django>=5.0,<6.0
- djangorestframework>=3.14.0
- numpy>=1.24.0
- reportlab>=4.0.0
- pytest>=7.0.0

### 4. Database Setup

Navigate to the Django project directory and run migrations:

```bash
cd mvp
python manage.py migrate
```

### 5. Create Superuser

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin user.

### 6. Load Test Data (Optional)

Populate the database with test users and sample projects:

```bash
python manage.py create_test_data
```

This creates:
- **Test Users** (password: `testpass123` for all):
  - `analyst1` (Analyst)
  - `analyst2` (Analyst)
  - `reviewer1` (Reviewer)
  - `qa1` (QA)

- **Sample Projects** in various stages
- **Complete Validation Data** for approved projects

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Usage Guide

### First Steps

1. **Login**: Navigate to http://127.0.0.1:8000/login/
2. **Use test credentials** if you loaded test data:
   - Analyst: `analyst1` / `testpass123`
   - Reviewer: `reviewer1` / `testpass123`
   - QA: `qa1` / `testpass123`

### As an Analyst

1. **Dashboard**: View project statistics and recent projects
2. **Create Project**: 
   - Go to Projects page
   - Click "Create New Project"
   - Fill in method details (name, product, technique)
3. **Start Validation**:
   - Open a project in "Draft" status
   - Click "Start Validation"
4. **Complete Validation Steps**:
   - **Linearity**: Enter 5+ concentration-response pairs
   - **Accuracy**: Select level (80/100/120%) and enter 3+ recovery values
   - **Precision**: Enter 6+ replicate measurements
   - **LOD/LOQ**: Enter 5+ blank responses
5. **Submit for Review**: System automatically advances to review stage

### As a Reviewer

1. **Access Review Dashboard**: Click "Reviews" in navigation
2. **Review Projects**: View projects pending review
3. **Detailed Review**:
   - Open a project for review
   - Verify data integrity and calculations
   - Review each validation parameter
   - Make approve/reject/correction decisions
4. **Submit Review**: Provide comments and final decision

### As QA

1. **Admin Dashboard**: Access QA Administration panel
2. **Final Approvals**: Review and approve validated projects
3. **Audit Trail**: 
   - Monitor system activities
   - Filter by time range, user, or action
   - Export audit logs
4. **User Management**: Create and manage system users
5. **Generate Reports**: Create PDF validation reports

## API Documentation

### Authentication Endpoints

```
POST /api/auth/login/          # Login
POST /api/auth/logout/         # Logout
GET  /api/users/me/            # Get current user
```

### User Management (QA only)

```
GET    /api/users/             # List all users
POST   /api/users/             # Create user
GET    /api/users/{id}/        # Get user details
PUT    /api/users/{id}/        # Update user
DELETE /api/users/{id}/        # Delete user
```

### Project Management

```
GET    /api/projects/                   # List projects
POST   /api/projects/                   # Create project
GET    /api/projects/{id}/              # Get project details
PUT    /api/projects/{id}/              # Update project
DELETE /api/projects/{id}/              # Delete project
POST   /api/projects/{id}/start-validation/    # Start validation
POST   /api/projects/{id}/review/              # Submit review
POST   /api/projects/{id}/approve/             # Approve project
```

### Validation Endpoints

```
GET/POST /api/validation/projects/{id}/linearity/   # Linearity data
GET/POST /api/validation/projects/{id}/accuracy/    # Accuracy data
GET/POST /api/validation/projects/{id}/precision/   # Precision data
GET/POST /api/validation/projects/{id}/lod-loq/     # LOD/LOQ data
```

### Reports

```
POST /api/reports/{project_id}/     # Generate PDF report
GET  /api/reports/{project_id}/     # Download PDF report
```

### Audit Trail (QA only)

```
GET /api/audit/                     # List all audit logs
GET /api/audit/{project_id}/        # Audit logs for specific project
```

## Project Structure

```
mvp/
├── mvp/                          # Django project settings
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # Root URL configuration
│   ├── api_urls.py               # API endpoint routing
│   └── wsgi.py                   # WSGI configuration
├── apps/
│   ├── users/                    # User management
│   │   ├── models.py             # User model with roles
│   │   ├── views.py              # Authentication views
│   │   ├── serializers.py        # API serializers
│   │   └── permissions.py        # Role-based permissions
│   ├── projects/                 # Project management
│   │   ├── models.py             # Project model
│   │   ├── views.py              # Project CRUD views
│   │   └── serializers.py        # Project serializers
│   ├── validation/               # Validation logic
│   │   ├── models.py             # Validation data models
│   │   ├── views.py              # Validation endpoints
│   │   ├── serializers.py        # Validation serializers
│   │   ├── rules/                # ICH Q2 validation rules
│   │   │   ├── linearity.py      # Linearity calculations
│   │   │   ├── accuracy.py       # Accuracy calculations
│   │   │   ├── precision.py      # Precision calculations
│   │   │   └── lod_loq.py        # LOD/LOQ calculations
│   │   └── workflow.py           # Workflow state management
│   ├── stats/                    # Statistical calculations
│   │   └── calculations.py       # NumPy-based statistics
│   ├── audit/                    # Audit logging
│   │   ├── models.py             # Audit log model
│   │   └── views.py              # Audit API views
│   ├── reports/                  # PDF report generation
│   │   └── views.py              # Report generation views
│   └── frontend/                 # Frontend views
│       ├── views.py              # Template views
│       └── urls.py               # Frontend URL routing
├── templates/                    # HTML templates
│   ├── base.html                 # Base template
│   ├── login.html                # Login page
│   ├── dashboard.html            # Dashboard
│   ├── projects.html             # Projects list
│   ├── project-detail.html       # Project details
│   ├── review.html               # Review interface
│   └── admin.html                # QA administration
├── static/                       # Static assets
│   ├── css/style.css             # Modern styling
│   └── js/                       # JavaScript files
│       ├── api.js                # API client
│       └── utils.js              # Utility functions
└── manage.py                     # Django management script
```

## Validation Rules (ICH Q2(R1))

### Linearity
- Correlation coefficient (r²) ≥ 0.99
- Minimum 5 concentration levels
- Linear regression analysis

### Accuracy (Recovery)
- Recovery range: 80-120%
- Three concentration levels (80%, 100%, 120%)
- Minimum 3 replicates per level

### Precision (Repeatability)
- RSD ≤ 2.0% for 6+ replicates
- RSD ≤ 5.0% for 3-5 replicates
- Minimum 6 measurements recommended

### LOD/LOQ
- **LOD** = 3.3 × σ / S
- **LOQ** = 10 × σ / S
- Where σ = standard deviation of blank responses
- Where S = slope from linearity (response/concentration)

## Development

### Running Tests

```bash
cd mvp
python manage.py test
```

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions
- Keep validation logic server-side only

### Adding New Features

1. Create feature branch
2. Implement with tests
3. Ensure all tests pass
4. Submit pull request

## Production Deployment

### Security Checklist
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS` with your domain
3. Use environment variables for secrets
4. Set up HTTPS/SSL
5. Configure proper logging

### Database
Switch to PostgreSQL for production:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mvp_db',
        'USER': 'mvp_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
Configure static files serving with Whitenoise or nginx:

```bash
python manage.py collectstatic
```

### Web Server
Use gunicorn or uWSGI with nginx:

```bash
gunicorn mvp.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'rest_framework'**
```bash
pip install djangorestframework
```

**Database errors after model changes**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Static files not loading**
```bash
python manage.py collectstatic
```

**Permission denied errors**
- Ensure user has correct role (analyst/reviewer/qa)
- Check that user is authenticated
- Verify permission classes in views

### Getting Help

- Check the Django documentation: https://docs.djangoproject.com/
- Django REST Framework docs: https://www.django-rest-framework.org/
- ICH Q2(R1) Guidelines: https://www.ich.org/

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Contact

For support or questions, please [add your contact information]

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-01  
**Django Version**: 5.x  
**Python Version**: 3.8+
