from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Acme")
        cls.other_company = Company.objects.create(name="Globex")

    def setUp(self):
        self.list_url = reverse("category-list")

    def detail_url(self, category_id):
        return reverse("category-detail", args=[category_id])

    def test_list(self):
        Category.objects.create(company=self.company, name="Books")
        Category.objects.create(company=self.company, name="Apparel")
        Category.objects.create(company=self.other_company, name="Toys")

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Default ordering is by name ascending.
        self.assertEqual([row["name"] for row in response.data], ["Apparel", "Books", "Toys"])

    def test_list_filter_by_company(self):
        Category.objects.create(company=self.company, name="Books")
        Category.objects.create(company=self.other_company, name="Toys")

        response = self.client.get(self.list_url, {"company": str(self.company.id)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Books")

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="Books")

        response = self.client.get(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(category.id))
        self.assertEqual(response.data["name"], "Books")
        self.assertEqual(str(response.data["company"]), str(self.company.id))

    def test_retrieve_not_found(self):
        response = self.client.get(self.detail_url("00000000-0000-0000-0000-000000000000"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "Books"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        created = Category.objects.get()
        self.assertEqual(created.name, "Books")
        self.assertEqual(created.company_id, self.company.id)

    def test_create_with_parent(self):
        parent = Category.objects.create(company=self.company, name="Books")
        payload = {
            "company": str(self.company.id),
            "name": "Comics",
            "parent_category": str(parent.id),
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["parent_category"]), str(parent.id))

    def test_create_rejects_parent_from_other_company(self):
        parent = Category.objects.create(company=self.other_company, name="Toys")
        payload = {
            "company": str(self.company.id),
            "name": "Comics",
            "parent_category": str(parent.id),
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_create_rejects_missing_name(self):
        payload = {"company": str(self.company.id)}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_rejects_duplicate_name_in_same_company(self):
        Category.objects.create(company=self.company, name="Books")
        payload = {"company": str(self.company.id), "name": "Books"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        category = Category.objects.create(company=self.company, name="Books")
        payload = {"company": str(self.company.id), "name": "Magazines"}

        response = self.client.put(self.detail_url(category.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "Magazines")

    def test_partial_update(self):
        category = Category.objects.create(company=self.company, name="Books")

        response = self.client.patch(
            self.detail_url(category.id), {"name": "Magazines"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "Magazines")

    def test_update_rejects_self_as_parent(self):
        category = Category.objects.create(company=self.company, name="Books")

        response = self.client.patch(
            self.detail_url(category.id),
            {"parent_category": str(category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="Books")

        response = self.client.delete(self.detail_url(category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
