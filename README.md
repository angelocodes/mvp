# Analytical Method Validation MVP

A Django REST Framework application implementing ICH Q2(R1) compliant analytical method validation for pharmaceutical assays using HPLC or UV techniques.

## Features

### Authentication & User Management
- User authentication with session-based login/logout
- Role-based access control (Analyst, Reviewer, QA)
- User profile management

### Project Management
- Create validation projects with method details
- Workflow management through validation steps
- Project approval workflow

### Validation Steps (ICH Q2 Compliant)
- **Linearity**: Regression analysis with r² ≥ 0.99
- **Accuracy**: Recovery testing (80-120% acceptance)
- **Precision**: Repeatability with %RSD limits
- **LOD/LOQ**: Detection and quantification limits

### Audit Trail
- Complete audit logging for all actions
- Immutable audit records
- QA-only audit log access

### Reporting
- PDF report generation for approved validations
- Downloadable validation reports

## Technology Stack

- **Backend**: Django 6.0.1 + Django REST Framework
- **Database**: SQLite (development)
- **PDF Generation**: ReportLab
- **Statistical Calculations**: NumPy
- **Authentication**: Django sessions

## Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd mvp
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Database Setup
```bash
cd mvp
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

### 4. Run Development Server
```bash
python manage.py runserver
```
Server will be available at http://127.0.0.1:8000/

## API Endpoints

### Authentication
```
POST /api/auth/login/
GET  /api/users/me/
POST /api/auth/logout/
```

### User Management (QA/Admin only)
```
GET  /api/users/
POST /api/users/
GET  /api/users/{id}/
PUT  /api/users/{id}/
DELETE /api/users/{id}/
```

### Project Management
```
GET  /api/projects/
POST /api/projects/
GET  /api/projects/{id}/
PUT  /api/projects/{id}/
DELETE /api/projects/{id}/
GET  /api/projects/{id}/workflow/
POST /api/projects/{id}/start-validation/
POST /api/projects/{id}/review/
POST /api/projects/{id}/approve/
```

### Validation APIs
```
POST /api/projects/{id}/linearity/
GET  /api/projects/{id}/linearity/
POST /api/projects/{id}/accuracy/
GET  /api/projects/{id}/accuracy/
POST /api/projects/{id}/precision/
GET  /api/projects/{id}/precision/
POST /api/projects/{id}/lod-loq/
GET  /api/projects/{id}/lod-loq/
```

### Audit Trail (QA only)
```
GET /api/audit/
GET /api/audit/{project_id}/
```

### Reports
```
POST /api/projects/{id}/report/  # Generate PDF
GET  /api/projects/{id}/report/  # Download PDF
```

## Testing the Application

### 1. Load Test Data
The system comes with pre-configured test data. Run this command to populate the database:

```bash
cd mvp
python manage.py create_test_data
```

This creates:
- **Test Users** (password: `testpass123` for all):
  - `analyst1` (Analyst) - Can create and manage validation projects
  - `analyst2` (Analyst) - Additional analyst user
  - `reviewer1` (Reviewer) - Can review validation data
  - `qa1` (QA) - Quality assurance and final approval authority

- **Test Projects** in different stages:
  - "Assay Method A - HPLC" (Draft - ready for validation)
  - "Assay Method B - UV" (In linearity stage)
  - "Assay Method C - HPLC" (Under review)
  - "Assay Method D - UV" (Approved with full validation data)

- **Complete Validation Data** for approved projects
- **Sample Audit Logs** demonstrating system activity

### 2. Login and Test Different Roles

#### As ANALYST (`analyst1` / `testpass123`):
- View dashboard with project statistics
- Create new validation projects
- Submit linearity, accuracy, precision, LOD/LOQ data
- Experience enhanced data entry with file uploads and confirmations

#### As REVIEWER (`reviewer1` / `testpass123`):
- Access review dashboard with pending projects
- Perform detailed parameter-level reviews
- Make approve/reject/correction decisions
- Experience scientific review workflow

#### As QA (`qa1` / `testpass123`):
- Access comprehensive QA administration
- Review audit trails and system compliance
- Perform final project approvals
- Manage users and system governance

### 3. Test Complete Workflow

#### Create and Validate a Project:
```bash
# 1. Login as analyst1
# 2. Create new project via web interface
# 3. Start validation workflow
# 4. Submit linearity data (use: 25,50,75,100,125 for concentrations and 2500,5000,7500,10000,12500 for responses)
# 5. Continue through accuracy, precision, LOD/LOQ
# 6. Submit for review
```

#### Review Process:
```bash
# 1. Login as reviewer1
# 2. Access review dashboard
# 3. Open project for detailed review
# 4. Review each validation parameter
# 5. Approve or request corrections
# 6. Submit review decision
```

#### QA Approval:
```bash
# 1. Login as qa1
# 2. Access QA administration
# 3. Review final approvals
# 4. Investigate audit trails
# 5. Grant final approval
# 6. Generate validation reports
```

### 4. API Testing Examples

#### Create a Validation Project:
```bash
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "method_name": "Assay Method Test",
    "method_type": "assay",
    "technique": "hplc",
    "guideline": "ich_q2",
    "product_name": "Test Product"
  }'
