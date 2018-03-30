# Generated by Django 2.0.3 on 2018-03-17 19:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180317_1811'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackAcademics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute1', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute2', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute3', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute4', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute5', models.TextField(validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('attribute6', models.TextField(validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Student')),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackInfrastructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute1', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute2', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute3', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute4', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('attribute5', models.TextField(validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('attribute6', models.TextField(validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Student')),
            ],
        ),
    ]
