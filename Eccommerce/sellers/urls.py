from django.urls import path
from .views import BecomeSellerView, SellerDashboardView

urlpatterns = [
    path('register/', BecomeSellerView.as_view(), name='become-seller'),
    path('status/', SellerDashboardView.as_view(), name='seller-status'),
]
