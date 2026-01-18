from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('cities', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('temperature', models.FloatField()),
                ('humidity', models.IntegerField()),
                ('wind_speed', models.FloatField()),
                ('pressure', models.FloatField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weather_records', to='cities.city')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['city', '-timestamp'], name='weather_wea_city_id_b1c2d3_idx'),
        ),
    ]
