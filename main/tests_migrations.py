import uuid
from unittest import skipUnless

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


@skipUnless(connection.vendor == "sqlite", "Legacy integer UUIDs occur on SQLite.")
class EducationUUIDMigrationTest(TransactionTestCase):
    def test_repairs_legacy_ids_and_preserves_stars_and_valid_ids(self):
        before = [("main", "0010_experience_starred_by")]
        after = [("main", "0011_repair_education_uuids")]
        executor = MigrationExecutor(connection)
        executor.migrate(before)
        try:
            apps = executor.loader.project_state(before).apps
            Education = apps.get_model("main", "Education")
            User = apps.get_model("auth", "User")
            user = User.objects.create(username="migration-user", password="!")
            valid = Education.objects.create(
                institution="Valid UUID", degree="S1", start_year="2025",
                end_year="Present", description="Must stay unchanged.",
            )
            valid.starred_by.add(user)
            # Reproduce the raw integer-text ID left by migration 0007.
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO main_education "
                    "(id, institution, degree, start_year, end_year, description) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    ["42", "Legacy ID", "S1", "2020", "2024", "Keep this data."],
                )
                cursor.execute(
                    "INSERT INTO main_education_starred_by (education_id, user_id) VALUES (%s, %s)",
                    ["42", user.pk],
                )

            executor = MigrationExecutor(connection)
            executor.migrate(after)
            Education = executor.loader.project_state(after).apps.get_model("main", "Education")
            repaired = Education.objects.get(institution="Legacy ID")
            self.assertIsInstance(repaired.pk, uuid.UUID)
            self.assertEqual(repaired.description, "Keep this data.")
            self.assertEqual(list(repaired.starred_by.values_list("pk", flat=True)), [user.pk])
            unchanged = Education.objects.get(pk=valid.pk)
            self.assertEqual(list(unchanged.starred_by.values_list("pk", flat=True)), [user.pk])
            # This also verifies that rows seeded by migrations 0003-0005 load.
            self.assertTrue(all(isinstance(item.pk, uuid.UUID) for item in Education.objects.all()))
            connection.check_constraints()
        finally:
            MigrationExecutor(connection).migrate(after)
