from django.contrib import admin
from .models import (
    Station,
    Day,
    Date,
    SeatCategory,
    Train,
    TrainSeatCategory,
    HaltStation,
    Journey,
    JourneySeatCategory,
    Ticket,
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_per_page = 20


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation")
    search_fields = ("name", "abbreviation")


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    list_display = ("date", "day")
    list_filter = ("day",)
    search_fields = ("date",)
    ordering = ("date",)


@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


class TrainSeatCategoryInline(admin.TabularInline):
    model = TrainSeatCategory
    extra = 1


class HaltStationInline(admin.TabularInline):
    model = HaltStation
    extra = 1


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "number",
        "departure_station",
        "arrival_station",
        "travel_days",
    )
    search_fields = ("name", "number")
    list_filter = ("departure_station", "arrival_station", "running_days")
    inlines = [TrainSeatCategoryInline, HaltStationInline]


@admin.register(TrainSeatCategory)
class TrainSeatCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "train",
        "seat_category",
        "total_seats",
        "available_seats",
        "base_price",
    )
    search_fields = ("train__name", "seat_category__name")
    list_filter = ("train", "seat_category")


@admin.register(HaltStation)
class HaltStationAdmin(admin.ModelAdmin):
    list_display = (
        "train",
        "station",
        "arrival_time",
        "departure_time",
        "order",
        "is_datechanging",
    )
    list_filter = ("train", "station", "is_datechanging")
    search_fields = ("train__name", "station__name")
    ordering = ("train", "order")


class JourneySeatCategoryInline(admin.TabularInline):
    model = JourneySeatCategory
    extra = 1


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "train",
        "departure_date",
        "arrival_date",
        "booked_seats",
        "available_seats",
    )
    list_filter = ("train", "departure_date")
    search_fields = ("train__name", "departure_date__date")
    inlines = [JourneySeatCategoryInline]


@admin.register(JourneySeatCategory)
class JourneySeatCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "journey",
        "seat_category",
        "total_seats",
        "available_seats",
        "base_price",
    )
    search_fields = ("journey__train__name", "seat_category__name")
    list_filter = ("journey", "seat_category")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "journey",
        "journey_seat_category",
        "num_seats",
        "price",
        "booking_date",
    )
    search_fields = (
        "journey__train__name",
        "journey_seat_category__seat_category__name",
    )
    list_filter = ("journey", "journey_seat_category", "booking_date")
    date_hierarchy = "booking_date"
    ordering = ("-booking_date",)