```

#### Submit Linearity Data:
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/linearity/ \
  -H "Content-Type: application/json" \
  -d '{
    "concentrations": [25, 50, 75, 100, 125],
    "responses": [2500, 5000, 7500, 10000, 12500]
  }'
```

### 3. Start Validation Workflow
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/start-validation/
```

### 4. Submit Validation Data

#### Linearity
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/linearity/ \
  -H "Content-Type: application/json" \
  -d '{
    "concentrations": [0.1, 0.2, 0.3, 0.4, 0.5],
    "responses": [0.12, 0.22, 0.31, 0.42, 0.53]
  }'
```

#### Accuracy
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/accuracy/ \
  -H "Content-Type: application/json" \
  -d '{
    "level": "100",
    "measured_values": [98.5, 101.2, 99.8, 100.5, 102.1]
  }'
```

#### Precision
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/precision/ \
  -H "Content-Type: application/json" \
  -d '{
    "replicate_values": [10.1, 10.2, 9.9, 10.0, 10.3]
  }'
```

#### LOD/LOQ
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/lod-loq/ \
  -H "Content-Type: application/json" \
  -d '{
    "blank_responses": [0.01, 0.02, 0.01, 0.015, 0.018]
  }'
```

### 5. Complete Workflow
```bash
# Review (as Reviewer)
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/review/ \
  -H "Content-Type: application/json" \
  -d '{"comment": "All validation criteria met"}'

# Approve (as QA)
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/approve/
```

### 6. Generate Report
```bash
curl -X POST http://127.0.0.1:8000/api/projects/{project_id}/report/
# Download PDF
curl http://127.0.0.1:8000/api/projects/{project_id}/report/ -o report.pdf
```

### 7. Check Audit Logs (QA only)
```bash
curl http://127.0.0.1:8000/api/audit/
```

## Validation Rules (ICH Q2(R1))

### Linearity
- Correlation coefficient (r²) ≥ 0.99
- Y-intercept within reasonable limits

### Accuracy
- Recovery: 80-120%
- RSD: ≤2.0% (≥6 replicates), ≤5.0% (3-5 replicates)

### Precision
- RSD: ≤2.0% (≥6 replicates), ≤5.0% (3-5 replicates)

### LOD/LOQ
- LOD = 3.3 × σ / S
- LOQ = 10 × σ / S
- Where σ is blank standard deviation, S is slope

## Architecture

### Apps Structure
```
apps/
├── users/          # Authentication & user management
├── projects/       # Project CRUD & workflow
├── validation/     # Validation data & rules
│   ├── rules/      # ICH compliance rules
│   └── workflow.py # State management
├── stats/          # Statistical calculations
├── audit/          # Audit logging
└── reports/        # PDF generation
```

### Key Principles
- **Thin Views**: Business logic in services/rules
- **Deterministic**: Same input = same result
- **Auditable**: All actions logged
- **Compliant**: ICH Q2(R1) guidelines followed
- **Secure**: Role-based permissions

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all functions
- Keep validation logic server-side only

## Production Deployment

1. Set `DEBUG = False`
2. Configure production database
3. Set up proper WSGI server (gunicorn)
4. Configure static files serving
5. Set up proper logging
6. Configure HTTPS
7. Set up backups for database

## Contributing

1. Create feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Follow code style guidelines
5. Submit pull request

## License

[Add appropriate license]
