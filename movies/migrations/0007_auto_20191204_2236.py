# Generated by Django 2.2.7 on 2019-12-04 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_auto_20191204_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='classification',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='movies.Classification'),
        ),
    ]
