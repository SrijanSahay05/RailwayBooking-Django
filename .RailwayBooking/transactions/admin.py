from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin interface for Wallet model.
    """

    list_display = ("user", "balance", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(self, request, obj=None):
        """
        Make balance field readonly for existing Wallets to prevent manual updates.
        """
        if obj:
            return self.readonly_fields + ("balance",)
        return self.readonly_fields


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    """

    list_display = (
        "id",
        "sender_wallet",
        "receiver_wallet",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "sender_wallet__user__username",
        "receiver_wallet__user__username",
        "status",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        """
        Disable add permission for transactions to ensure they are created programmatically.
        """
        return False
