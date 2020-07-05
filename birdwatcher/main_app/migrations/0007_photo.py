# Generated by Django 3.0.7 on 2020-07-05 02:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_auto_20200704_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('bird', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.Bird')),
            ],
        ),
    ]
