from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from visits.models import Visit, VISIT_OUTCOMES
from leads.models import Lead, PIPELINE_STAGES
from visits.forms import VisitForm, VisitOutcomeForm


@login_required
def visit_list(request):
    outcome_filter = request.GET.get('outcome', '')
    visits = Visit.objects.all()
    if outcome_filter:
        visits = visits.filter(outcome=outcome_filter)

    return render(request, 'visits/visit_list.html', {
        'visits': visits,
        'visit_outcomes': VISIT_OUTCOMES,
        'outcome_filter': outcome_filter,
    })


@login_required
def schedule_visit(request):
    lead_id = request.GET.get('lead_id', '')
    lead = None
    if lead_id:
        try:
            lead = Lead.objects.get(id=lead_id)
        except Exception:
            pass

    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            try:
                lead = Lead.objects.get(id=form.cleaned_data['lead_id'])
            except Exception:
                messages.error(request, 'Lead not found.')
                return redirect('visit_list')

            visit = Visit(
                lead=lead,
                property_name=form.cleaned_data['property_name'],
                property_address=form.cleaned_data.get('property_address', ''),
                visit_date=form.cleaned_data['visit_date'],
                visit_time=str(form.cleaned_data['visit_time']),
                notes=form.cleaned_data.get('notes', ''),
            )
            visit.save()

            # Update lead stage to visit_scheduled
            if lead.status not in ('visit_completed', 'booked'):
                lead.status = 'visit_scheduled'
                lead.stage_updated_at = datetime.utcnow()
                lead.save()

            messages.success(request, 'Visit scheduled successfully.')
            return redirect('visit_detail', visit_id=str(visit.id))
    else:
        initial = {'lead_id': lead_id}
        form = VisitForm(initial=initial)

    leads = Lead.objects.all().order_by('-created_at')
    return render(request, 'visits/schedule_visit.html', {
        'form': form,
        'lead': lead,
        'leads': leads,
    })


@login_required
def visit_detail(request, visit_id):
    try:
        visit = Visit.objects.get(id=visit_id)
    except Exception:
        messages.error(request, 'Visit not found.')
        return redirect('visit_list')

    outcome_form = VisitOutcomeForm(initial={
        'outcome': visit.outcome,
        'notes': visit.notes or '',
    })

    if request.method == 'POST':
        outcome_form = VisitOutcomeForm(request.POST)
        if outcome_form.is_valid():
            visit.outcome = outcome_form.cleaned_data['outcome']
            visit.notes = outcome_form.cleaned_data.get('notes', '')
            visit.save()

            # Update lead stage based on outcome
            lead = visit.lead
            if visit.outcome in ('completed', 'interested'):
                if lead.status == 'visit_scheduled':
                    lead.status = 'visit_completed'
                    lead.stage_updated_at = datetime.utcnow()
                    lead.save()
            elif visit.outcome == 'not_interested':
                lead.status = 'lost'
                lead.stage_updated_at = datetime.utcnow()
                lead.save()

            messages.success(request, 'Visit outcome updated.')
            return redirect('visit_detail', visit_id=str(visit.id))

    return render(request, 'visits/visit_detail.html', {
        'visit': visit,
        'outcome_form': outcome_form,
        'visit_outcomes': VISIT_OUTCOMES,
    })


@login_required
def delete_visit(request, visit_id):
    if request.method == 'POST':
        try:
            visit = Visit.objects.get(id=visit_id)
            visit.delete()
            messages.success(request, 'Visit deleted.')
        except Exception:
            messages.error(request, 'Visit not found.')
    return redirect('visit_list')
