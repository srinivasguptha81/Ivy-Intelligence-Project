from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Application, AutoFillLog, APPLICATION_STATUS
from apps.opportunities.models import Opportunity


def _get_profile(user):
    from apps.profiles.models import StudentProfile
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


@login_required
def apply(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, pk=opportunity_id, is_active=True)

    if Application.objects.filter(student=request.user, opportunity=opportunity).exists():
        messages.warning(request, "You have already applied for this opportunity.")
        return redirect('opportunity_detail', pk=opportunity_id)

    profile = _get_profile(request.user)

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        resume_used = profile.resume

        application = Application.objects.create(
            student=request.user,
            opportunity=opportunity,
            cover_letter=cover_letter,
            resume_used=resume_used,
            status='SUBMITTED',
        )

        if opportunity.source_url and request.POST.get('auto_apply') == '1':
            auto_result = attempt_auto_fill(application, opportunity)
            if auto_result['success']:
                application.auto_submitted = True
                application.save()
                messages.success(request, f"Auto-application submitted to {opportunity.get_university_display()}!")
            else:
                messages.info(request, f"Application recorded. Auto-fill was not possible: {auto_result['reason']}")
        else:
            messages.success(request, "Application submitted! Track it in your dashboard.")

        return redirect('my_applications')

    return render(request, 'applications/apply.html', {
        'opportunity': opportunity,
        'profile': profile,
    })


def attempt_auto_fill(application, opportunity):
    import requests as req
    from bs4 import BeautifulSoup

    result = {'success': False, 'reason': '', 'fields_detected': [], 'fields_filled': []}

    try:
        resp = req.get(opportunity.source_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        forms = soup.find_all('form')
        if not forms:
            result['reason'] = "No application form found on page"
            return result

        fields_detected = []
        for form in forms:
            for inp in form.find_all(['input', 'textarea', 'select']):
                name = inp.get('name', '') or inp.get('id', '')
                if name:
                    fields_detected.append(name)

        result['fields_detected'] = fields_detected
        profile = _get_profile(application.student)
        user = application.student
        field_map = {
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'university': profile.university,
        }
        fields_filled = [f for f in fields_detected if f.lower() in field_map]
        result['fields_filled'] = fields_filled

        AutoFillLog.objects.create(
            application=application,
            form_url=opportunity.source_url,
            fields_detected=fields_detected,
            fields_filled=fields_filled,
            success=len(fields_filled) > 0,
        )
        result['success'] = len(fields_filled) > 0
        if not result['success']:
            result['reason'] = "Form fields did not match profile data"

    except Exception as e:
        result['reason'] = str(e)

    return result


@login_required
def my_applications(request):
    applications = Application.objects.filter(
        student=request.user
    ).select_related('opportunity').order_by('-applied_at')

    status_counts = {
        'total': applications.count(),
        'submitted': applications.filter(status='SUBMITTED').count(),
        'shortlisted': applications.filter(status='SHORTLISTED').count(),
        'selected': applications.filter(status='SELECTED').count(),
    }

    return render(request, 'applications/my_applications.html', {
        'applications': applications,
        'status_counts': status_counts,
        'status_choices': APPLICATION_STATUS,
    })


@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, student=request.user)
    if application.status in ('PENDING', 'SUBMITTED'):
        application.status = 'WITHDRAWN'
        application.save()
        messages.success(request, "Application withdrawn.")
    else:
        messages.error(request, "Cannot withdraw this application in its current status.")
    return redirect('my_applications')
