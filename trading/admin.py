from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from trading.models import User, Portfolio, Transaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'balance', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CryptoNexus', {'fields': ('balance',)}),
    )


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'symbol', 'quantity', 'avg_buy_price', 'updated_at')
    list_filter = ('symbol',)
    search_fields = ('user__email', 'symbol')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'symbol', 'quantity', 'price', 'total', 'timestamp')
    list_filter = ('type', 'symbol')
    search_fields = ('user__email', 'symbol')
    date_hierarchy = 'timestamp'
