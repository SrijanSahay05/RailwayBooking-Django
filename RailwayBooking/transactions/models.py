from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model

user = get_user_model()


class Wallet(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} Wallet"

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        with transaction.atomic():
            # Update the wallet balance
            Wallet.objects.filter(id=self.id).update(balance=F("balance") + amount)
            self.refresh_from_db()

            # Create a transaction record for the deposit
            Transaction.objects.create(
                receiver_wallet=self,
                amount=amount,
                status="COMPLETED",
                created_at=timezone.now(),
            )

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=self.id)
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")

            # Update the wallet balance
            Wallet.objects.filter(id=self.id).update(balance=F("balance") - amount)
            self.refresh_from_db()

            # Create a transaction record for the withdrawal
            Transaction.objects.create(
                sender_wallet=self,
                amount=amount,
                status="COMPLETED",
                created_at=timezone.now(),
            )


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
        ("REVERTED", "REVERTED"),
    )
    sender_wallet = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL, null=True, related_name="sent_transactions"
    )
    receiver_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        related_name="received_transactions",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

    def complete_transaction(self):
        with transaction.atomic():
            if (self.status == "PENDING") and (
                self.sender_wallet.balance >= self.amount
            ):
                self.sender_wallet.withdraw(self.amount)
                self.receiver_wallet.deposit(self.amount)
                self.status = "COMPLETED"
                self.save()
                return True
            else:
                raise ValueError(
                    "Transaction cannot be completed. Insufficient funds or invalid status."
                )

    def revert_transaction(self):
        with transaction.atomic():
            if self.status == "COMPLETED":
                self.sender_wallet.deposit(self.amount)
                self.receiver_wallet.withdraw(self.amount)
                self.status = "REVERTED"
                self.save()
                return True
            else:
                raise ValueError("Transaction cannot be reverted. Invalid status.")
