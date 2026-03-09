from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from leads.models import Lead, FollowUp


class Command(BaseCommand):
    help = 'Create follow-up reminders for stale leads (>24 hours in same stage)'

    def handle(self, *args, **options):
        cutoff = datetime.utcnow() - timedelta(hours=24)
        stale_stages = [
            'new_lead', 'contacted', 'requirement_collected',
            'property_suggested', 'visit_scheduled', 'visit_completed'
        ]

        stale_leads = Lead.objects.filter(
            status__in=stale_stages,
            stage_updated_at__lte=cutoff
        )

        created_count = 0
        for lead in stale_leads:
            # Avoid duplicate reminders: skip if an incomplete follow-up exists
            existing = FollowUp.objects.filter(
                lead=lead,
                is_completed=False,
                stage_at_creation=lead.status
            ).first()

            if not existing:
                FollowUp(
                    lead=lead,
                    reminder_message=(
                        f"Follow up with {lead.name} — "
                        f"stale in '{lead.get_status_display()}' stage for over 24 hours."
                    ),
                    due_at=datetime.utcnow(),
                    stage_at_creation=lead.status,
                ).save()
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Created {created_count} follow-up reminder(s).'
            )
        )
