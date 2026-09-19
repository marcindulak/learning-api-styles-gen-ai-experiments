from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed

from .models import City, Forecast


class ForecastAtomFeed(Feed):
    feed_type = Atom1Feed

    # Feed.__call__ already converts any ObjectDoesNotExist raised here
    # (City.DoesNotExist is one) into a 404 response, so no explicit
    # try/except is needed.
    def get_object(self, request, city_uuid):
        return City.objects.get(uuid=city_uuid)

    def title(self, city):
        return f"{city.name} 7-day forecast"

    def link(self, city):
        return reverse("city-forecast-feed", kwargs={"city_uuid": city.uuid})

    def items(self, city):
        # select_related avoids an extra City query per item in item_link below.
        return Forecast.objects.filter(city=city).select_related("city")

    def item_title(self, item):
        return str(item.date)

    def item_description(self, item):
        return f"{item.condition}, {item.temp_min}–{item.temp_max}°C"

    def item_link(self, item):
        return f"{self.link(item.city)}#{item.date}"
