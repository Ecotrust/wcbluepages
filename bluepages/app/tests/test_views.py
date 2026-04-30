from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from app.models import Contact, ContactSuggestion, Record, Topic, Region

from app.views import (
    formatSuggestionMenuEntry,
)


class GetSuggestionMenuTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

    def test_getSuggestionMenu_unauthenticated(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse("get_suggestion_menu"))
        self.assertEqual(response.status_code, 302)

    def test_getSuggestionMenu_no_suggestions(self):
        """Test getSuggestionMenu with no suggestions"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("get_suggestion_menu"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["suggestions"], [])

    def test_getSuggestionMenu_with_pending_suggestions(self):
        """Test getSuggestionMenu returns pending suggestions first"""
        self.client.login(username="testuser", password="testpass123")

        ContactSuggestion.objects.create(
            user=self.user, first_name="John", last_name="Doe", status="Pending"
        )

        response = self.client.get(reverse("get_suggestion_menu"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["suggestions"]), 1)
        self.assertEqual(
            response.context["suggestions"][0]["contact_name"], "new (Doe, John)"
        )

    def test_getSuggestionMenu_user_only_sees_own_suggestions(self):
        """Test that users only see their own suggestions"""
        self.client.login(username="testuser", password="testpass123")

        suggestion1 = ContactSuggestion.objects.create(
            user=self.user, first_name="John", last_name="Doe", status="Pending"
        )
        ContactSuggestion.objects.create(
            user=self.other_user, first_name="Jane", last_name="Smith", status="Pending"
        )

        response = self.client.get(reverse("get_suggestion_menu"))
        self.assertEqual(len(response.context["suggestions"]), 1)
        self.assertEqual(response.context["suggestions"][0]["id"], suggestion1.id)

    def test_getSuggestionMenu_sorted_by_status(self):
        """Test suggestions are sorted by status (Pending first)"""
        self.client.login(username="testuser", password="testpass123")

        ContactSuggestion.objects.create(
            user=self.user, first_name="John", last_name="Doe", status="Pending"
        )
        ContactSuggestion.objects.create(
            user=self.user, first_name="Jane", last_name="Smith", status="Approved"
        )

        response = self.client.get(reverse("get_suggestion_menu"))
        suggestions = response.context["suggestions"]
        self.assertEqual(suggestions[0]["status"], "Pending")
        self.assertEqual(suggestions[1]["status"], "Approved")

    def test_formatSuggestionMenuEntry(self):
        """Test formatting of suggestion menu entry"""
        suggestion = ContactSuggestion.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            status="Pending",
            description="Test description",
        )

        formatted = formatSuggestionMenuEntry(suggestion)
        self.assertEqual(formatted["id"], suggestion.id)
        self.assertEqual(formatted["status"], "Pending")
        self.assertEqual(formatted["description"], "Test description")
        self.assertEqual(formatted["topics"], [])


class DeleteRecordTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.topic = Topic.objects.create(name="Test Topic")
        self.contact = Contact.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
        )
        self.record = Record.objects.create(
            topic=self.topic,
            contact=self.contact,
        )

    def test_deleteRecord_unauthenticated(self):
        """Test that unauthenticated users cannot delete records"""
        response = self.client.post(
            reverse("delete_record", args=[self.contact.id, self.record.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_deleteRecord_authenticated(self):
        """Test that authenticated users can delete their own records"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("delete_record", args=[self.contact.id, self.record.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.contact.record_set.filter(id=self.record.id).exists())

    def test_deleteRecord_cannot_delete_others_records(self):
        """Test that authenticated users receive 404 when trying to delete records that do not belong to them"""
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        other_contact = Contact.objects.create(
            user=other_user,
            first_name="Jane",
            last_name="Smith",
        )
        other_record = Record.objects.create(
            topic=self.topic,
            contact=other_contact,
        )

        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("delete_record", args=[other_contact.id, other_record.id])
        )

        self.assertEqual(response.json()["status"], 404)
        self.assertTrue(other_contact.record_set.filter(id=other_record.id).exists())


class ContactFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.contact = Contact.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

    def test_contactForm_unauthenticated(self):
        """Test that unauthenticated users cannot access contact form"""
        response = self.client.get(reverse("contact_form", args=[self.contact.id]))
        self.assertEqual(response.status_code, 302)

    def test_contactForm_authenticated(self):
        """Test that authenticated users can access contact form"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("contact_form", args=[self.contact.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_contactForm_post_request_valid_data(self):
        """Test submitting valid data to contact form creates/updates contact"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("contact_form", args=[self.contact.id]),
            {
                "first_name": "John",
                "last_name": "Doee",
                "email": "john.doe@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.first_name, "John")
        self.assertEqual(self.contact.last_name, "Doee")
        self.assertEqual(self.contact.email, "john.doe@example.com")
        self.assertEqual(Contact.objects.filter(user=self.user).count(), 1)

        response_data = response.json()
        self.assertEqual(response_data["contact"]["id"], self.contact.id)
        self.assertEqual(response_data["contact"]["email"], "john.doe@example.com")


class ContactSuggestionFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.contact_suggestion = ContactSuggestion.objects.create(
            user=self.user, first_name="John", last_name="Doe", status="Pending"
        )

    def test_contactSuggestionForm_unauthenticated(self):
        """Test that unauthenticated users cannot access contact suggestion form"""
        response = self.client.get(
            reverse("contact_suggestion_form", args=[self.contact_suggestion.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_contactSuggestionForm_authenticated(self):
        """Test that authenticated users can access contact suggestion form"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("contact_suggestion_form", args=[self.contact_suggestion.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_contactSuggestionForm_post_request_valid_data(self):
        """Test submitting valid data to contact suggestion form creates contact and updates suggestion"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("contact_suggestion_form", args=[self.contact_suggestion.id]),
            {
                "user": self.user.id,
                "status": "Pending",
                "first_name": "John",
                "last_name": "Doee",
                "email": "john.doe@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.contact_suggestion.refresh_from_db()
        self.assertEqual(self.contact_suggestion.first_name, "John")
        self.assertEqual(self.contact_suggestion.last_name, "Doee")
        self.assertEqual(self.contact_suggestion.email, "john.doe@example.com")
        self.assertEqual(ContactSuggestion.objects.filter(user=self.user).count(), 1)

        response_data = response.json()
        self.assertEqual(response_data["contact"]["id"], self.contact_suggestion.id)
        self.assertEqual(response_data["contact"]["contact_name"], "new (Doee, John)")


class RecordContactFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.contact = Contact.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        self.topic = Topic.objects.create(name="Test Topic")
        self.other_topic = Topic.objects.create(name="Other Topic")
        self.region = Region.objects.create(id="N001", name="Test Region")
        self.record = Record.objects.create(
            contact=self.contact,
            topic=self.topic,
        )
        self.record.regions.add(self.region)

    def test_recordContactForm_unauthenticated(self):
        """Test that unauthenticated users cannot access record contact form"""
        response = self.client.get(
            reverse("record_contact_form", args=[self.contact.id, self.record.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_recordContactForm_authenticated(self):
        """Test that authenticated users can access record contact form"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("record_contact_form", args=[self.contact.id, self.record.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("record_form", response.context)

    def test_recordContactForm_post_request_valid_data(self):
        """Test submitting valid data to record contact form creates/updates record"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("record_contact_form", args=[self.contact.id, self.record.id]),
            {
                "topic": self.other_topic.id,
                "regions": [self.region.id],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.topic, self.other_topic)
        self.assertEqual(self.contact.record_set.count(), 1)

        response_data = response.json()
        self.assertEqual(response_data["contact"]["id"], self.record.id)
        self.assertEqual(response_data["contact"]["topic"], self.other_topic.name)


class RecordSuggestionFormTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.contact_suggestion = ContactSuggestion.objects.create(
            user=self.user, first_name="John", last_name="Doe", status="Pending"
        )
        self.topic = Topic.objects.create(name="Test Topic")
        self.region = Region.objects.create(id="N001", name="Test Region")

    def test_recordSuggestionForm_unauthenticated(self):
        """Test that unauthenticated users cannot access record suggestion form"""
        response = self.client.get(
            reverse("record_suggestion_form", args=[self.contact_suggestion.id, 1])
        )
        self.assertEqual(response.status_code, 302)

    def test_recordSuggestionForm_authenticated(self):
        """Test that authenticated users can access record suggestion form"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("record_suggestion_form", args=[self.contact_suggestion.id, 1])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_recordSuggestionForm_post_request_valid_data(self):
        """Test submitting valid data to record suggestion form creates record suggestion"""
        self.client.login(username="testuser", password="testpass123")
        self.other_topic = Topic.objects.create(name="Other Topic")
        response = self.client.post(
            reverse("record_suggestion_form", args=[self.contact_suggestion.id, 1]),
            {
                "topic": self.other_topic.id,
                "regions": [self.region.id],
            },
        )
        self.assertEqual(response.status_code, 200)
        record_suggestion = self.contact_suggestion.recordsuggestion_set.first()

        self.assertIsNotNone(record_suggestion)
        self.assertEqual(record_suggestion.topic, self.other_topic)
        response_data = response.json()
        self.assertEqual(
            response_data["contact_suggestion"]["id"], self.contact_suggestion.id
        )
        self.assertEqual(
            response_data["contact_suggestion"]["topics"][0]["topic"],
            self.other_topic.name,
        )
