from django import forms

from crispy_forms.bootstrap import Field, Accordion, AccordionGroup
from crispy_forms.helper import FormHelper


class ParametersForm(forms.Form):

    class Meta:
        abstract = True

    error_css_class = 'has-error'

    ending_t = forms.IntegerField(
        label="Duration",
        required=True,
        initial=25,
    )

    radius = forms.ChoiceField(
        widget=forms.Select,
        choices=[
            (0.25, '0.25'),
            (0.5, '0.50'),
            (0.75, '0.75'),
            (1., '1.00'),
        ],
        label="Field of view radius for consumers",
        required=True
    )

    trial = forms.BooleanField(
        label="Trial",
        initial=False,
        required=False,
    )

    form_function = forms.Field(widget=forms.HiddenInput, initial="room_organisation")


class RoomForm(ParametersForm):

    def __init__(self, *args):

        super(RoomForm, self).__init__(*args)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.group = (Field(field) for field in self.fields)

        self.helper.layout = Accordion(
            AccordionGroup('Parameters', *self.group),
        )

        self.cleaned_data = None

    def clean(self):

        """
        called by is_valid method
        when the form is going
        to be validated
        """

        self.cleaned_data = super(RoomForm, self).clean()

        cleaned_data = self.cleaned_data.copy()

        if cleaned_data.get("trial") is None:
            self.cleaned_data["trial"] = False
        else:
            cleaned_data.pop("trial")

        if not all(cleaned_data.get(field) for field in cleaned_data.keys()):

            raise forms.ValidationError(
                message="You must fill in all the required fields!",
            )

    def get_data(self):

        return self.cleaned_data
