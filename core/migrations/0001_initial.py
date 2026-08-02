from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('role', models.CharField(blank=True, help_text='Job title or role, e.g. "Executive Director".', max_length=150)),
                ('bio', models.TextField(blank=True)),
                ('photo', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='team_photos/',
                    help_text="Shown on the Our Team page. A square photo (roughly 600\u00d7600px) "
                    "works best \u2014 it gets cropped to fit. Until a photo is uploaded, this "
                    "person's initials are shown instead.",
                )),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('linkedin_url', models.URLField(blank=True, verbose_name='LinkedIn URL')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Uncheck to hide this person from the public Our Team page without deleting their record.',
                )),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
    ]
