from django.db import models
from datetime import datetime, timedelta


class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Day(models.Model):
    name = models.CharField(max_length=10)
    abbreviation = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class Date(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return self.date.strftime("%d-%m-%Y")  # Format date as dd-mm-yyyy


class SeatCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class TrainSeatCategory(models.Model):
    train = models.ForeignKey("Train", on_delete=models.CASCADE)
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.train.name} - {self.seat_category.name}"


class HaltStation(models.Model):
    train = models.ForeignKey("Train", on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    is_datechanging = models.BooleanField(default=False)
    order = models.IntegerField()

    class Meta:
        unique_together = ["station", "order", "train"]

    def check_date_change(self):
        if self.departure_time < self.arrival_time:
            self.is_datechanging = True
        else:
            self.is_datechanging = False
        self.save()
        return self.is_datechanging

    def __str__(self):
        return f"{self.station.name} (Order: {self.order})"


class Train(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(unique=True)
    departure_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="departure_trains"
    )
    arrival_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="arrival_trains"
    )
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    travel_days = models.IntegerField(default=0)
    running_days = models.ManyToManyField(Day)
    halts = models.ManyToManyField(Station, related_name="halts", through="HaltStation")
    seat_categories = models.ManyToManyField(SeatCategory, through="TrainSeatCategory")

    def calculate_journey_duration(self):
        """Calculate and return the journey duration."""
        departure_datetime = datetime.combine(datetime.today(), self.departure_time)
        arrival_datetime = datetime.combine(datetime.today(), self.arrival_time)

        if arrival_datetime < departure_datetime:
            arrival_datetime += timedelta(days=1)

        journey_duration = arrival_datetime - departure_datetime
        return journey_duration + timedelta(days=self.travel_days)

    def __str__(self):
        return f"{self.name} ({self.number})"


class Journey(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_date = models.ForeignKey(
        Date, on_delete=models.CASCADE, related_name="departure_journeys", null=True
    )
    arrival_date = models.ForeignKey(
        Date,
        on_delete=models.CASCADE,
        related_name="arrival_journeys",
        null=True,
        blank=True,
    )
    booked_seats = models.IntegerField(default=0)
    total_seats = models.IntegerField(default=0)
    journey_seat_categories = models.ManyToManyField(
        "JourneySeatCategory", related_name="journeys"
    )
    available_seats = models.IntegerField(default=0)

    def calculate_arrival_date(self):
        """
        Calculate and set the arrival date based on the train's travel_days.
        """
        if self.train.travel_days == 0:
            self.arrival_date = self.departure_date
        else:
            arrival_date_value = self.departure_date.date + timedelta(
                days=self.train.travel_days
            )
            day_of_week = arrival_date_value.strftime("%A")
            arrival_day = Day.objects.get(name=day_of_week)
            arrival_date, _ = Date.objects.get_or_create(
                day=arrival_day, date=arrival_date_value
            )
            self.arrival_date = arrival_date

        self.save()
        return self.arrival_date

    def __str__(self):
        return f"{self.train.name} - {self.departure_date.date.strftime('%d-%m-%Y')}"


class JourneySeatCategory(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def book_seats(self, seats):
        """Book seats for the journey."""
        if self.available_seats < seats:
            raise ValueError("Not enough available seats")
        self.available_seats -= seats
        self.save()

    def cancel_seats(self, seats):
        """Cancel seats for the journey."""
        self.available_seats += seats
        if self.available_seats > self.total_seats:
            raise ValueError("Available seats cannot exceed total seats")
        self.save()

    def __str__(self):
        return f"{self.journey.train.name} - {self.seat_category.name}"


class Passenger(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    is_child = models.BooleanField(default=False)
    is_senior = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    booking_user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, null=True, default=None
    )
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    journey_seat_category = models.ForeignKey(
        JourneySeatCategory, on_delete=models.CASCADE
    )
    passengers = models.ManyToManyField(Passenger)
    num_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.journey.train.name} - {self.booking_date.strftime('%d-%m-%Y %H:%M:%S')}"
