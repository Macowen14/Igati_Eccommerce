from django.contrib import admin
from .models import Product, Inventory, Category, Order, order_product, Profile


# 1. Define Inlines first so they can be used in Admins below
class OrderProductInline(admin.TabularInline):
    model = order_product
    extra = 1
    fields = ['product', 'quantity', 'price_at_purchase', 'units']


# 2. Register Models
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'total_stock_quantity', 'created_at']  
    search_fields = ['name', 'description']
    list_filter = ['category', 'created_at']
    readonly_fields = ['slug', 'total_stock_quantity', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}  


@admin.register(Inventory)  # ← Fixed: Uppercase
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'stock', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['product__name', 'seller__user__username']  
    actions = ['verify_inventory', 'unverify_inventory']
    readonly_fields = ['created_at', 'updated_at'] 
    
    def verify_inventory(self, request, queryset):
        queryset.update(is_verified=True)
        # Update stock for all affected products
        for inv in queryset:
            inv.product.update_total_stock()
    verify_inventory.short_description = "Verify selected inventories"
    
    def unverify_inventory(self, request, queryset):
        queryset.update(is_verified=False)
        # Update stock for all affected products
        for inv in queryset:
            inv.product.update_total_stock()
    unverify_inventory.short_description = "Unverify selected inventories"


@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'total_quantity', 'created_at'] 
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email'] 
    readonly_fields = ['created_at', 'updated_at'] 
    inlines = [OrderProductInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'location', 'updated_at']
    search_fields = ['user__username', 'phone_number', 'location']
    readonly_fields = ['updated_at'] 


# Register order_product separately if you want to see the full list of items sold
@admin.register(order_product)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_purchase', 'units', 'created_at']  
    list_filter = ['created_at']
    search_fields = ['product__name', 'order__user__username']  
    readonly_fields = ['created_at', 'updated_at']  