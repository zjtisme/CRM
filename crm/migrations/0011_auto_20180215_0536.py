# Generated by Django 2.0.1 on 2018-02-15 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_auto_20180215_0247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': [['permission_test', 'Hello permissions'], ['can_access_my_course', 'Allowed to access course'], ['can_access_customer_list', 'Allowed to access customer list'], ['can_access_customer_detail', 'Allowed to access customer detailed info']]},
        ),
    ]
