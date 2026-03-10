from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
import logging

from leads.models import Lead, StageHistory, FollowUp, PIPELINE_STAGES, LEAD_SOURCES, PIPELINE_STAGE_LABELS
from agents.models import Agent
from agents.utils import assign_agent_round_robin
from leads.forms import LeadCaptureForm, LeadUpdateForm, StageUpdateForm
from visits.models import Visit

logger = logging.getLogger(__name__)
PAGE_SIZE = 15


@login_required
def lead_list(request):
    \"\"\"Lead list view with error handling.\"\"\"\n    status_filter = request.GET.get('status', '')
    source_filter = request.GET.get('source', '')
    search = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    if page < 1:
        page = 1

    try:
        leads_qs = Lead.objects.all()
        if status_filter:
            leads_qs = leads_qs.filter(status=status_filter)
        if source_filter:
            leads_qs = leads_qs.filter(source=source_filter)
        if search:
            leads_qs = leads_qs.filter(name__icontains=search)

        total_count = leads_qs.count()
        total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * PAGE_SIZE
        leads = list(leads_qs.skip(offset).limit(PAGE_SIZE))
    except Exception as e:
        logger.error(f\"Error fetching leads: {e}\", exc_info=True)
        leads = []
        total_count = 0
        total_pages = 1
        page = 1
        messages.error(request, 'Error loading leads. Please try again.')

    return render(request, 'leads/lead_list.html', {
        'leads': leads,
        'pipeline_stages': PIPELINE_STAGES,
        'lead_sources': LEAD_SOURCES,
        'status_filter': status_filter,
        'source_filter': source_filter,
        'search': search,
        'page': page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1,
        'next_page': page + 1,
    })


@login_required
def lead_detail(request, lead_id):
    try:
        lead = Lead.objects.get(id=lead_id)
    except Exception:
        messages.error(request, 'Lead not found.')
        return redirect('lead_list')

    history = StageHistory.objects.filter(lead=lead).order_by('-changed_at')
    followups = FollowUp.objects.filter(lead=lead).order_by('due_at')
    visits = Visit.objects.filter(lead=lead).order_by('-visit_date')
    agents = Agent.objects.filter(is_active=True)
    agent_choices = [(str(a.id), a.name) for a in agents]

    if request.method == 'POST':
        form = LeadUpdateForm(request.POST, agent_choices=agent_choices)
        if form.is_valid():
            old_status = lead.status
            new_status = form.cleaned_data['status']

            lead.name = form.cleaned_data['name']
            lead.phone = form.cleaned_data['phone']
            lead.email = form.cleaned_data.get('email', '')
            lead.source = form.cleaned_data['source']
            lead.status = new_status
            lead.notes = form.cleaned_data.get('notes', '')

            agent_id = form.cleaned_data.get('assigned_agent')
            if agent_id:
                try:
                    lead.assigned_agent = Agent.objects.get(id=agent_id)
                except Exception:
                    pass

            if old_status != new_status:
                lead.stage_updated_at = datetime.utcnow()
                StageHistory(
                    lead=lead,
                    from_stage=old_status,
                    to_stage=new_status,
                    changed_by=request.user.username,
                ).save()

            lead.save()
            messages.success(request, 'Lead updated successfully.')
            return redirect('lead_detail', lead_id=str(lead.id))
    else:
        form = LeadUpdateForm(
            initial={
                'name': lead.name,
                'phone': lead.phone,
                'email': lead.email or '',
                'source': lead.source,
                'status': lead.status,
                'notes': lead.notes or '',
                'assigned_agent': str(lead.assigned_agent.id) if lead.assigned_agent else '',
            },
            agent_choices=agent_choices,
        )

    return render(request, 'leads/lead_detail.html', {
        'lead': lead,
        'form': form,
        'history': history,
        'followups': followups,
        'visits': visits,
        'pipeline_stages': PIPELINE_STAGES,
    })


def lead_capture(request):
    """Public-facing lead capture form — no login required."""
    if request.method == 'POST':
        form = LeadCaptureForm(request.POST)
        if form.is_valid():
            assigned_agent = assign_agent_round_robin()
            lead = Lead(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                source=form.cleaned_data['source'],
                notes=form.cleaned_data.get('notes', ''),
                assigned_agent=assigned_agent,
                status='new_lead',
            )
            lead.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'lead_id': str(lead.id)})
            return redirect('lead_capture_success')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = LeadCaptureForm()

    return render(request, 'leads/lead_capture.html', {'form': form})


def lead_capture_success(request):
    return render(request, 'leads/lead_capture_success.html')


@login_required
def pipeline_view(request):
    stages_data = []
    for stage_key, stage_label in PIPELINE_STAGES:
        stage_leads = Lead.objects.filter(status=stage_key)
        stages_data.append({
            'key': stage_key,
            'label': stage_label,
            'leads': stage_leads,
            'count': stage_leads.count(),
        })

    return render(request, 'leads/pipeline.html', {
        'stages_data': stages_data,
        'pipeline_stages': PIPELINE_STAGES,
    })


@login_required
def update_stage(request, lead_id):
    """Update lead stage — supports both AJAX JSON and plain form POST."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        lead = Lead.objects.get(id=lead_id)
    except Exception:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Lead not found'}, status=404)
        messages.error(request, 'Lead not found.')
        return redirect('pipeline_view')

    new_status = request.POST.get('status')
    valid_statuses = [s[0] for s in PIPELINE_STAGES]
    if new_status not in valid_statuses:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid status'}, status=400)
        messages.error(request, 'Invalid stage selected.')
        return redirect('pipeline_view')

    old_status = lead.status
    if old_status != new_status:
        StageHistory(
            lead=lead,
            from_stage=old_status,
            to_stage=new_status,
            changed_by=request.user.username,
        ).save()
        lead.status = new_status
        lead.stage_updated_at = datetime.utcnow()
        lead.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'new_status_label': PIPELINE_STAGE_LABELS.get(new_status, new_status),
        })

    messages.success(
        request,
        f'{lead.name} moved to {PIPELINE_STAGE_LABELS.get(new_status, new_status)}.'
    )
    return redirect('pipeline_view')


@login_required
def followup_list(request):
    followups = FollowUp.objects.filter(is_completed=False).order_by('due_at')
    return render(request, 'leads/followup_list.html', {'followups': followups})


@login_required
def complete_followup(request, followup_id):
    try:
        followup = FollowUp.objects.get(id=followup_id)
        followup.is_completed = True
        followup.completed_at = datetime.utcnow()
        followup.save()
        messages.success(request, 'Follow-up marked as completed.')
    except Exception:
        messages.error(request, 'Follow-up not found.')
    return redirect('followup_list')


@login_required
def delete_lead(request, lead_id):
    if request.method == 'POST':
        try:
            lead = Lead.objects.get(id=lead_id)
            lead.delete()
            messages.success(request, 'Lead deleted.')
        except Exception:
            messages.error(request, 'Lead not found.')
    return redirect('lead_list')
