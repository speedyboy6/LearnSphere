# Generated by Django 3.0.14 on 2024-09-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acb', '0002_register_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='RollNumber',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='register',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
