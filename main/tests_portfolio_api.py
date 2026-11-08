import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience


class PortfolioAPIChecks:
    """Run the same access and CSRF contract against both assignment resources."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(
            username="portfolio-owner", email="owner@example.com", password="portfolio-test-password",
        )
        cls.visitor = User.objects.create_user(
            username="portfolio-visitor", email="visitor@example.com", password="portfolio-test-password",
        )
        cls.editor = User.objects.create_user(
            username="portfolio-editor", password="portfolio-test-password",
        )
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.item = cls.model.objects.create(**cls.payload)
        cls.list_url = reverse(f"api:{cls.resource}-list")
        cls.detail_url = reverse(f"api:{cls.resource}-detail", args=[cls.item.pk])
        cls.star_url = reverse(f"api:{cls.resource}-star", args=[cls.item.pk])
        cls.page_url = reverse(f"main:show_{cls.resource}")

    def snapshot(self):
        return list(self.model.objects.order_by("id").values())

    def test_all_roles_can_read_without_changing_the_database(self):
        before = self.snapshot()
        for user in (None, self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            for url in (self.list_url, self.detail_url):
                for method in ("get", "head", "options"):
                    with self.subTest(user=user, url=url, method=method):
                        self.assertEqual(getattr(self.client, method)(url).status_code, 200)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.item.starred_by.count(), 0)

    def test_guest_and_regular_user_cannot_write(self):
        before = self.snapshot()
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("put", self.detail_url, self.payload),
                ("patch", self.detail_url, {self.edit_field: "Forbidden"}),
                ("delete", self.detail_url, {}),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(self.item.starred_by.count(), 0)

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {self.edit_field: "Updated"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(getattr(self.item, self.edit_field), "Updated")
        self.assertEqual(self.item.description, self.payload["description"])
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(getattr(self.item, self.edit_field), self.payload[self.edit_field])
        before = self.snapshot()
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        before_count = self.model.objects.count()
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        created_id = response.data["id"]
        self.assertEqual(self.model.objects.count(), before_count + 1)
        created = self.model.objects.get(pk=created_id)
        self.assertEqual(created.description, self.payload["description"])
        detail_url = reverse(f"api:{self.resource}-detail", args=[created_id])
        self.assertEqual(self.client.patch(detail_url, {self.edit_field: "Updated"}, format="json").status_code, 200)
        created.refresh_from_db()
        self.assertEqual(getattr(created, self.edit_field), "Updated")
        self.assertEqual(self.client.put(detail_url, self.payload, format="json").status_code, 200)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(self.model.objects.filter(pk=created_id).exists())
        self.assertEqual(self.model.objects.count(), before_count)

    def test_search_matches_both_fields_case_insensitively(self):
        for query in self.search_queries:
            with self.subTest(query=query):
                response = self.client.get(self.list_url, {"q": f"  {query}  "})
                self.assertEqual(response.status_code, 200)
                self.assertIn(str(self.item.pk), [item["id"] for item in response.data])
        self.assertEqual(self.client.get(self.list_url, {"q": "no-such-portfolio-record"}).data, [])
        self.model.objects.all().delete()
        self.assertEqual(self.client.get(self.list_url).data, [])

    def test_text_validation_rejects_empty_html_and_keeps_database_unchanged(self):
        self.client.force_authenticate(user=self.owner)
        before = self.snapshot()
        for field in self.text_fields:
            for value in ("   ", "<i></i>"):
                with self.subTest(field=field, value=value):
                    for method, url, payload in (
                        ("post", self.list_url, {**self.payload, field: value}),
                        ("patch", self.detail_url, {field: value}),
                    ):
                        response = getattr(self.client, method)(url, payload, format="json")
                        self.assertEqual(response.status_code, 400)
                        self.assertIn(field, response.data)
                        self.assertEqual(self.snapshot(), before)

    def test_valid_text_is_cleaned_by_serializer(self):
        self.client.force_authenticate(user=self.owner)
        payload = {field: "<b>ok</b>" for field in self.text_fields}
        response = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        for field in self.text_fields:
            self.assertEqual(getattr(self.item, field), "ok")

    def test_put_requires_required_fields_and_missing_ids_return_404(self):
        self.client.force_authenticate(user=self.owner)
        before = self.snapshot()
        self.assertEqual(self.client.put(self.detail_url, {}, format="json").status_code, 400)
        self.assertEqual(self.snapshot(), before)
        missing = uuid.uuid4()
        detail_url = reverse(f"api:{self.resource}-detail", args=[missing])
        star_url = reverse(f"api:{self.resource}-star", args=[missing])
        for method, payload in (("get", {}), ("patch", self.payload), ("delete", {})):
            self.assertEqual(getattr(self.client, method)(detail_url, payload, format="json").status_code, 404)
        self.assertEqual(self.client.post(star_url).status_code, 404)
        self.assertEqual(self.snapshot(), before)

    def test_star_uses_session_user_and_never_client_supplied_account(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.item.starred_by.count(), 0)
        for user in (self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            with self.subTest(user=user):
                response = self.client.post(self.star_url, {"starred_by": [self.owner.pk]}, format="json")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data["is_starred"])
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(list(self.item.starred_by.values_list("pk", flat=True)), [user.pk])
                self.assertEqual(self.client.get(self.detail_url).data["is_starred"], True)
                response = self.client.post(self.star_url)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.data["is_starred"])
                self.assertEqual(self.item.starred_by.count(), 0)

    def test_summary_fields_are_read_only_and_hide_sensitive_account_data(self):
        self.item.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {
            "id": str(uuid.uuid4()), "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.owner.pk],
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.item.pk))
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], self.visitor.username)
        self.assertNotIn("starred_by", response.data)
        self.assertNotIn(self.visitor.email, response.content.decode())
        self.assertNotIn(self.visitor.password, response.content.decode())
        self.assertEqual(list(self.item.starred_by.values_list("pk", flat=True)), [self.visitor.pk])

    def test_session_writes_need_csrf_for_owner_editor_and_regular_user(self):
        for user, url, method, payload in (
            (self.owner, self.list_url, "post", self.payload),
            (self.editor, self.detail_url, "patch", {self.edit_field: "Session update"}),
            (self.visitor, self.star_url, "post", {}),
        ):
            with self.subTest(user=user):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(client.login(username=user.username, password="portfolio-test-password"))
                page = client.get(self.page_url)
                self.assertEqual(page.status_code, 200)
                self.assertIn("csrftoken", client.cookies)
                before = self.snapshot()
                response = getattr(client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.item.starred_by.count(), 0)
                token = client.cookies["csrftoken"].value
                response = getattr(client, method)(
                    url, payload, format="json", HTTP_X_CSRFTOKEN=token,
                    HTTP_ORIGIN="http://testserver",
                )
                self.assertEqual(response.status_code, 201 if user == self.owner else 200)
                if user == self.editor:
                    self.item.refresh_from_db()
                    self.assertEqual(getattr(self.item, self.edit_field), "Session update")
                if user == self.visitor:
                    self.assertEqual(list(self.item.starred_by.values_list("pk", flat=True)), [user.pk])

    def test_browsable_api_and_page_role_controls(self):
        response = self.client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rest_framework/api.html")
        for user in (None, self.visitor, self.editor, self.owner):
            client = APIClient()
            if user:
                client.force_login(user)
            response = client.get(self.page_url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("csrftoken", client.cookies)
            self.assertContains(response, self.list_url)
            self.assertContains(response, "js/portfolio-section.js")
            if user == self.owner:
                self.assertContains(response, "data-create")
            else:
                self.assertNotContains(response, "data-create")
            if user in (self.editor, self.owner):
                self.assertContains(response, "data-portfolio-form")
            else:
                self.assertNotContains(response, "data-portfolio-form")

    def test_legacy_delete_cannot_use_get_or_bypass_editor_restrictions(self):
        url = reverse(f"main:delete_{self.resource}", args=[self.item.pk])
        before = self.snapshot()
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.snapshot(), before)
        for user in (self.editor, self.visitor):
            self.client.force_login(user)
            self.assertEqual(self.client.post(url).status_code, 403)
            self.assertEqual(self.snapshot(), before)


class EducationAPIIntegrationTest(PortfolioAPIChecks, APITestCase):
    model = Education
    resource = "education"
    edit_field = "degree"
    text_fields = ("institution", "degree", "start_year", "end_year", "description")
    search_queries = ("TEST UNIVERSITY", "S2 API")
    payload = {
        "institution": "Test University", "degree": "S2 API", "start_year": "2025",
        "end_year": "Present", "description": "Education API fixture",
    }


class ExperienceAPIIntegrationTest(PortfolioAPIChecks, APITestCase):
    model = Experience
    resource = "experience"
    edit_field = "title"
    text_fields = ("title", "description")
    search_queries = ("API INTERNSHIP", "INTERNSHIP")
    payload = {
        "title": "API Internship", "category": "internship",
        "description": "Experience API fixture", "ended_at": None,
    }

    def test_invalid_category_url_and_date_do_not_change_data(self):
        self.client.force_authenticate(user=self.owner)
        before = self.snapshot()
        for field, value in (
            ("category", "not-a-category"), ("thumbnail", "javascript:alert(1)"),
            ("ended_at", "not-a-date"),
        ):
            response = self.client.patch(self.detail_url, {field: value}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
            self.assertEqual(self.snapshot(), before)

    def test_ongoing_and_category_labels_are_computed(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {
            "ended_at": "2026-11-08T12:00:00+07:00", "is_ongoing": True,
            "started_at": "2000-01-01T00:00:00Z", "category_display": "Forged",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_ongoing"])
        self.assertEqual(response.data["category_display"], "Internship")
        self.item.refresh_from_db()
        self.assertNotEqual(self.item.started_at.year, 2000)
        self.assertEqual(self.item.ended_at.hour, 5)
