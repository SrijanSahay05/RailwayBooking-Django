from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from datetime import date, timedelta

from .models import (
    Day,
    Date,
    Train,
    Journey,
    JourneySeatCategory,
    TrainSeatCategory,
)


@receiver(post_save, sender=Day)
def create_upcoming_dates(sender, instance, created, **kwargs):
    """
    Create upcoming Date objects for the given Day.
    """
    if created:
        print(f"[Signal] Creating upcoming dates for {instance.name}")

    today = date.today()
    for day_offset in range(90):
        target_date = today + timedelta(days=day_offset)
        if target_date.strftime("%A") == instance.name:
            Date.objects.get_or_create(day=instance, date=target_date)
            print(f"[Signal] Created Date object for {target_date}")


@receiver(post_save, sender=Train)
def create_journeys_for_train(sender, instance, created, **kwargs):
    """
    Automatically create Journey instances for a Train when it is created.
    """
    if created:
        print(f"[Signal] Creating journeys for train: {instance.name}")
        handle_journey_creation(instance)


@receiver(m2m_changed, sender=Train.running_days.through)
def handle_running_days_change(sender, instance, action, **kwargs):
    """
    Handle changes to the running_days ManyToManyField of a Train.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        print(f"[Signal] Running days changed for Train: {instance.name}")
        handle_journey_creation(instance)


@receiver(post_save, sender=Journey)
def create_journey_seat_categories(sender, instance, created, **kwargs):
    """
    Automatically create JourneySeatCategory instances for a Journey when it is created.
    """
    if created:
        print(f"[Signal] Creating seat categories for Journey: {instance}")
        link_seat_categories_to_journey(instance)


def handle_journey_creation(train_instance):
    """
    Create Journey instances for a Train based on its running days and future dates.
    """
    print(f"[Signal] Handling journey creation for Train: {train_instance.name}")

    # Get the train's running days
    running_days = train_instance.running_days.all()

    # Fetch all future dates corresponding to the train's running days
    today = date.today()
    future_dates = Date.objects.filter(day__in=running_days, date__gte=today)

    # Create journeys for each future date
    journeys_to_create = []
    for journey_date in future_dates:
        journey = Journey(
            train=train_instance,
            departure_date=journey_date,
            total_seats=sum(
                TrainSeatCategory.objects.filter(train=train_instance).values_list(
                    "total_seats", flat=True
                )
            ),
            available_seats=sum(
                TrainSeatCategory.objects.filter(train=train_instance).values_list(
                    "available_seats", flat=True
                )
            ),
        )
        journeys_to_create.append(journey)

    # Bulk create journeys
    created_journeys = Journey.objects.bulk_create(journeys_to_create)
    print(
        f"[Signal] Created {len(created_journeys)} Journey objects for {train_instance.name}"
    )

    # Update arrival dates and link seat categories
    for journey in created_journeys:
        update_arrival_date_for_journey(journey, train_instance.travel_days)
        link_seat_categories_to_journey(journey)


def update_arrival_date_for_journey(journey, travel_days):
    """
    Update the arrival_date for the given Journey based on travel_days.
    """
    if travel_days == 0:
        journey.arrival_date = journey.departure_date
    else:
        arrival_date_value = journey.departure_date.date + timedelta(days=travel_days)
        arrival_day_instance, _ = Day.objects.get_or_create(
            name=arrival_date_value.strftime("%A")
        )
        arrival_date, _ = Date.objects.get_or_create(
            day=arrival_day_instance, date=arrival_date_value
        )
        journey.arrival_date = arrival_date

    journey.save()
    print(
        f"[Signal] Updated Journey arrival date to {journey.arrival_date.date.strftime('%d-%m-%Y')}"
    )


def link_seat_categories_to_journey(journey_instance):
    """
    Link seat categories from TrainSeatCategory to JourneySeatCategory for the given Journey.
    """
    train = journey_instance.train
    train_seat_categories = TrainSeatCategory.objects.filter(train=train)

    # Prepare JourneySeatCategory objects
    journey_seat_categories = [
        JourneySeatCategory(
            journey=journey_instance,
            seat_category=train_seat_category.seat_category,
            total_seats=train_seat_category.total_seats,
            available_seats=train_seat_category.available_seats,
            base_price=train_seat_category.base_price,
        )
        for train_seat_category in train_seat_categories
    ]

    # Bulk create JourneySeatCategory objects
    JourneySeatCategory.objects.bulk_create(journey_seat_categories)
    print(f"[Signal] Linked seat categories for Journey: {journey_instance}")
