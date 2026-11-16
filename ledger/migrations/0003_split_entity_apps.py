"""Перенос моделей между приложениями с сохранением таблиц и прав доступа."""

from django.db import migrations


MODEL_APPS = {
    "user": "users",
    "category": "categories",
    "account": "accounts",
    "operation": "operations",
}


def move_content_types(apps, schema_editor, reverse=False):
    alias = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    LogEntry = apps.get_model("admin", "LogEntry")
    content_types = ContentType.objects.using(alias)
    permissions = Permission.objects.using(alias)
    for model, entity_app in MODEL_APPS.items():
        source, target = (entity_app, "ledger") if reverse else ("ledger", entity_app)
        old = content_types.filter(app_label=source, model=model).first()
        if old is None:
            continue
        duplicate = content_types.filter(app_label=target, model=model).first()
        if duplicate:
            # Возможен после частичного migrate с запуском post_migrate.
            for permission in permissions.filter(content_type_id=duplicate.pk):
                saved = permissions.filter(
                    content_type_id=old.pk, codename=permission.codename
                ).first()
                if saved is None:
                    permission.content_type_id = old.pk
                    permission.save(using=alias, update_fields=["content_type"])
                    continue
                for owner in apps.get_models():
                    for field in owner._meta.local_many_to_many:
                        if field.remote_field.model != Permission:
                            continue
                        through = field.remote_field.through
                        key = field.m2m_reverse_field_name() + "_id"
                        for row in (
                            through.objects.using(alias)
                            .filter(**{key: permission.pk})
                            .values()
                        ):
                            row.pop(through._meta.pk.attname)
                            row[key] = saved.pk
                            through.objects.using(alias).get_or_create(**row)
                permission.delete(using=alias)
            LogEntry.objects.using(alias).filter(content_type_id=duplicate.pk).update(
                content_type_id=old.pk
            )
            duplicate.delete(using=alias)
        old.app_label = target
        old.save(using=alias, update_fields=["app_label"])


def forwards(apps, schema_editor):
    move_content_types(apps, schema_editor)


def backwards(apps, schema_editor):
    move_content_types(apps, schema_editor, reverse=True)


class Migration(migrations.Migration):
    dependencies = [
        ("ledger", "0002_category_name_key"),
        ("operations", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel("Operation"),
                migrations.DeleteModel("Account"),
                migrations.DeleteModel("Category"),
                migrations.DeleteModel("User"),
            ]
        ),
        migrations.RunPython(forwards, backwards),
    ]
