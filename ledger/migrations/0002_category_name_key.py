from django.db import migrations, models


def normalize_names(apps, schema_editor):
    Category = apps.get_model("ledger", "Category")
    for category in Category.objects.all():
        category.name_key = category.name.strip().casefold()
        category.save(update_fields=["name_key"])


class Migration(migrations.Migration):
    dependencies = [("ledger", "0001_initial")]
    operations = [
        migrations.RemoveConstraint(model_name="category", name="category_name_ci"),
        migrations.AddField(
            model_name="category",
            name="name_key",
            field=models.CharField(max_length=100, null=True, editable=False),
        ),
        migrations.RunPython(normalize_names, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="category",
            name="name_key",
            field=models.CharField(
                max_length=100, blank=True, editable=False, unique=True
            ),
        ),
    ]
