# Generated by Django 3.0.7 on 2020-09-25 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_auto_20200925_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='age',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(default='Nothing', max_length=15),
        ),
    ]