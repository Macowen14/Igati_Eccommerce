from django.db import models
from django.conf import settings

def seller_document_path(instance, filename):
    # uploads/<business_name>/<filename>
    # instance is SellerDocument, so access seller.business_name
    business_name = instance.seller.business_name
    safe_name = "".join([c for c in business_name if c.isalnum() or c in (' ', '-', '_')]).strip()
    return f'uploads/{safe_name}/{filename}'

class Seller(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    business_registration_number = models.CharField(max_length=100)
    business_address = models.TextField()
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} ({self.user.email})"

class SellerDocument(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to=seller_document_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.seller.business_name}"
