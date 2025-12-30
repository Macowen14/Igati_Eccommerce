from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product,inventory,category, Order, order_product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class InventorySerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = inventory
        fields = ['id', 'product', 'product_name', 'seller', 'seller_name', 
                  'stock', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    inventories = InventorySerializer(many=True, read_only=True)
    seller_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'category', 'price', 
                  'total_stock_quantity', 'image', 'seller_count', 'inventories',
                  'created_at', 'updated_at']
        read_only_fields = ['slug', 'total_stock_quantity', 'created_at', 'updated_at']
    
    def get_seller_count(self, obj):
        """Get number of sellers for this product"""
        return obj.inventories.filter(is_verified=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing products without inventories"""
    seller_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'price', 
                  'total_stock_quantity', 'image', 'seller_count', 'created_at']
    
    def get_seller_count(self, obj):
        return obj.inventories.filter(is_verified=True).count()
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = category
        fields = ['id', 'name', 'description']

class OrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = order_product
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_purchase', 'units']

class OrderSerializer(serializers.ModelSerializer):
    # This uses the OrderProductInline logic
    items = OrderProductSerializer(many=True, read_only=True, source='order_items')
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'total_price', 'total_quantity', 'items', 'created_at']