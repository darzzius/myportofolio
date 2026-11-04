import uuid

from django.db import migrations


def repair_education_uuids(apps, schema_editor):
    # SQLite's old AlterField copied integer IDs into a UUID column as text.
    # Raw SQL avoids UUID conversion errors when reading those legacy rows.
    connection = schema_editor.connection
    if connection.vendor != "sqlite":
        return

    education = apps.get_model("main", "Education")
    stars = education.starred_by.through
    quote = connection.ops.quote_name
    table = quote(education._meta.db_table)
    pk = quote(education._meta.pk.column)
    stars_table = quote(stars._meta.db_table)
    education_fk = quote(stars._meta.get_field("education").column)

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT {pk} FROM {table}")
        ids = [row[0] for row in cursor.fetchall()]
        used_ids = {str(value) for value in ids}
        for old_id in ids:
            try:
                uuid.UUID(str(old_id))
            except ValueError:
                new_id = uuid.uuid4().hex
                while new_id in used_ids:
                    new_id = uuid.uuid4().hex
                used_ids.add(new_id)
                # Django's SQLite foreign keys are deferred until commit, so
                # both sides can be updated together in this atomic migration.
                cursor.execute(
                    f"UPDATE {stars_table} SET {education_fk} = %s WHERE {education_fk} = %s",
                    [new_id, old_id],
                )
                cursor.execute(
                    f"UPDATE {table} SET {pk} = %s WHERE {pk} = %s",
                    [new_id, old_id],
                )


class Migration(migrations.Migration):
    dependencies = [("main", "0010_experience_starred_by")]

    operations = [
        # Keep repaired UUIDs if this migration is unapplied.
        migrations.RunPython(repair_education_uuids, migrations.RunPython.noop),
    ]
