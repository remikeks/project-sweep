from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


def populate_snapshot_fields(apps, schema_editor):
    for Model, relation, suffix in ((apps.get_model("credentials", "Badge"), "course", "completion badge"), (apps.get_model("credentials", "Certificate"), "school", "certificate of completion")):
        for item in Model.objects.select_related("user", relation).all().iterator():
            name = item.user.get_full_name().strip() or item.user.get_username()
            item.issued_to_name = name
            item.credential_title = f"{getattr(item, relation).title if relation == 'course' else getattr(item, relation).name} {suffix}"
            item.issuer_name = "SWEEP"
            item.save(update_fields=["issued_to_name", "credential_title", "issuer_name"])


class Migration(migrations.Migration):
    dependencies = [("credentials", "0001_initial")]
    operations = [
        migrations.AddField(model_name="badge", name="issued_to_name", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="badge", name="credential_title", field=models.CharField(blank=True, max_length=250)),
        migrations.AddField(model_name="badge", name="issuer_name", field=models.CharField(default="SWEEP", max_length=120)),
        migrations.AddField(model_name="badge", name="status", field=models.CharField(choices=[("active", "Active"), ("revoked", "Revoked"), ("superseded", "Superseded")], default="active", max_length=20)),
        migrations.AddField(model_name="badge", name="revoked_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="badge", name="revocation_reason", field=models.TextField(blank=True)),
        migrations.AddField(model_name="badge", name="replaced_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="replaces", to="credentials.badge")),
        migrations.AddField(model_name="certificate", name="issued_to_name", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="certificate", name="credential_title", field=models.CharField(blank=True, max_length=250)),
        migrations.AddField(model_name="certificate", name="issuer_name", field=models.CharField(default="SWEEP", max_length=120)),
        migrations.AddField(model_name="certificate", name="status", field=models.CharField(choices=[("active", "Active"), ("revoked", "Revoked"), ("superseded", "Superseded")], default="active", max_length=20)),
        migrations.AddField(model_name="certificate", name="revoked_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="certificate", name="revocation_reason", field=models.TextField(blank=True)),
        migrations.AddField(model_name="certificate", name="replaced_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="replaces", to="credentials.certificate")),
        migrations.RunPython(populate_snapshot_fields, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(name="badge", unique_together=set()),
        migrations.AlterUniqueTogether(name="certificate", unique_together=set()),
        migrations.AddConstraint(model_name="badge", constraint=models.UniqueConstraint(condition=Q(("status", "active")), fields=("user", "course"), name="unique_active_badge")),
        migrations.AddConstraint(model_name="certificate", constraint=models.UniqueConstraint(condition=Q(("status", "active")), fields=("user", "school"), name="unique_active_certificate")),
    ]
