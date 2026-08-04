from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="createAt",
            field=models.DateField(
                auto_now_add=True,
                default=timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="loginAt",
            field=models.DateField(
                auto_now=True,
                default=timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(
                max_length=10,
                default=""
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="profile",
            field=models.ImageField(
                upload_to="profile/",
                blank=True,
                null=True
            ),
        ),
    ]