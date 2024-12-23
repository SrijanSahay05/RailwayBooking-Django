from django import forms
from django.forms import modelformset_factory
from railways.models import Passenger, JourneySeatCategory


class BookingForm(forms.Form):
    """
    Form for booking tickets for a specific journey.
    """

    seat_category = forms.ModelChoiceField(
        queryset=JourneySeatCategory.objects.none(),
        label="Seat Category",
        empty_label="Select a seat category",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, journey_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the seat category based on the journey
        self.fields["seat_category"].queryset = JourneySeatCategory.objects.filter(
            journey_id=journey_id
        )


class PassengerForm(forms.ModelForm):
    """
    Form for adding passenger details.
    """

    class Meta:
        model = Passenger
        fields = ["name", "age", "gender"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter passenger name"}
            ),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter age"}
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Passenger Name",
            "age": "Passenger Age",
            "gender": "Gender",
        }

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and age < 0:
            raise forms.ValidationError("Age cannot be negative.")
        return age


# Define a formset for multiple passengers
PassengerFormSet = modelformset_factory(
    Passenger,
    form=PassengerForm,
    extra=1,  # Allows for adding one passenger by default
    can_delete=True,  # Option to delete rows if necessary
)
