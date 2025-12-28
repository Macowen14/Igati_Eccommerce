from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Seller, SellerDocument
from .serializers import SellerSerializer, SellerDocumentSerializer

class BecomeSellerView(generics.CreateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SellerStatusView(generics.RetrieveAPIView):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.seller_profile
        except Seller.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "Not a seller"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SellerDocumentUploadView(generics.CreateAPIView):
    serializer_class = SellerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        try:
            seller = self.request.user.seller_profile
            serializer.save(seller=seller)
        except Seller.DoesNotExist:
            raise serializers.ValidationError({"detail": "You must be a registered seller to upload documents."})
