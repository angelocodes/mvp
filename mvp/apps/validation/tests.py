from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.projects.models import Project
from apps.validation.models import ValidationStep, LinearityData
from apps.validation.rules.linearity import evaluate_linearity
import json

User = get_user_model()


class LinearitySubmissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testanalyst',
            email='test@example.com',
            password='testpass123',
            role='analyst'
        )
        self.client.force_login(self.user)
        
        # Create a project in 'linearity' status
        self.project = Project.objects.create(
            method_name='Test HPLC Method',
            product_name='Test Product',
            technique='hplc',
            method_type='assay',
            guideline='ich_q2',
            status='linearity',
            created_by=self.user
        )
    
    def test_linearity_evaluation_function(self):
        """Test the evaluate_linearity function directly"""
        # Valid linear data
        concentrations = [50, 75, 100, 125, 150]
        responses = [5000, 7500, 10000, 12500, 15000]
        
        result = evaluate_linearity(concentrations, responses)
        
        print("\n=== Linearity Evaluation Test ===")
        print(f"Input concentrations: {concentrations}")
        print(f"Input responses: {responses}")
        print(f"Result: {result}")
        print("================================\n")
        
        self.assertIn('status', result)
        self.assertIn('metrics', result)
        self.assertIn('justification', result)
    
    def test_linearity_api_submission(self):
        """Test submitting linearity data via API"""
        url = f'/api/validation/projects/{self.project.id}/linearity/'
        
        data = {
            'concentrations': [50, 75, 100, 125, 150],
            'responses': [5000, 7500, 10000, 12500, 15000]
        }
        
        print("\n=== API Submission Test ===")
        print(f"URL: {url}")
        print(f"Request data: {data}")
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        print("============================\n")
        
        # Check if submission was successful
        if response.status_code == 200:
            response_data = json.loads(response.content)
            print(f"Success! Response: {response_data}")
        elif response.status_code == 400:
            print(f"Bad request error: {response.content.decode()}")
        elif response.status_code == 404:
            print(f"URL not found - check API endpoint configuration")
        else:
            print(f"Unexpected status code: {response.status_code}")
    
    def test_duplicate_submission(self):
        """Test that duplicate submission is rejected"""
        # First submission
        url = f'/api/validation/projects/{self.project.id}/linearity/'
        data = {
            'concentrations': [50, 75, 100, 125, 150],
            'responses': [5000, 7500, 10000, 12500, 15000]
        }
        
        # First submission
        response1 = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        print("\n=== Duplicate Submission Test ===")
        print(f"First submission status: {response1.status_code}")
        
        # Second submission (should fail)
        response2 = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        print(f"Second submission status: {response2.status_code}")
        print(f"Second submission response: {response2.content.decode()}")
        print("=================================\n")
        
        self.assertEqual(response2.status_code, 400)
