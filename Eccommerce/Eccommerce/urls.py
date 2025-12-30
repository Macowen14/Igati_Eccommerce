from django.contrib import admin
from django.urls import path, include
from MarketplaceApp.views import*
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.routers import DefaultRouter
from MarketplaceApp.views import ProductViewSet, InventoryViewSet,CategoryViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'categories', CategoryViewSet , basename='category')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/user/register/', UserCreate.as_view(), name='user_create'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('callback/', google_login_callback, name='google_login_callback'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('api/validate-google-token/', validate_google_token, name='validate_google_token'),
    path('api/sellers/', include('sellers.urls')),
]