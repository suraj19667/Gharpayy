from mongoengine import (
    Document, StringField, DateTimeField, IntField, BooleanField
)
from datetime import datetime


class Agent(Document):
    name = StringField(required=True, max_length=100)
    email = StringField(required=True, unique=True, max_length=200)
    phone = StringField(max_length=15)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'agents',
        'ordering': ['name'],
    }

    def __str__(self):
        return self.name

    def active_leads_count(self):
        """Leads currently assigned and not yet closed (booked/lost)."""
        from leads.models import Lead
        return Lead.objects.filter(
            assigned_agent=self,
            status__nin=['booked', 'lost']
        ).count()

    def total_leads_count(self):
        """All leads ever assigned to this agent."""
        from leads.models import Lead
        return Lead.objects.filter(assigned_agent=self).count()

    def booked_count(self):
        """Leads this agent converted to Booked."""
        from leads.models import Lead
        return Lead.objects.filter(assigned_agent=self, status='booked').count()

    def conversion_rate(self):
        total = self.total_leads_count()
        if total == 0:
            return 0.0
        return round(self.booked_count() / total * 100, 1)


class RoundRobinState(Document):
    """Tracks the current index for round-robin assignment."""
    current_index = IntField(default=0)

    meta = {'collection': 'round_robin_state'}

    @classmethod
    def get_or_create(cls):
        state = cls.objects.first()
        if not state:
            state = cls(current_index=0)
            state.save()
        return state
