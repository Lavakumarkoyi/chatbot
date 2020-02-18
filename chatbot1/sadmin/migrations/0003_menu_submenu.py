# Generated by Django 2.2.9 on 2020-01-27 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sadmin', '0002_auto_20200127_1614'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('MenuName', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('MenuIcon', models.CharField(max_length=20)),
                ('userAccess', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SubMenuName', models.CharField(max_length=20)),
                ('Link', models.CharField(max_length=255)),
                ('Menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sadmin.Menu')),
            ],
        ),
    ]
