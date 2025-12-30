from rest_framework import serializers
from .models import Seller, SellerDocument

class SellerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDocument
        fields = ['id', 'document', 'uploaded_at']

class SellerSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
        max_length=3
    )
    uploaded_documents = SellerDocumentSerializer(many=True, read_only=True, source='documents')

    class Meta:
        model = Seller
        fields = [
            'id', 'user', 'business_name', 'business_email', 'business_phone',
            'business_registration_number', 'business_address', 'documents', 
            'uploaded_documents', 'is_verified', 'status', 'created_at'
        ]
        read_only_fields = ['user', 'is_verified', 'status', 'created_at']

    def validate_documents(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("You can upload a maximum of 3 documents.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        # For CREATE: check if existing profile
        if self.instance is None and Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have already applied to become a seller.")
        return attrs

    def create(self, validated_data):
        documents_data = validated_data.pop('documents')
        seller = Seller.objects.create(**validated_data)
        for doc in documents_data:
            SellerDocument.objects.create(seller=seller, document=doc)
        return seller
    
    def update(self, instance, validated_data):
        # We don't support updating documents here for now, only business details
        if 'documents' in validated_data:
            validated_data.pop('documents') # Ignore docs on update or handle separately if needed
        return super().update(instance, validated_data)
