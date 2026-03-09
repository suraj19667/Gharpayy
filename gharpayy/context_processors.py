from leads.models import FollowUp


def crm_globals(request):
    """Inject CRM-wide variables into every template context."""
    if request.user.is_authenticated:
        try:
            count = FollowUp.objects.filter(is_completed=False).count()
        except Exception:
            count = 0
        return {'pending_followups_count': count}
    return {'pending_followups_count': 0}
