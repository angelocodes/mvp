from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.projects.models import Project
from apps.validation.models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData
from apps.audit.models import AuditLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for the validation system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        # Create test users
        self.create_test_users()

        # Create test projects
        self.create_test_projects()

        # Create validation data
        self.create_validation_data()

        # Create audit logs
        self.create_audit_logs()

        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))


    def create_test_users(self):
        """Create test users for each role"""
        users_data = [
            {
                'username': 'analyst1',
                'email': 'analyst1@company.com',
                'first_name': 'John',
                'last_name': 'Analyst',
                'role': 'analyst',
                'password': 'testpass123'
            },
            {
                'username': 'analyst2',
                'email': 'analyst2@company.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'analyst',
                'password': 'testpass123'
            },
            {
                'username': 'reviewer1',
                'email': 'reviewer1@company.com',
                'first_name': 'Bob',
                'last_name': 'Reviewer',
                'role': 'reviewer',
                'password': 'testpass123'
            },
            {
                'username': 'qa1',
                'email': 'qa1@company.com',
                'first_name': 'Alice',
                'last_name': 'QA',
                'role': 'qa',
                'password': 'testpass123'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role']
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username} ({user.role})')


    def create_test_projects(self):
        """Create test projects in different stages"""
        analyst1 = User.objects.get(username='analyst1')
        analyst2 = User.objects.get(username='analyst2')
        reviewer1 = User.objects.get(username='reviewer1')
        qa1 = User.objects.get(username='qa1')

        projects_data = [
            {
                'method_name': 'Assay Method A - HPLC',
                'product_name': 'Drug Product X',
                'technique': 'hplc',
                'created_by': analyst1,
                'status': 'draft'
            },
            {
                'method_name': 'Assay Method B - UV',
                'product_name': 'Drug Product Y',
                'technique': 'uv',
                'created_by': analyst1,
                'status': 'linearity'
            },
            {
                'method_name': 'Assay Method C - HPLC',
                'product_name': 'Drug Product Z',
                'technique': 'hplc',
                'created_by': analyst2,
                'status': 'review'
            },
            {
                'method_name': 'Assay Method D - UV',
                'product_name': 'Drug Product W',
                'technique': 'uv',
                'created_by': analyst2,
                'status': 'approved',
                'reviewer': reviewer1,
                'qa_approver': qa1,
                'reviewed_at': timezone.now() - timezone.timedelta(days=2),
                'approved_at': timezone.now() - timezone.timedelta(days=1),
                'report_generated': True
            }
        ]

        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                method_name=project_data['method_name'],
                defaults=project_data
            )
            if created:
                self.stdout.write(f'Created project: {project.method_name} ({project.status})')


    def create_validation_data(self):
        """Create validation data for test projects"""
        # Get projects
        project_draft = Project.objects.get(status='draft')
        project_linearity = Project.objects.get(status='linearity')
        project_review = Project.objects.get(status='review')
        project_approved = Project.objects.get(status='approved')

        # Create linearity data for projects in linearity or later stages
        linearity_projects = [project_linearity, project_review, project_approved]

        for project in linearity_projects:
            if not ValidationStep.objects.filter(project=project, step='linearity').exists():
                # Create validation step
                step = ValidationStep.objects.create(
                    project=project,
                    step='linearity',
                    completed=True,
                    passed=True
                )

                # Create linearity data
                LinearityData.objects.create(
                    validation_step=step,
                    concentrations=[25, 50, 75, 100, 125],
                    responses=[2500, 5000, 7500, 10000, 12500],
                    slope=100.0,
                    intercept=0.0,
                    r_squared=1.0,
                    passed=True
                )

        # Create accuracy data for projects in accuracy or later stages
        accuracy_projects = [project_review, project_approved]

        for project in accuracy_projects:
            if not ValidationStep.objects.filter(project=project, step='accuracy').exists():
                step = ValidationStep.objects.create(
                    project=project,
                    step='accuracy',
                    completed=True,
                    passed=True
                )

                AccuracyData.objects.create(
                    validation_step=step,
                    level='100',
                    measured_values=[98.5, 101.2, 99.8, 100.5, 102.1],
                    mean_recovery=100.42,
                    rsd=1.23,
                    passed=True
                )

        # Create precision data for projects in precision or later stages
        precision_projects = [project_review, project_approved]

        for project in precision_projects:
            if not ValidationStep.objects.filter(project=project, step='precision').exists():
                step = ValidationStep.objects.create(
                    project=project,
                    step='precision',
                    completed=True,
                    passed=True
                )

                PrecisionData.objects.create(
                    validation_step=step,
                    replicate_values=[10.1, 10.2, 9.9, 10.0, 10.3],
                    mean=10.1,
                    rsd=1.45,
                    passed=True
                )

        # Create LOD/LOQ data for projects in lod_loq or later stages
        lodloq_projects = [project_review, project_approved]

        for project in lodloq_projects:
            if not ValidationStep.objects.filter(project=project, step='lod_loq').exists():
                step = ValidationStep.objects.create(
                    project=project,
                    step='lod_loq',
                    completed=True,
                    passed=True
                )

                # Get slope from linearity data
                linearity_step = ValidationStep.objects.get(project=project, step='linearity')
                linearity_data = LinearityData.objects.get(validation_step=linearity_step)

                LODLOQData.objects.create(
                    validation_step=step,
                    blank_responses=[0.01, 0.02, 0.01, 0.015, 0.018],
                    slope=linearity_data.slope,
                    lod=0.05,
                    loq=0.15,
                    passed=True
                )

        self.stdout.write('Created validation data for test projects')


    def create_audit_logs(self):
        """Create sample audit logs"""
        users = User.objects.all()
        projects = Project.objects.all()

        audit_entries = [
            {
                'user': users.filter(role='analyst').first(),
                'action': 'create',
                'object_type': 'project',
                'object_id': projects.first().id,
                'details': 'Created new validation project'
            },
            {
                'user': users.filter(role='analyst').first(),
                'action': 'submit',
                'object_type': 'project',
                'object_id': projects.first().id,
                'details': 'Submitted linearity validation data'
            },
            {
                'user': users.filter(role='reviewer').first(),
                'action': 'review',
                'object_type': 'project',
                'object_id': projects.filter(status='review').first().id,
                'details': 'Completed parameter review and approved'
            },
            {
                'user': users.filter(role='qa').first(),
                'action': 'approve',
                'object_type': 'project',
                'object_id': projects.filter(status='approved').first().id,
                'details': 'Final QA approval granted'
            },
            {
                'user': users.filter(role='qa').first(),
                'action': 'login',
                'object_type': 'system',
                'object_id': 0,
                'details': 'User login to QA dashboard'
            }
        ]

        for entry in audit_entries:
            AuditLog.objects.create(**entry)

        self.stdout.write('Created sample audit logs')
