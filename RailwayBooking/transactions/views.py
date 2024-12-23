from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet


@login_required
def add_money(request):
    """
    View to add money to the logged-in user's wallet.
    """
    if request.method == "POST":
        amount = request.POST.get("amount", "").strip()

        try:
            # Validate input
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")

            # Get or create the user's wallet
            wallet, _ = Wallet.objects.get_or_create(user=request.user)

            # Deposit the amount
            wallet.deposit(amount)
            messages.success(request, f"₹{amount:.2f} has been added to your wallet.")

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect("user-dashboard")  # Redirect to the user's dashboard

    return render(request, "dashboard/add_money.html")
