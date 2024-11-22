from django.urls import path
from . import views as dashboard_views
import railways.views as railway_views
import users.views as users_views
import transactions.views as transactions_views

import dashboard

urlpatterns = [
    path("", dashboard_views.index, name="index"),
    path("my-tickets/", dashboard_views.my_tickets, name="my-tickets"),
    path(
        "ticket-detail/<int:ticket_id>/",
        dashboard_views.ticket_detail,
        name="ticket-detail",
    ),
    path("dashboard/", dashboard_views.user_dashboard, name="user-dashboard"),
    path("login/", users_views.login_view, name="login"),
    path("register/", users_views.register_view, name="register"),
    path("logout/", users_views.logout_view, name="logout"),
    path(
        "journey-seats/",
        railway_views.populate_journey_seat_category,
        name="refresh-trains",
    ),
    path("search-trains/", dashboard_views.search_trains, name="search-trains"),
    path(
        "book-ticket/<int:journey_id>/", dashboard_views.book_ticket, name="book-ticket"
    ),
    path("add-money/", transactions_views.add_money, name="add-money"),
    path(
        "cancel/<int:ticket_id>/", dashboard_views.cancel_ticket, name="cancel-ticket"
    ),
]
