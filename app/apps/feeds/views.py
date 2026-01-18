from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.utils.feedgenerator import Atom1Feed
from django.utils import timezone
from apps.weather.models import Forecast
from apps.cities.models import City


class AtomFeedView(View):
    """
    Generates an Atom 1.0 feed for weather forecasts.
    """

    def get(self, request):
        """
        Generate and return Atom feed for all weather forecasts.
        """
        # Create Atom feed
        feed = Atom1Feed(
            title='Weather Forecast Feed',
            link='/',
            description='Real-time weather forecast data for multiple cities',
            language='en'
        )

        # Get all latest forecasts grouped by city
        cities = City.objects.all()

        for city in cities:
            # Get the latest 7 forecasts for each city
            forecasts = Forecast.objects.filter(city=city).order_by('forecast_date')[:7]

            for forecast in forecasts:
                # Create feed entry for each forecast
                feed.add_item(
                    title=f'{city.name} - {forecast.forecast_date.strftime("%Y-%m-%d")}',
                    link=f'/cities/{city.uuid}/forecast/',
                    description=self._format_forecast_description(forecast),
                    author_name='Weather Service',
                    pubdate=forecast.updated_at,
                    updateddate=forecast.updated_at,
                    unique_id=f'forecast-{forecast.uuid}',
                    categories=[city.name, 'weather', 'forecast']
                )

        # Return as HTTP response with Atom content type
        return HttpResponse(feed.writeString('utf-8'), content_type='application/atom+xml; charset=utf-8')

    def _format_forecast_description(self, forecast):
        """
        Format forecast data as HTML content for feed entry.
        """
        city = forecast.city
        html_content = f"""
        <html xmlns="http://www.w3.org/1999/xhtml">
            <body>
                <h3>{city.name}, {city.country}</h3>
                <p><strong>Forecast Date:</strong> {forecast.forecast_date.strftime('%Y-%m-%d')}</p>
                <dl>
                    <dt>Temperature</dt>
                    <dd>{forecast.temperature}°C</dd>
                    <dt>Humidity</dt>
                    <dd>{forecast.humidity}%</dd>
                    <dt>Wind Speed</dt>
                    <dd>{forecast.wind_speed} m/s</dd>
                    <dt>Pressure</dt>
                    <dd>{forecast.pressure} hPa</dd>
                    <dt>Description</dt>
                    <dd>{forecast.description or 'N/A'}</dd>
                </dl>
            </body>
        </html>
        """
        return html_content
