from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0004_flashcard_answer_flashcard_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunit',
            name='last_studied_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
