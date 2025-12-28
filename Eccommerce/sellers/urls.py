from django.urls import path
from .views import BecomeSellerView, SellerStatusView, SellerDocumentUploadView

urlpatterns = [
    path('register/', BecomeSellerView.as_view(), name='become_seller'),
    path('status/', SellerStatusView.as_view(), name='seller_status'),
    path('upload-doc/', SellerDocumentUploadView.as_view(), name='upload_doc'),
]
