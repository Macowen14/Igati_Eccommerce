from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Inventory, Category, Order, order_product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class InventorySerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.username', read_only=True)  
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Inventory  
        fields = ['id', 'product', 'product_name', 'seller', 'seller_name', 
                  'stock', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    inventories = InventorySerializer(many=True, read_only=True)
    seller_count = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)  
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'category', 'category_name', 'price', 
                  'total_stock_quantity', 'image', 'seller_count', 'inventories',
                  'created_at', 'updated_at']
        read_only_fields = ['slug', 'total_stock_quantity', 'created_at', 'updated_at']
    
    def get_seller_count(self, obj):
        """Get number of verified sellers for this product"""
        return obj.inventories.filter(is_verified=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing products without inventories"""
    seller_count = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)  # ← Added
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'category', 'category_name', 'price', 
                  'total_stock_quantity', 'image', 'seller_count', 'created_at']
    
    def get_seller_count(self, obj):
        return obj.inventories.filter(is_verified=True).count()

    
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField() 
    
    class Meta:
        model = Category  
        fields = ['id', 'name', 'description', 'product_count']
    
    def get_product_count(self, obj):
        """Get number of products in this category"""
        return obj.product_set.count()


class OrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.URLField(source='product.image', read_only=True) 

    class Meta:
        model = order_product
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 
                  'price_at_purchase', 'units', 'created_at']