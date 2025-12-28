from rest_framework import serializers
from .models import Seller, SellerDocument

class SellerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDocument
        fields = ['id', 'document', 'doc_type', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class SellerSerializer(serializers.ModelSerializer):
    documents = SellerDocumentSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'user', 'business_name', 'is_verified', 'status', 'documents', 'created_at']
        read_only_fields = ['id', 'user', 'is_verified', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        # Ensure user doesn't already have a seller profile
        if Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have already applied to be a seller.")
        
        seller = Seller.objects.create(user=user, **validated_data)
        return seller
