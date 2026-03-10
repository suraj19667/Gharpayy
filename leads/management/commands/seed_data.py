"""Seed the database with sample data for testing."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from agents.models import Agent
from leads.models import Lead, PIPELINE_STAGES
from visits.models import Visit
from datetime import datetime, date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with sample agents and leads for testing'

    def handle(self, *args, **options):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Create agents
        agent_data = [
            {'name': 'Rahul Sharma', 'email': 'rahul@gharpayy.com', 'phone': '+91 9876543210'},
            {'name': 'Priya Singh', 'email': 'priya@gharpayy.com', 'phone': '+91 9876543211'},
            {'name': 'Amit Verma', 'email': 'amit@gharpayy.com', 'phone': '+91 9876543212'},
        ]
        agents = []
        for data in agent_data:
            existing = Agent.objects(email=data['email']).first()
            if not existing:
                agent = Agent(**data, is_active=True)
                agent.save()
                agents.append(agent)
                self.stdout.write(f'  Created agent: {data["name"]}')
            else:
                agents.append(existing)

        if not agents:
            self.stdout.write(self.style.WARNING('No agents created (already exist).'))
            return

        # Create leads
        names = [
            'Arun Kumar', 'Sunita Patel', 'Rohit Mehta', 'Kavya Nair',
            'Deepak Gupta', 'Pooja Yadav', 'Vijay Reddy', 'Anjali Mishra',
            'Sanjay Tiwari', 'Ritu Sharma',
        ]
        sources = ['website', 'whatsapp', 'social_media', 'phone_call', 'referral']
        statuses = [s[0] for s in PIPELINE_STAGES]

        for i, name in enumerate(names):
            phone = f'+91 98765432{i:02d}'
            agent = agents[i % len(agents)]
            lead = Lead(
                name=name,
                phone=phone,
                email=f'{name.lower().replace(" ", ".")}@email.com',
                source=random.choice(sources),
                status=random.choice(statuses),
                assigned_agent=agent,
                notes=f'Sample lead {i+1} for testing.',
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            )
            lead.save()
            self.stdout.write(f'  Created lead: {name}')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('Login at /login/ with: admin / admin123'))
