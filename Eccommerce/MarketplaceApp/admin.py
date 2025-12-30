from django.contrib import admin
from .models import Product, inventory, category, Order, order_product, Profile, Seller

# 1. Define Inlines first so they can be used in Admins below
class OrderProductInline(admin.TabularInline):
    model = order_product
    extra = 1
    fields = ['product', 'quantity', 'price_at_purchase', 'units']

# 2. Register Models
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'total_stock_quantity', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['slug', 'total_stock_quantity']

@admin.register(inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'stock', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['product__name', 'seller__username']
    actions = ['verify_inventory', 'unverify_inventory']
    
    def verify_inventory(self, request, queryset):
        queryset.update(is_verified=True)
    verify_inventory.short_description = "Verify selected inventories"
    
    def unverify_inventory(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_inventory.short_description = "Unverify selected inventories"

@admin.register(category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'created_at']
    list_filter = ['created_at']
    inlines = [OrderProductInline]  

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'location', 'updated_at']

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'is_verified']

# Register order_product separately if you want to see the full list of items sold
@admin.register(order_product)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_purchase']