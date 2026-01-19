from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255)),
                ('timezone', models.CharField(max_length=63)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddIndex(
            model_name='city',
            index=models.Index(fields=['name'], name='cities_city_name_idx'),
        ),
    ]
