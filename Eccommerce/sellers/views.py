from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Seller
from .serializers import SellerSerializer
from drf_spectacular.utils import extend_schema

class BecomeSellerView(generics.CreateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SellerDashboardView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser] # Allow multipart for updates too if we eventually support doc updates

    def get_object(self):
        return get_object_or_404(Seller, user=self.request.user)
