from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='school',
            old_name='icon',
            new_name='poster',
        ),
        migrations.AlterField(
            model_name='school',
            name='poster',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='school_posters/',
                help_text="Displayed at the top of the school's card and in the hero "
                "section of the school's page. A portrait image (roughly 3:4, e.g. "
                "900\u00d71200px) works best \u2014 it gets cropped to fit both spots.",
            ),
        ),
    ]
