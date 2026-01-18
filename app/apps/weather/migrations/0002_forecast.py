from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('temperature', models.FloatField()),
                ('humidity', models.IntegerField()),
                ('wind_speed', models.FloatField()),
                ('pressure', models.FloatField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('forecast_date', models.DateTimeField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forecasts', to='cities.city')),
            ],
            options={
                'ordering': ['forecast_date'],
            },
        ),
        migrations.AddIndex(
            model_name='forecast',
            index=models.Index(fields=['city', 'forecast_date'], name='weather_for_city_id_a1b2c3_idx'),
        ),
    ]
