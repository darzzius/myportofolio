from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen Kalkulus",
            description="Membantu mahasiswa memahami materi Kalkulus 1.",
            category="part-time",
        )
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="S1 Sistem Informasi",
            start_year="2025",
            end_year="Sekarang",
            description="Fakultas Ilmu Komputer. Aktif dalam kegiatan akademik.",
        ) 

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), self.experience.title)
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, reverse("main:get_experience_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')

        # The browser fetches the cards separately; Django's client does not run JS.
        data = self.client.get(reverse("main:get_experience_json")).json()
        item = next(item for item in data if item["pk"] == str(self.experience.pk))
        self.assertEqual(item["fields"]["title"], self.experience.title)
        self.assertEqual(item["fields"]["description"], self.experience.description)
        self.assertEqual(item["fields"]["category"], "Part-Time")
        self.assertTrue(item["fields"]["is_ongoing"])

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan atau ditemukan.")
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(response.status_code, 200)
        item = next(item for item in response.json() if item["pk"] == str(self.experience.pk))
        self.assertFalse(item["fields"]["is_ongoing"])
        self.assertEqual(item["fields"]["ended_at"], self.experience.ended_at.strftime("%b %Y"))

    def test_education_model(self):
        self.assertEqual(str(self.education), "Universitas Indonesia")
        self.assertEqual(self.education.degree, "S1 Sistem Informasi")
        self.assertEqual(self.education.start_year, "2025")
        self.assertEqual(self.education.end_year, "Sekarang")

    def test_education_page(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, 'id="education-timeline"')
        self.assertContains(response, reverse("main:get_education_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

        data = self.client.get(reverse("main:get_education_json")).json()
        item = next(item for item in data if item["pk"] == str(self.education.pk))
        self.assertEqual(item["fields"]["institution"], self.education.institution)
        self.assertEqual(item["fields"]["degree"], self.education.degree)
        self.assertEqual(item["fields"]["description"], self.education.description)

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan atau ditemukan.")
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
