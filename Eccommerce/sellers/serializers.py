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

    id_document = serializers.FileField(write_only=True, required=False)
    business_license = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Seller
        fields = ['id', 'user', 'business_name', 'business_location', 'is_verified', 'status', 'documents', 'created_at', 'id_document', 'business_license']
        read_only_fields = ['id', 'user', 'is_verified', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        # Ensure user doesn't already have a seller profile
        if Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have already applied to be a seller.")
        
        id_doc = validated_data.pop('id_document', None)
        license_doc = validated_data.pop('business_license', None)

        seller = Seller.objects.create(user=user, **validated_data)

        if id_doc:
            SellerDocument.objects.create(seller=seller, document=id_doc, doc_type='ID')
        if license_doc:
            SellerDocument.objects.create(seller=seller, document=license_doc, doc_type='Business License')
            
        return seller
