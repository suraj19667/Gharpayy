from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from calendar import monthrange
import logging

from leads.models import Lead, FollowUp, PIPELINE_STAGES, LEAD_SOURCES
from agents.models import Agent
from visits.models import Visit

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Dashboard view with defensive error handling for production."""
    
    # Initialize all variables with safe defaults
    total_leads = 0
    total_agents = 0
    total_visits = 0
    pending_followups = 0
    bookings_count = 0
    lost_count = 0
    conversion_rate = 0.0
    new_today = 0
    stage_counts = []
    visits_scheduled = 0
    visits_completed = 0
    source_counts = []
    agent_workload = []
    recent_leads = []
    upcoming_visits = []
    
    try:
        # Basic counts with error handling
        try:
            total_leads = Lead.objects.count()
        except Exception as e:
            logger.error(f"Error counting leads: {e}")
            
        try:
            total_agents = Agent.objects.filter(is_active=True).count()
        except Exception as e:
            logger.error(f"Error counting agents: {e}")
            
        try:
            total_visits = Visit.objects.count()
        except Exception as e:
            logger.error(f"Error counting visits: {e}")
            
        try:
            pending_followups = FollowUp.objects.filter(is_completed=False).count()
        except Exception as e:
            logger.error(f"Error counting followups: {e}")

        try:
            bookings_count = Lead.objects.filter(status='booked').count()
            lost_count = Lead.objects.filter(status='lost').count()
        except Exception as e:
            logger.error(f"Error counting bookings/lost: {e}")

        # Conversion rate
        if total_leads > 0:
            conversion_rate = round(bookings_count / total_leads * 100, 1)

        # New leads today
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            new_today = Lead.objects.filter(created_at__gte=today_start).count()
        except Exception as e:
            logger.error(f"Error counting new leads today: {e}")

        # Leads per stage
        try:
            for stage_key, stage_label in PIPELINE_STAGES:
                count = Lead.objects.filter(status=stage_key).count()
                stage_counts.append({'key': stage_key, 'label': stage_label, 'count': count})
        except Exception as e:
            logger.error(f"Error getting stage counts: {e}")

        # Visits
        try:
            visits_scheduled = Visit.objects.filter(outcome='pending').count()
            visits_completed = Visit.objects.filter(outcome__in=['completed', 'interested']).count()
        except Exception as e:
            logger.error(f"Error counting visits by outcome: {e}")

        # Lead source distribution
        try:
            for source_key, source_label in LEAD_SOURCES:
                count = Lead.objects.filter(source=source_key).count()
                if count > 0:
                    source_counts.append({'label': source_label, 'count': count})
        except Exception as e:
            logger.error(f"Error getting source counts: {e}")

        # Agent workload — active leads per agent
        try:
            for agent in Agent.objects.filter(is_active=True):
                try:
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
                except Exception as e:
                    logger.error(f"Error calculating stats for agent {agent.name}: {e}")
                    # Add agent with zero stats if calculation fails
                    agent_workload.append({
                        'name': agent.name,
                        'active': 0,
                        'total': 0,
                        'booked': 0,
                        'rate': 0.0,
                    })
            agent_workload.sort(key=lambda x: x['total'], reverse=True)
        except Exception as e:
            logger.error(f"Error getting agent workload: {e}")

        # Recent leads
        try:
            recent_leads = list(Lead.objects.order_by('-created_at')[:8])
        except Exception as e:
            logger.error(f"Error fetching recent leads: {e}")

        # Upcoming visits
        try:
            upcoming_visits = list(Visit.objects.filter(
                outcome='pending',
                visit_date__gte=date.today()
            ).order_by('visit_date')[:5])
        except Exception as e:
            logger.error(f"Error fetching upcoming visits: {e}")
            
    except Exception as e:
        logger.error(f"Unexpected error in dashboard view: {e}", exc_info=True)

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
    """Analytics view with defensive error handling."""
    
    # Initialize with safe defaults
    stage_labels, stage_data = [], []
    stage_colors = ['#4e73df', '#36b9cc', '#1cc88a', '#f6c23e', '#fd7e14', '#6f42c1', '#2ecc71', '#e74a3b']
    source_labels, source_data = [], []
    agent_stats = []
    monthly_data = []
    
    try:
        # Stage distribution
        try:
            for stage_key, stage_label in PIPELINE_STAGES:
                stage_labels.append(stage_label)
                stage_data.append(Lead.objects.filter(status=stage_key).count())
        except Exception as e:
            logger.error(f"Error getting stage distribution: {e}")

        # Source distribution
        try:
            for source_key, source_label in LEAD_SOURCES:
                count = Lead.objects.filter(source=source_key).count()
                if count > 0:
                    source_labels.append(source_label)
                    source_data.append(count)
        except Exception as e:
            logger.error(f"Error getting source distribution: {e}")

        # Agent performance
        try:
            for agent in Agent.objects.filter(is_active=True):
                try:
                    total = agent.total_leads_count()
                    booked = agent.booked_count()
                    agent_stats.append({
                        'name': agent.name,
                        'lead_count': total,
                        'booked_count': booked,
                        'conversion_rate': agent.conversion_rate(),
                    })
                except Exception as e:
                    logger.error(f"Error calculating stats for agent {agent.name}: {e}")
            agent_stats.sort(key=lambda x: x['lead_count'], reverse=True)
        except Exception as e:
            logger.error(f"Error getting agent performance: {e}")

        # Monthly leads — last 6 months
        try:
            now = datetime.utcnow()
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
        except Exception as e:
            logger.error(f"Error calculating monthly data: {e}")
            
    except Exception as e:
        logger.error(f"Unexpected error in analytics view: {e}", exc_info=True)

    return render(request, 'dashboard/analytics.html', {
        'stage_labels': stage_labels,
        'stage_data': stage_data,
        'stage_colors': stage_colors[:len(stage_labels)],
        'source_labels': source_labels,
        'source_data': source_data,
        'agent_stats': agent_stats,
        'monthly_data': monthly_data,
    })
