from django.db import models
from django.conf import settings


class Seller(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now=True)
    business_location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

class SellerDocument(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='seller_docs/')
    doc_type = models.CharField(max_length=100, help_text="e.g. ID, Business License")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_type} for {self.seller.business_name}"



class category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()# Detailed information of the product
    slug=models.SlugField(unique=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_stock_quantity = models.IntegerField(default=0)
    image = models.URLField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_total_stock(self):
        """Calculate total stock from all inventories"""
        total = self.inventories.aggregate(models.Sum('stock'))['stock__sum'] or 0
        self.total_stock_quantity = total
        self.save()     

class inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)  # Admin verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Meta:
        unique_together = ['product', 'seller']  # One inventory per product-seller pair
        verbose_name_plural = "Inventories"

def __str__(self):
        return f"{self.seller.username} - {self.product.name} ({self.stock})"
    
def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update total stock in product whenever inventory changes
        self.product.update_total_stock()
    

class Profile (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_img = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)
    

class Order(models.Model):
    items = models.ForeignKey('order_product', on_delete=models.CASCADE, related_name='parent_order', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class order_product(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    units = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Payments(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Support(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    SUPPORT_TYPE=(
        ('complain', 'Complain'),
        ('complement', 'Complement'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    support_type=models.CharField(choices=SUPPORT_TYPE, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, default='pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    