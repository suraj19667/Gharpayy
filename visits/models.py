from mongoengine import (
    Document, StringField, DateTimeField, ReferenceField, DateField
)
from datetime import datetime


VISIT_OUTCOMES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled'),
    ('interested', 'Interested'),
    ('not_interested', 'Not Interested'),
]


class Visit(Document):
    lead = ReferenceField('leads.Lead', required=True)
    property_name = StringField(required=True, max_length=200)
    property_address = StringField(max_length=500)
    visit_date = DateField(required=True)
    visit_time = StringField(required=True, max_length=10)
    outcome = StringField(
        choices=[o[0] for o in VISIT_OUTCOMES],
        default='pending'
    )
    notes = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'visits',
        'ordering': ['-visit_date'],
        'indexes': ['lead', 'visit_date', 'outcome'],
    }

    def __str__(self):
        return f"{self.property_name} - {self.visit_date}"

    def get_outcome_display(self):
        return dict(VISIT_OUTCOMES).get(self.outcome, self.outcome)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(*args, **kwargs)
