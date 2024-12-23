from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Journey, TrainSeatCategory, JourneySeatCategory


def populate_journey_seat_category(request):
    """
    Populate JourneySeatCategory model for all Journey instances.
    """
    journeys = Journey.objects.all()
    created_count = 0
    error_count = 0
    errors = []

    for journey in journeys:
        train = journey.train
        train_seat_categories = TrainSeatCategory.objects.filter(train=train)

        if not train_seat_categories.exists():
            errors.append(f"No TrainSeatCategory found for train: {train.name}")
            error_count += 1
            continue

        for train_seat_category in train_seat_categories:
            journey_seat_category, created = JourneySeatCategory.objects.get_or_create(
                journey=journey,
                seat_category=train_seat_category.seat_category,
                defaults={
                    "total_seats": train_seat_category.total_seats,
                    "available_seats": train_seat_category.available_seats,
                    "base_price": train_seat_category.base_price,
                },
            )
            if created:
                created_count += 1

    response = {
        "status": "success",
        "message": f"Populated JourneySeatCategory for all journeys.",
        "created_count": created_count,
        "error_count": error_count,
        "errors": errors,
    }
    # return JsonResponse(response)
    return redirect("search-trains")
