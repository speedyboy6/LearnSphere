# Generated by Django 4.2.5 on 2024-09-07 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acb', '0004_alter_register_email_alter_register_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacherreg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Firstname', models.CharField(blank=True, max_length=20, null=True)),
                ('Lastname', models.CharField(blank=True, max_length=20, null=True)),
                ('IDNumber', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('DOB', models.DateField(blank=True, null=True)),
                ('Email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('Password', models.CharField(blank=True, max_length=20, null=True)),
                ('Image', models.ImageField(blank=True, null=True, upload_to='Teacher/')),
            ],
        ),
    ]
