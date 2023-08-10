from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sports", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="teams",
            field=models.ManyToManyField(blank=True, to="sports.team"),
        ),
    ]
