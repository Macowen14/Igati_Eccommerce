from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Seller

User = get_user_model()

class SellerWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.client.force_authenticate(user=self.user)
        
    def test_apply_become_seller(self):
        # 1. Apply to become a seller
        response = self.client.post('/api/sellers/register/', {
            'business_name': 'Best Shop'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Seller.objects.filter(user=self.user).exists())
        seller = Seller.objects.get(user=self.user)
        self.assertEqual(seller.business_name, 'Best Shop')
        self.assertEqual(seller.status, 'pending')
        self.assertFalse(seller.is_verified)
        
        # 2. Check status
        response = self.client.get('/api/sellers/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
        
        # 3. Upload document
        file_content = b"fake document content"
        test_file = SimpleUploadedFile("doc.pdf", file_content, content_type="application/pdf")
        
        response = self.client.post('/api/sellers/upload-doc/', {
            'document': test_file,
            'doc_type': 'Business License'
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(seller.documents.count(), 1)
        
        # 4. Verification (Admin Action Simulation)
        seller.status = 'approved'
        seller.is_verified = True
        seller.save()
        
        # 5. Check status again
        response = self.client.get('/api/sellers/status/')
        self.assertEqual(response.data['status'], 'approved')
        self.assertTrue(response.data['is_verified'])

    def test_duplicate_application(self):
        Seller.objects.create(user=self.user, business_name="Old Shop")
        response = self.client.post('/api/sellers/register/', {
            'business_name': 'New Shop'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
