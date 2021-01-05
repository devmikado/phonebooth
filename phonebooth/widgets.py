from django import forms
from django.conf import settings
from django.forms import Textarea, TextInput
from django_filters import widgets
# from django_prices.widgets import MoneyInput

from django.forms import Select, TextInput
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

phone_prefixes = [
    ('+{}'.format(k), '+{}'.format(k)) for
    (k, v) in sorted(COUNTRY_CODE_TO_REGION_CODE.items())]


class PhonePrefixWidget(PhoneNumberPrefixWidget):
    """Uses choices with tuple in a simple form of "+XYZ: +XYZ".

    Workaround for an issue:
    https://github.com/stefanfoulis/django-phonenumber-field/issues/82
    """

    template_name = 'account/snippets/phone_prefix_widget.html'

    def __init__(self, attrs=None):
        widgets = (Select(attrs=attrs, choices=phone_prefixes), TextInput())
        # pylint: disable=bad-super-call
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)



class DateRangeWidget(widgets.DateRangeWidget):
    def __init__(self, attrs=None):
        date_widgets = (forms.DateInput, forms.DateInput)
        # pylint: disable=bad-super-call
        super(widgets.RangeWidget, self).__init__(date_widgets, attrs)


class MoneyRangeWidget(widgets.RangeWidget):
    def __init__(self, attrs=None):
        self.currency = getattr(settings, 'DEFAULT_CURRENCY')
        money_widgets = (MoneyInput(self.currency), MoneyInput(self.currency))
        # pylint: disable=bad-super-call
        super(widgets.RangeWidget, self).__init__(money_widgets, attrs)


class PhonePrefixWidget(PhonePrefixWidget):
    template_name = 'dashboard/order/widget/phone_prefix_widget.html'


class RichTextEditorWidget(Textarea):
    """A WYSIWYG editor widget using medium-editor."""

    def __init__(self, attrs=None):
        default_attrs = {'class': 'rich-text-editor'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class CharsLeftWidget(TextInput):
    """Displays number of characters left on the right side of the label,
    requires different rendering on the frontend.
    """
    pass
