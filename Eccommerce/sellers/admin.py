from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'status', 'is_verified', 'created_at')
    list_filter = ('status', 'is_verified')
    search_fields = ('business_name', 'user__username', 'user__email')
    readonly_fields = ('created_at',)
    actions = ['approve_sellers', 'reject_sellers']

    def approve_sellers(self, request, queryset):
        queryset.update(status='APPROVED', is_verified=True)
    approve_sellers.short_description = "Approve selected sellers"

    def reject_sellers(self, request, queryset):
        queryset.update(status='REJECTED', is_verified=False)
    reject_sellers.short_description = "Reject selected sellers"
