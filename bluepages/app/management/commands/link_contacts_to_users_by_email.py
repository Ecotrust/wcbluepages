from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import Contact
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Link contacts to users when contact.email matches user.email."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be linked without writing changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        users_by_email = {}
        duplicate_user_emails = set()

        for user in (
            User.objects.exclude(email__isnull=True).exclude(email="").iterator()
        ):
            normalized = user.email.strip().lower()
            if not normalized:
                continue
            if normalized in users_by_email:
                duplicate_user_emails.add(normalized)
                continue
            users_by_email[normalized] = user.id

        used_user_ids = set(
            Contact.objects.exclude(user_id__isnull=True).values_list(
                "user_id", flat=True
            )
        )

        contacts = (
            Contact.objects.filter(user_id__isnull=True)
            .exclude(email__isnull=True)
            .exclude(email="")
            .order_by("id")
        )

        examined = 0
        linked = 0
        skipped_no_match = 0
        skipped_used_user = 0
        skipped_duplicate_user_email = 0

        with transaction.atomic():
            for contact in contacts.iterator():
                examined += 1
                normalized = contact.email.strip().lower()

                if normalized in duplicate_user_emails:
                    skipped_duplicate_user_email += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIP duplicate user email: contact_id={contact.id} email={contact.email}"
                        )
                    )
                    continue

                user_id = users_by_email.get(normalized)
                if not user_id:
                    skipped_no_match += 1
                    continue

                if user_id in used_user_ids:
                    skipped_used_user += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"SKIP user already linked: contact_id={contact.id} user_id={user_id} email={contact.email}"
                        )
                    )
                    continue

                linked += 1
                used_user_ids.add(user_id)

                if dry_run:
                    self.stdout.write(
                        f"DRY-RUN link: contact_id={contact.id} -> user_id={user_id} email={contact.email}"
                    )
                    continue

                Contact.objects.filter(id=contact.id, user_id__isnull=True).update(
                    user_id=user_id
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Linked contact_id={contact.id} -> user_id={user_id} email={contact.email}"
                    )
                )

            if dry_run:
                transaction.set_rollback(True)

        summary_style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(summary_style(""))
        self.stdout.write(summary_style("Summary"))
        self.stdout.write(summary_style(f"Examined contacts: {examined}"))
        self.stdout.write(summary_style(f"Linked contacts: {linked}"))
        self.stdout.write(
            summary_style(f"Skipped (no user email match): {skipped_no_match}")
        )
        self.stdout.write(
            summary_style(f"Skipped (user already linked): {skipped_used_user}")
        )
        self.stdout.write(
            summary_style(
                f"Skipped (duplicate user emails): {skipped_duplicate_user_email}"
            )
        )
        if dry_run:
            self.stdout.write(summary_style("No database changes were committed."))
