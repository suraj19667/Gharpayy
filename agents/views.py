from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from agents.models import Agent, RoundRobinState


class AgentForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agent Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'agent@gharpayy.com'})
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9999999999'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


def _agent_stats(agent):
    """Return a dict of stat values for one agent."""
    total = agent.total_leads_count()
    booked = agent.booked_count()
    active = agent.active_leads_count()
    rate = agent.conversion_rate()
    return {
        'agent': agent,
        'total': total,
        'active': active,
        'booked': booked,
        'rate': rate,
    }


@login_required
def agent_list(request):
    agents = Agent.objects.all()
    stats = [_agent_stats(a) for a in agents]
    # Round-robin state for display
    rr_state = RoundRobinState.get_or_create()
    active_agents = [a for a in agents if a.is_active]
    next_agent = None
    if active_agents:
        idx = rr_state.current_index % len(active_agents)
        next_agent = active_agents[idx].name
    return render(request, 'agents/agent_list.html', {
        'stats': stats,
        'next_agent': next_agent,
    })


@login_required
def agent_create(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            if Agent.objects(email=form.cleaned_data['email']).first():
                messages.error(request, 'An agent with this email already exists.')
            else:
                agent = Agent(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    is_active=form.cleaned_data.get('is_active', True),
                )
                agent.save()
                messages.success(request, f'Agent {agent.name} created.')
                return redirect('agent_list')
    else:
        form = AgentForm()

    return render(request, 'agents/agent_form.html', {'form': form, 'action': 'Create'})


@login_required
def agent_edit(request, agent_id):
    try:
        agent = Agent.objects.get(id=agent_id)
    except Exception:
        messages.error(request, 'Agent not found.')
        return redirect('agent_list')

    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            agent.name = form.cleaned_data['name']
            agent.email = form.cleaned_data['email']
            agent.phone = form.cleaned_data.get('phone', '')
            agent.is_active = form.cleaned_data.get('is_active', True)
            agent.save()
            messages.success(request, 'Agent updated.')
            return redirect('agent_list')
    else:
        form = AgentForm(initial={
            'name': agent.name,
            'email': agent.email,
            'phone': agent.phone or '',
            'is_active': agent.is_active,
        })

    return render(request, 'agents/agent_form.html', {
        'form': form,
        'agent': agent,
        'action': 'Edit',
    })


@login_required
def agent_delete(request, agent_id):
    if request.method == 'POST':
        try:
            agent = Agent.objects.get(id=agent_id)
            agent.delete()
            messages.success(request, 'Agent deleted.')
        except Exception:
            messages.error(request, 'Agent not found.')
    return redirect('agent_list')
