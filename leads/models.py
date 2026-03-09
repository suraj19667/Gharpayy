from mongoengine import (
    Document, StringField, DateTimeField, ReferenceField, BooleanField
)
from datetime import datetime


PIPELINE_STAGES = [
    ('new_lead', 'New Lead'),
    ('contacted', 'Contacted'),
    ('requirement_collected', 'Requirement Collected'),
    ('property_suggested', 'Property Suggested'),
    ('visit_scheduled', 'Visit Scheduled'),
    ('visit_completed', 'Visit Completed'),
    ('booked', 'Booked'),
    ('lost', 'Lost'),
]

PIPELINE_STAGE_LABELS = dict(PIPELINE_STAGES)

LEAD_SOURCES = [
    ('website', 'Website'),
    ('whatsapp', 'WhatsApp'),
    ('social_media', 'Social Media'),
    ('phone_call', 'Phone Call'),
    ('referral', 'Referral'),
    ('walk_in', 'Walk-in'),
    ('other', 'Other'),
]

LEAD_SOURCE_LABELS = dict(LEAD_SOURCES)


class Lead(Document):
    name = StringField(required=True, max_length=100)
    phone = StringField(required=True, max_length=15)
    email = StringField(max_length=200)
    source = StringField(
        choices=[s[0] for s in LEAD_SOURCES],
        default='website'
    )
    status = StringField(
        choices=[s[0] for s in PIPELINE_STAGES],
        default='new_lead'
    )
    assigned_agent = ReferenceField('agents.Agent', null=True)
    notes = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    stage_updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'leads',
        'ordering': ['-created_at'],
        'indexes': ['status', 'source', 'assigned_agent', 'created_at'],
    }

    def __str__(self):
        return f"{self.name} - {self.phone}"

    def get_status_display(self):
        return PIPELINE_STAGE_LABELS.get(self.status, self.status)

    def get_source_display(self):
        return LEAD_SOURCE_LABELS.get(self.source, self.source)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(*args, **kwargs)


class StageHistory(Document):
    lead = ReferenceField(Lead, required=True)
    from_stage = StringField()
    to_stage = StringField()
    changed_at = DateTimeField(default=datetime.utcnow)
    changed_by = StringField()

    meta = {
        'collection': 'stage_history',
        'ordering': ['-changed_at'],
    }


class FollowUp(Document):
    lead = ReferenceField(Lead, required=True)
    reminder_message = StringField(max_length=500)
    due_at = DateTimeField(required=True)
    is_completed = BooleanField(default=False)
    completed_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    stage_at_creation = StringField(max_length=50)

    meta = {
        'collection': 'followups',
        'ordering': ['due_at'],
        'indexes': ['lead', 'is_completed', 'due_at'],
    }

    def __str__(self):
        return f"FollowUp for {self.lead.name} due at {self.due_at}"
