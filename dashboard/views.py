from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from railways.models import (
    Journey,
    Passenger,
    Ticket,
    JourneySeatCategory,
    Train,
    Station,
)
from .forms import BookingForm, PassengerFormSet
from transactions.models import Wallet, Transaction


def index(request):
    """
    Home page view.
    """
    return render(request, "dashboard/index.html")


def search_trains(request):
    """
    Search for available trains based on user input.
    """
    from_station = request.GET.get("from_station", "").strip()
    to_station = request.GET.get("to_station", "").strip()
    departure_date = request.GET.get("departure_date", "").strip()

    # Initialize queryset
    journeys = Journey.objects.all()

    # Filter based on from_station
    if from_station:
        journeys = journeys.filter(
            train__departure_station__name__icontains=from_station
        )

    # Filter based on to_station
    if to_station:
        journeys = journeys.filter(train__arrival_station__name__icontains=to_station)

    # Filter based on departure_date
    if departure_date:
        try:
            parsed_departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            journeys = journeys.filter(departure_date__date=parsed_departure_date)
        except ValueError:
            journeys = journeys.none()  # Invalid date format returns no results

    # Further filter journeys for only future departures
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    journeys = journeys.filter(
        Q(departure_date__date__gt=current_date)
        | Q(departure_date__date=current_date, train__departure_time__gt=current_time)
    )

    # Order journeys by departure date and time
    journeys = journeys.order_by("departure_date__date", "train__departure_time")

    # Prepare seat categories for each journey
    journeys_with_seat_categories = [
        {
            "journey": journey,
            "seat_categories": JourneySeatCategory.objects.filter(journey=journey),
        }
        for journey in journeys
    ]

    # Check for errors
    error = None
    if not journeys_with_seat_categories and (
        from_station or to_station or departure_date
    ):
        error = "No journeys match your search criteria."

    return render(
        request,
        "dashboard/search_trains.html",
        {
            "journeys_with_seat_categories": journeys_with_seat_categories,
            "from_station": from_station,
            "to_station": to_station,
            "departure_date": departure_date,
            "error": error,
        },
    )


@login_required
@transaction.atomic
def book_ticket(request, journey_id):
    """
    View to handle ticket booking for a specific journey. Requires user login.
    """
    journey = get_object_or_404(Journey, id=journey_id)
    seat_categories = JourneySeatCategory.objects.filter(journey=journey)

    if request.method == "POST":
        booking_form = BookingForm(journey_id, request.POST)
        passenger_formset = PassengerFormSet(
            request.POST, queryset=Passenger.objects.none()
        )

        if booking_form.is_valid() and passenger_formset.is_valid():
            seat_category = booking_form.cleaned_data["seat_category"]
            num_seats = len(
                [form for form in passenger_formset.forms if form.cleaned_data]
            )

            total_price = num_seats * seat_category.base_price
            wallet = Wallet.objects.get(user=request.user)

            if wallet.balance < total_price:
                messages.error(request, "Insufficient wallet balance for booking!")
                return redirect("refresh-trains")

            try:
                # Deduct seats dynamically
                seat_category.book_seats(num_seats)

                # Deduct wallet balance
                wallet.withdraw(total_price)
                ticket = Ticket.objects.create(
                    booking_user=request.user,
                    journey=journey,
                    journey_seat_category=seat_category,
                    num_seats=num_seats,
                    price=total_price,
                )
                for form in passenger_formset.forms:
                    if form.cleaned_data:
                        passenger = Passenger.objects.create(
                            name=form.cleaned_data["name"],
                            age=form.cleaned_data["age"],
                            gender=form.cleaned_data["gender"],
                        )
                        ticket.passengers.add(passenger)

                messages.success(request, "Booking successful!")
                return redirect("my-tickets")

            except ValueError as e:
                messages.error(request, str(e))
                return redirect("search-trains")

    else:
        booking_form = BookingForm(journey_id)
        passenger_formset = PassengerFormSet(queryset=Passenger.objects.none())

    return render(
        request,
        "dashboard/book_ticket.html",
        {
            "booking_form": booking_form,
            "passenger_formset": passenger_formset,
            "journey": journey,
            "seat_categories": seat_categories,
        },
    )


@login_required
@transaction.atomic
def cancel_ticket(request, ticket_id):
    """
    View to cancel a ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, booking_user=request.user)
    journey = ticket.journey
    departure_time = datetime.combine(
        journey.departure_date.date, journey.train.departure_time
    )
    current_time = datetime.now()

    if departure_time - current_time < timedelta(hours=1):
        messages.error(
            request, "Tickets cannot be canceled within 1 hour of departure."
        )
        return redirect("my-tickets")

    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet.deposit(ticket.price)

        ticket.journey_seat_category.cancel_seats(ticket.num_seats)

        ticket.delete()

        messages.success(request, "Ticket canceled successfully. Refund initiated.")
        return redirect("my-tickets")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("my-tickets")


@login_required
def my_tickets(request):
    """
    View to display the tickets booked by the logged-in user.
    """
    tickets = Ticket.objects.filter(booking_user=request.user).select_related(
        "journey", "journey__train", "journey_seat_category"
    )

    for ticket in tickets:
        departure_datetime = datetime.combine(
            ticket.journey.departure_date.date, ticket.journey.train.departure_time
        )
        ticket.can_cancel = departure_datetime - datetime.now() > timedelta(hours=1)

    return render(request, "dashboard/my_tickets.html", {"tickets": tickets})


@login_required
def ticket_detail(request, ticket_id):
    """
    View to display detailed information about a specific ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, booking_user=request.user)

    return render(
        request,
        "dashboard/ticket_detail.html",
        {"ticket": ticket},
    )


@login_required
def user_dashboard(request):
    """
    Dashboard view to show wallet balance, upcoming bookings, and transaction history.
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet_balance = wallet.balance

    # Get the logged-in user's tickets
    upcoming_tickets = (
        Ticket.objects.filter(
            booking_user=request.user,
            journey__departure_date__date__gte=datetime.now().date(),
        )
        .select_related("journey", "journey__train", "journey_seat_category")
        .order_by("journey__departure_date__date")
    )

    # Get the logged-in user's transactions
    transactions = Transaction.objects.filter(
        Q(sender_wallet=wallet) | Q(receiver_wallet=wallet)
    ).order_by("-created_at")

    return render(
        request,
        "dashboard/user_dashboard.html",
        {
            "wallet_balance": wallet_balance,
            "upcoming_tickets": upcoming_tickets,
            "transactions": transactions,
        },
    )
