"""
Atom feed views for weather forecasts.
"""
from datetime import date, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring
from django.http import HttpResponse, Http404
from django.views import View
from apps.cities.models import City
from apps.forecast.models import WeatherForecast


ATOM_NAMESPACE = 'http://www.w3.org/2005/Atom'


class WeatherAtomFeedView(View):
    """
    View to generate Atom feeds for city weather forecasts.
    """

    def get(self, request, city_uuid):
        """
        Generate an Atom feed for the specified city's weather forecast.
        """
        try:
            city = City.objects.get(uuid=city_uuid)
        except City.DoesNotExist:
            raise Http404("City not found")

        # Get or generate forecast data
        today = date.today()
        end_date = today + timedelta(days=6)  # 7 days including today
        forecasts = WeatherForecast.objects.filter(
            city=city,
            forecast_date__gte=today,
            forecast_date__lte=end_date
        ).order_by('forecast_date')

        # If no forecasts exist, generate mock data
        if not forecasts.exists():
            forecasts = self._generate_mock_forecast(city, 7)

        # Build Atom feed
        feed_xml = self._build_atom_feed(city, forecasts, request)

        return HttpResponse(
            feed_xml,
            content_type='application/atom+xml; charset=utf-8'
        )

    def _generate_mock_forecast(self, city, days):
        """Generate mock forecast data for the feed."""
        today = date.today()
        forecasts = []

        conditions = [
            'Clear sky',
            'Partly cloudy',
            'Overcast',
            'Light rain',
            'Sunny',
            'Scattered clouds',
            'Moderate rain',
        ]

        for i in range(days):
            forecast_date = today + timedelta(days=i)
            forecast = WeatherForecast(
                city=city,
                forecast_date=forecast_date,
                temperature=20.0 + (i % 10) - 5,
                humidity=60.0 + (i % 20) - 10,
                wind_speed=5.0 + (i % 5),
                condition=conditions[i % len(conditions)],
            )
            forecast.save()
            forecasts.append(forecast)

        return forecasts

    def _build_atom_feed(self, city, forecasts, request):
        """
        Build the Atom XML feed document.
        """
        # Create root element with Atom namespace
        feed = Element('feed')
        feed.set('xmlns', ATOM_NAMESPACE)

        # Feed metadata
        title = SubElement(feed, 'title')
        title.text = f"Weather Forecast for {city.name}"

        # Feed ID (unique identifier for the feed)
        feed_id = SubElement(feed, 'id')
        feed_id.text = f"urn:weather-forecast:city:{city.uuid}"

        # Updated timestamp (use most recent forecast update or now)
        updated = SubElement(feed, 'updated')
        if forecasts:
            # Get the most recent updated_at from forecasts
            latest = forecasts[0]
            for f in forecasts:
                if hasattr(f, 'updated_at') and f.updated_at and (not latest.updated_at or f.updated_at > latest.updated_at):
                    latest = f
            if hasattr(latest, 'updated_at') and latest.updated_at:
                updated.text = latest.updated_at.isoformat() + 'Z'
            else:
                from datetime import datetime
                updated.text = datetime.utcnow().isoformat() + 'Z'
        else:
            from datetime import datetime
            updated.text = datetime.utcnow().isoformat() + 'Z'

        # Author
        author = SubElement(feed, 'author')
        author_name = SubElement(author, 'name')
        author_name.text = 'Weather Forecast Service'

        # Link to self
        link = SubElement(feed, 'link')
        link.set('rel', 'self')
        link.set('href', request.build_absolute_uri())

        # Add entries for each forecast
        for forecast in forecasts:
            entry = self._build_entry(forecast, city)
            feed.append(entry)

        # Return XML string with declaration
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
        return xml_declaration + tostring(feed, encoding='unicode')

    def _build_entry(self, forecast, city):
        """
        Build an Atom entry element for a forecast.
        """
        entry = Element('entry')

        # Entry title with weather summary
        title = SubElement(entry, 'title')
        title.text = f"{forecast.forecast_date}: {forecast.condition}, {forecast.temperature:.1f}C"

        # Entry ID (unique identifier)
        entry_id = SubElement(entry, 'id')
        entry_id.text = f"urn:weather-forecast:city:{city.uuid}:date:{forecast.forecast_date}"

        # Updated timestamp
        updated = SubElement(entry, 'updated')
        if hasattr(forecast, 'updated_at') and forecast.updated_at:
            updated.text = forecast.updated_at.isoformat() + 'Z'
        else:
            from datetime import datetime
            updated.text = datetime.utcnow().isoformat() + 'Z'

        # Content with temperature and other details
        content = SubElement(entry, 'content')
        content.set('type', 'html')
        content.text = f"""
        <div>
            <p><strong>Date:</strong> {forecast.forecast_date}</p>
            <p><strong>Temperature:</strong> {forecast.temperature:.1f}C</p>
            <p><strong>Humidity:</strong> {forecast.humidity:.1f}%</p>
            <p><strong>Wind Speed:</strong> {forecast.wind_speed:.1f} m/s</p>
            <p><strong>Condition:</strong> {forecast.condition}</p>
        </div>
        """

        # Summary
        summary = SubElement(entry, 'summary')
        summary.text = f"Temperature: {forecast.temperature:.1f}C, {forecast.condition}"

        return entry
