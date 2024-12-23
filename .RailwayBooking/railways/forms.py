from django import forms
from django.forms import formset_factory
from railways.models import Passenger, JourneySeatCategory


class BookingForm(forms.Form):
    seat_category = forms.ModelChoiceField(
        queryset=JourneySeatCategory.objects.none(),
        label="Seat Category",
        empty_label="Select Seat Category",
    )
    num_seats = forms.IntegerField(label="Number of Seats", min_value=1)

    def __init__(self, journey_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["seat_category"].queryset = JourneySeatCategory.objects.filter(
            journey_id=journey_id
        )


class PassengerForm(forms.Form):
    name = forms.CharField(label="Passenger Name")
    age = forms.IntegerField(label="Passenger Age", min_value=1)
    gender = forms.ChoiceField(
        label="Passenger Gender", choices=Passenger.GENDER_CHOICES
    )


PassengerFormSet = formset_factory(
    PassengerForm, extra=1
)  # Allow adding multiple passengers
