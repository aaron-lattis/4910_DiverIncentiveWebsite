# Generated by Django 3.1.2 on 2021-02-23 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_sponsorcompany_company_about_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinformation',
            name='points',
            field=models.IntegerField(default=0, null=True, verbose_name='Points'),
        ),
    ]
