from django.shortcuts import render, redirect, get_object_or_404
from .models import Invitation, Person, Assignment
from .forms import InvitationForm, PersonForm, AssignmentForm, BaseAssignmentFormSet
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# Invitations List & Add

def invitations_list(request):
    invitations = Invitation.objects.all().order_by('-created_at')
    return render(request, 'invitations/invitations_list.html', {'invitations': invitations})

def add_invitation(request):
    if request.method == 'POST':
        form = InvitationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invitation added successfully!')
            return redirect('invitations_list')
    else:
        form = InvitationForm()
    return render(request, 'invitations/add_invitation.html', {'form': form})

# Assigning Persons List & Add

def persons_list(request):
    persons = Person.objects.all().order_by('name')
    return render(request, 'invitations/persons_list.html', {'persons': persons})

def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Person added successfully!')
            return redirect('persons_list')
    else:
        form = PersonForm()
    return render(request, 'invitations/add_person.html', {'form': form})

def assign_persons(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    persons = Person.objects.all()
    filter_assembly = request.GET.get('assembly', '')
    filter_mandal = request.GET.get('mandal', '')
    filter_area = request.GET.get('area', '')

    # Filtering
    if filter_assembly:
        persons = persons.filter(assembly=filter_assembly)
    if filter_mandal:
        persons = persons.filter(mandal=filter_mandal)
    if filter_area:
        persons = persons.filter(area=filter_area)

    if request.method == 'POST':
        selected_person_ids = request.POST.getlist('person_ids')
        gift_handler_id = request.POST.get('gift_handler')
        # Remove previous assignments
        Assignment.objects.filter(invitation=invitation).delete()
        for pid in selected_person_ids:
            Assignment.objects.create(
                invitation=invitation,
                person_id=pid,
                is_gift_handler=(str(pid) == gift_handler_id)
            )
        messages.success(request, 'Persons assigned successfully!')
        return redirect('invitation_detail', invitation_id=invitation.id)

    # For filter dropdowns
    assemblies = Person.objects.values_list('assembly', flat=True).distinct()
    mandals = Person.objects.values_list('mandal', flat=True).distinct()
    areas = Person.objects.values_list('area', flat=True).distinct()

    # Pre-select assigned persons
    assigned_ids = set(invitation.assignments.values_list('person_id', flat=True))
    gift_handler = invitation.assignments.filter(is_gift_handler=True).first()
    gift_handler_id = gift_handler.person_id if gift_handler else None

    return render(request, 'invitations/assign_persons.html', {
        'invitation': invitation,
        'persons': persons,
        'assemblies': assemblies,
        'mandals': mandals,
        'areas': areas,
        'filter_assembly': filter_assembly,
        'filter_mandal': filter_mandal,
        'filter_area': filter_area,
        'assigned_ids': assigned_ids,
        'gift_handler_id': gift_handler_id,
    })

def assign_persons_view(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    # Assuming you have an AssignmentForm and possibly a formset for multiple persons
    # from your forms.py
    from django.forms import inlineformset_factory

    AssignmentFormSet = inlineformset_factory(Invitation, Assignment, form=AssignmentForm, formset=BaseAssignmentFormSet, extra=1)

    if request.method == 'POST':
        formset = AssignmentFormSet(request.POST, instance=invitation)
        if formset.is_valid():
            formset.save()
            # Handle success - maybe return a JSON response
            # For now, let's just return a success indicator
            return JsonResponse({'status': 'success', 'message': 'Assignments saved successfully.'})
        else:
            # Handle form errors - return errors as JSON
            return JsonResponse({'status': 'error', 'errors': formset.errors}, status=400)

    # For GET request (AJAX to fetch form)
    formset = AssignmentFormSet(instance=invitation)
    context = {
        'invitation': invitation,
        'formset': formset,
    }
    # Render just the formset part
    return render(request, 'invitations/includes/assignment_form.html', context)

def ajax_assign_persons(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    persons = Person.objects.all().order_by('name') # Fetch all persons
    
    if request.method == 'POST':
        # Process the AJAX POST request to save assignments
        selected_person_ids = request.POST.getlist('person_ids')
        gift_handler_id = request.POST.get('gift_handler_id')

        # Clear existing assignments for this invitation
        invitation.assignments.all().delete()

        # Create new assignments
        assignments_to_create = []
        for person_id in selected_person_ids:
            assignment = Assignment(invitation=invitation, person_id=person_id)
            if gift_handler_id and str(person_id) == gift_handler_id:
                assignment.is_gift_handler = True
            assignments_to_create.append(assignment)
        
        Assignment.objects.bulk_create(assignments_to_create)

        return JsonResponse({'status': 'success', 'message': 'Assignments saved successfully!'})

    # For AJAX GET request (render the person list for the modal)
    assigned_person_ids = set(invitation.assignments.values_list('person_id', flat=True))
    gift_handler = invitation.assignments.filter(is_gift_handler=True).first()
    gift_handler_id = gift_handler.person_id if gift_handler else None

    context = {
        'invitation': invitation,
        'persons': persons,
        'assigned_person_ids': assigned_person_ids,
        'gift_handler_id': gift_handler_id,
    }
    return render(request, 'invitations/includes/ajax_assign_persons_modal.html', context)

def invitation_detail(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    assignments = invitation.assignments.select_related('person')
    return render(request, 'invitations/invitation_detail.html', {
        'invitation': invitation,
        'assignments': assignments,
    }) 