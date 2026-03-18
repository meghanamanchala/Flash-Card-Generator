from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunit',
            name='max_flashcards',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
