from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quran', '0006_surah_revelation_place'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surah',
            old_name='name_bangla',
            new_name='meaning_bangla',
        ),
        migrations.AddField(
            model_name='surah',
            name='name_bangla',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
