from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Election, Candidate, Vote
from .utils import get_election_safely, clean_id_str
import base64
import json
from bson import ObjectId


def get_client_ip(request):
    """Utility to extract client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def student_dashboard(request):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    all_elections = Election.objects.all().order_by('-created_at')
    
    # Efficiently fetch IDs of elections user already participated in
    user_votes = Vote.objects.filter(voter_email=request.user.email).values_list('election_id', flat=True)
    voted_elections = [str(vid) for vid in user_votes]
    
    now = timezone.now()
    elections_data = []
    
    for election in all_elections:
        if not election.is_active:
            continue
            
        status = 'upcoming'
        can_vote = False
        
        if election.start_date <= now <= election.end_date:
            status = 'active'
            can_vote = True
        elif now > election.end_date:
            status = 'ended'
        
        e_id = clean_id_str(election._id)
        has_voted = e_id in voted_elections
        
        elections_data.append({
            'election': election,
            'election_id': e_id,
            'has_voted': has_voted,
            'status': status,
            'can_vote': can_vote and not has_voted
        })
    
    context = {
        'user': request.user,
        'elections': elections_data
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def vote_page(request, election_id):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    election = get_election_safely(election_id)
    if not election:
        messages.error(request, 'Election not found.')
        return redirect('student_dashboard')
    
    if not election.is_ongoing():
        messages.error(request, 'This election is not currently active.')
        return redirect('student_dashboard')
    
    e_id_str = clean_id_str(election._id)
    if Vote.objects.filter(election_id=e_id_str, voter_email=request.user.email).exists():
        messages.warning(request, 'You have already voted in this election.')
        return redirect('student_dashboard')
    
    candidates = Candidate.objects.filter(election_id=e_id_str)
    
    return render(request, 'student/vote.html', {'election': election, 'candidates': candidates})


@login_required
def submit_vote(request, election_id):
    if request.method != 'POST':
        return redirect('student_dashboard')
    
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    election = get_election_safely(election_id)
    if not election:
        messages.error(request, 'Election not found.')
        return redirect('student_dashboard')
    
    if not election.is_ongoing():
        messages.error(request, 'The election has concluded or is not yet active.')
        return redirect('student_dashboard')
    
    e_id_str = clean_id_str(election._id)
    if Vote.objects.filter(election_id=e_id_str, voter_email=request.user.email).exists():
        messages.warning(request, 'Multiple votes are not allowed.')
        return redirect('student_dashboard')
    
    candidate_id = request.POST.get('candidate_id')
    image_data = request.POST.get('voter_image')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    city = request.POST.get('city', '')
    country = request.POST.get('country', '')
    
    if not all([candidate_id, image_data, latitude, longitude]):
        messages.error(request, 'Permissions (Camera & Location) are required for casting a vote.')
        return redirect('vote_page', election_id=election_id)
    
    try:
        candidate = Candidate.objects.get(_id=ObjectId(candidate_id), election_id=e_id_str)
    except Candidate.DoesNotExist:
        messages.error(request, 'Invalid selection.')
        return redirect('vote_page', election_id=election_id)
    
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'{request.user.email}_{election_id}.{ext}')
    except:
        messages.error(request, 'Photo capture failed.')
        return redirect('vote_page', election_id=election_id)
    
    vote = Vote(
        election_id=e_id_str,
        candidate_id=clean_id_str(candidate._id),
        voter_email=request.user.email,
        voter_image=image_file,
        latitude=float(latitude),
        longitude=float(longitude),
        city=city,
        country=country,
        ip_address=get_client_ip(request)
    )
    vote.save()
    
    try:
        user = request.user
        user.latitude = float(latitude)
        user.longitude = float(longitude)
        user.city = city
        user.country = country
        user.last_location_update = timezone.now()
        user.save()
    except:
        pass # Optional update
    
    messages.success(request, 'Vote cast successfully!')
    return redirect('vote_confirmation', election_id=election_id)


@login_required
def vote_confirmation(request, election_id):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    election = get_election_safely(election_id)
    if not election:
        return redirect('student_dashboard')
    
    e_id_str = clean_id_str(election._id)
    try:
        vote = Vote.objects.get(election_id=e_id_str, voter_email=request.user.email)
        candidate = Candidate.objects.get(_id=ObjectId(vote.candidate_id))
    except (Vote.DoesNotExist, Candidate.DoesNotExist):
        return redirect('student_dashboard')
    
    return render(request, 'student/confirmation.html', {'election': election, 'candidate': candidate, 'vote': vote})
