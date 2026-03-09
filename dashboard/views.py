from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from calendar import monthrange

from leads.models import Lead, FollowUp, PIPELINE_STAGES, LEAD_SOURCES
from agents.models import Agent
from visits.models import Visit


@login_required
def dashboard(request):
    total_leads = Lead.objects.count()
    total_agents = Agent.objects.filter(is_active=True).count()
    total_visits = Visit.objects.count()
    pending_followups = FollowUp.objects.filter(is_completed=False).count()

    bookings_count = Lead.objects.filter(status='booked').count()
    lost_count = Lead.objects.filter(status='lost').count()

    # Conversion rate
    conversion_rate = round(bookings_count / total_leads * 100, 1) if total_leads else 0.0

    # New leads today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = Lead.objects.filter(created_at__gte=today_start).count()

    # Leads per stage
    stage_counts = []
    for stage_key, stage_label in PIPELINE_STAGES:
        count = Lead.objects.filter(status=stage_key).count()
        stage_counts.append({'key': stage_key, 'label': stage_label, 'count': count})

    # Visits
    visits_scheduled = Visit.objects.filter(outcome='pending').count()
    visits_completed = Visit.objects.filter(outcome__in=['completed', 'interested']).count()

    # Lead source distribution
    source_counts = []
    for source_key, source_label in LEAD_SOURCES:
        count = Lead.objects.filter(source=source_key).count()
        if count > 0:
            source_counts.append({'label': source_label, 'count': count})

    # Agent workload — active leads per agent
    agent_workload = []
    for agent in Agent.objects.filter(is_active=True):
        active = agent.active_leads_count()
        total = agent.total_leads_count()
        booked = agent.booked_count()
        agent_workload.append({
            'name': agent.name,
            'active': active,
            'total': total,
            'booked': booked,
            'rate': agent.conversion_rate(),
        })
    agent_workload.sort(key=lambda x: x['total'], reverse=True)

    # Recent leads
    recent_leads = Lead.objects.order_by('-created_at')[:8]

    # Upcoming visits
    upcoming_visits = Visit.objects.filter(
        outcome='pending',
        visit_date__gte=date.today()
    ).order_by('visit_date')[:5]

    return render(request, 'dashboard/dashboard.html', {
        'total_leads': total_leads,
        'total_agents': total_agents,
        'total_visits': total_visits,
        'pending_followups': pending_followups,
        'bookings_count': bookings_count,
        'lost_count': lost_count,
        'conversion_rate': conversion_rate,
        'new_today': new_today,
        'stage_counts': stage_counts,
        'visits_scheduled': visits_scheduled,
        'visits_completed': visits_completed,
        'source_counts': source_counts,
        'agent_workload': agent_workload,
        'recent_leads': recent_leads,
        'upcoming_visits': upcoming_visits,
        'pipeline_stages': PIPELINE_STAGES,
    })


@login_required
def analytics(request):
    # Stage distribution
    stage_labels, stage_data = [], []
    stage_colors = ['#4e73df', '#36b9cc', '#1cc88a', '#f6c23e', '#fd7e14', '#6f42c1', '#2ecc71', '#e74a3b']
    for stage_key, stage_label in PIPELINE_STAGES:
        stage_labels.append(stage_label)
        stage_data.append(Lead.objects.filter(status=stage_key).count())

    # Source distribution
    source_labels, source_data = [], []
    for source_key, source_label in LEAD_SOURCES:
        count = Lead.objects.filter(source=source_key).count()
        if count > 0:
            source_labels.append(source_label)
            source_data.append(count)

    # Agent performance
    agent_stats = []
    for agent in Agent.objects.filter(is_active=True):
        total = agent.total_leads_count()
        booked = agent.booked_count()
        agent_stats.append({
            'name': agent.name,
            'lead_count': total,
            'booked_count': booked,
            'conversion_rate': agent.conversion_rate(),
        })
    agent_stats.sort(key=lambda x: x['lead_count'], reverse=True)

    # Monthly leads — last 6 months (correct calendar boundary calculation)
    now = datetime.utcnow()
    monthly_data = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        month_start = datetime(y, m, 1)
        if m == 12:
            month_end = datetime(y + 1, 1, 1)
        else:
            month_end = datetime(y, m + 1, 1)
        count = Lead.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_data.append({'month': month_start.strftime('%b %Y'), 'count': count})

    return render(request, 'dashboard/analytics.html', {
        'stage_labels': stage_labels,
        'stage_data': stage_data,
        'stage_colors': stage_colors[:len(stage_labels)],
        'source_labels': source_labels,
        'source_data': source_data,
        'agent_stats': agent_stats,
        'monthly_data': monthly_data,
    })
