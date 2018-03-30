# Generated by Django 2.0.1 on 2018-02-15 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_auto_20180215_0536'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': [['permission_test', 'Hello permissions'], ['can_access_my_course', 'Allowed to access course'], ['can_access_customer_list', 'Allowed to access customer list'], ['can_access_customer_detail', 'Allowed to access customer detailed info'], ['can_access_studyrecords', 'Allowed to access study records'], ['can_access_homework_detail', 'Allowed to access homework detail'], ['can_upload_homework', 'Allowed to upload homework']]},
        ),
    ]