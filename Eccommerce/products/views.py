from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Inventory, Category, Order 
from .serializers import ProductSerializer, ProductListSerializer, InventorySerializer, CategorySerializer, OrderProductSerializer


User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user    


@login_required
def google_login_callback(request):
    user = request.user

    Social_accounts = SocialAccount.objects.filter(user=user)
    print("Social_accounts:", Social_accounts)

    social_account = Social_accounts.first()
    if not social_account:
        return redirect('http://localhost:5173/login/callback/?error=Nosocialaccountfound')

    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print("Google Token:", token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/login/callback/?access_token={access_token}')
    else:
        return redirect('http://localhost:5173/login/callback/?error=Notokenfound')
    

@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
            print("Received Google Access Token:", google_access_token)

            if not google_access_token:
                return JsonResponse({'detail': 'Access token is required.'}, status=400)
            return JsonResponse({'detail': 'Token is valid.'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)  
        

class IsAdminOrReadOnly(permissions.BasePermission):
    """Only admin can create/update/delete"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by minimum stock
        min_stock = self.request.query_params.get('min_stock', None)
        if min_stock:
            queryset = queryset.filter(total_stock_quantity__gte=min_stock)
        
        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def sellers(self, request, pk=None):
        """Get all verified sellers for this product"""
        product = self.get_object()
        inventories = product.inventories.filter(is_verified=True)
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low total stock (less than 10)"""
        products = Product.objects.filter(total_stock_quantity__lt=10)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()  
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can manage inventory
    
    def get_queryset(self):
        queryset = Inventory.objects.all()  # ← Fixed: Uppercase
        
        # Filter by product
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by seller
        seller_id = self.request.query_params.get('seller', None)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Admin verifies a seller's inventory"""
        inventory_obj = self.get_object() 
        inventory_obj.is_verified = True
        inventory_obj.save()
        serializer = self.get_serializer(inventory_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unverify(self, request, pk=None):
        """Admin unverifies a seller's inventory"""
        inventory_obj = self.get_object() 
        inventory_obj.is_verified = False
        inventory_obj.save()
        serializer = self.get_serializer(inventory_obj)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_verification(self, request):
        """Get all unverified inventories"""
        inventories = Inventory.objects.filter(is_verified=False)  
        serializer = self.get_serializer(inventories, many=True)
        return Response(serializer.data)    


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in this category"""
        category_obj = self.get_object()
        products = Product.objects.filter(category=category_obj)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users should only see their own orders
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user when creating an order
        serializer.save(user=self.request.user)