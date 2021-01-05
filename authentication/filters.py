from django.utils.translation import npgettext, pgettext_lazy
from django_filters import CharFilter, ChoiceFilter, OrderingFilter, BooleanFilter
from django import forms

from django_filters import FilterSet

from b2b.models import *

SORT_BY_FIELDS = {
    'positive_response_text': pgettext_lazy('Category list sorting option', 'positive_response_text'),
    'negative_response_text': pgettext_lazy('Category list sorting option', 'negative_response_text'),
    'neutral_response_text': pgettext_lazy('Category list sorting option', 'neutral_response_text'),
}
    

class SortedFilterSet(FilterSet):
    """Base class for filter sets used in dashboard views.

    Adds flag `is_bound_unsorted` to indicate if filter set has data from
    filters other than `sort_by` or `page`.
    """

    def __init__(self, data, *args, **kwargs):
        self.is_bound_unsorted = self.set_is_bound_unsorted(data)
        super(SortedFilterSet, self).__init__(data, *args, **kwargs)

    def set_is_bound_unsorted(self, data):
        return any([key not in {'sort_by', 'page'} for key in data.keys()])

    def get_summary_message(self):
        """Return message displayed in dashboard filter cards.

        Inherited by subclasses for record specific naming.
        """
        counter = self.qs.count()
        return npgettext(
            'Number of matching records in the dashboard list',
            'Found %(counter)d matching record',
            'Found %(counter)d matching records',
            number=counter) % {'counter': counter}


class CannnedFilter(SortedFilterSet):
    positive_response_text = CharFilter(
        label=pgettext_lazy('Category list filter label', 'Positive Response'),
        lookup_expr='icontains')

    negative_response_text = CharFilter(
        label=pgettext_lazy('Category list filter label', 'Negative Response'),
        lookup_expr='icontains')

    neutral_response_text = CharFilter(
        label=pgettext_lazy('Category list filter label', 'Neutral Response'),
        lookup_expr='icontains')

    sort_by = OrderingFilter(
        label=pgettext_lazy('Category list sorting filter label', 'Sort by'),
        fields=SORT_BY_FIELDS.keys(),
        field_labels=SORT_BY_FIELDS)

   
    class Meta:
        model = canned_response_management
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            'Number of matching records in the responses list',
            'Found %(counter)d matching response',
            'Found %(counter)d matching responses',
            number=counter) % {'counter': counter}

    def filter_by_subcatogories(self, queryset, name, value):
        return queryset