from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Election, Candidate, Vote
import base64
import json
from bson import ObjectId
from bson.errors import InvalidId

def clean_id(id_str):
    """Clean MongoDB ObjectId string if it contains extra characters"""
    if not id_str:
        return None
    # Remove 'ObjectId(' and ')' if present
    s = str(id_str).replace("ObjectId('", "").replace("')", "").strip()
    return s


def get_client_ip(request):
    """Get client IP address"""
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
    
    # Get all elections from DB and process in Python to avoid Djongo query issues
    all_elections = Election.objects.all().order_by('-created_at')
    
    # Check which elections user has voted in (robust string matching)
    voted_elections = [str(vid) for vid in Vote.objects.filter(voter_email=request.user.email).values_list('election_id', flat=True)]
    
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
        
        elections_data.append({
            'election': election,
            'election_id': str(election._id),  # Add election_id as string for template
            'has_voted': str(election._id) in voted_elections,
            'status': status,
            'can_vote': can_vote and (str(election._id) not in voted_elections)
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
    
    # --- SAFE ELECTION FETCHING ---
    from bson import ObjectId
    clean_eid = str(election_id).strip()
    election = None
    
    # Method 1: Direct PK
    try:
        election = Election.objects.filter(pk=clean_eid).first()
    except: pass

    # Method 2: ObjectId lookup
    if not election and len(clean_eid) == 24:
        try:
            election = Election.objects.filter(_id=ObjectId(clean_eid)).first()
        except: pass

    # Method 3: List find
    if not election:
        try:
            for e in Election.objects.all():
                if str(getattr(e, '_id', e.pk)) == clean_eid:
                    election = e
                    break
        except: pass

    if not election:
        messages.error(request, 'Election not found.')
        return redirect('student_dashboard')
    
    # Check if election is ongoing
    if not election.is_ongoing():
        messages.error(request, 'This election is not currently active.')
        return redirect('student_dashboard')
    
    # Check if user has already voted
    if Vote.objects.filter(election_id=str(election._id), voter_email=request.user.email).exists():
        messages.warning(request, 'You have already voted in this election.')
        return redirect('student_dashboard')
    
    # Get candidates for this election
    candidates = Candidate.objects.filter(election_id=str(election._id))
    
    context = {
        'election': election,
        'candidates': candidates
    }
    return render(request, 'student/vote.html', context)


@login_required
def submit_vote(request, election_id):
    if request.method != 'POST':
        return redirect('student_dashboard')
    
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    # --- SAFE ELECTION FETCHING ---
    from bson import ObjectId
    clean_eid = str(election_id).strip()
    election = None
    
    # Method 1: Direct PK
    try:
        election = Election.objects.filter(pk=clean_eid).first()
    except: pass

    # Method 2: ObjectId lookup
    if not election and len(clean_eid) == 24:
        try:
            election = Election.objects.filter(_id=ObjectId(clean_eid)).first()
        except: pass

    # Method 3: List find
    if not election:
        try:
            for e in Election.objects.all():
                if str(getattr(e, '_id', e.pk)) == clean_eid:
                    election = e
                    break
        except: pass

    if not election:
        messages.error(request, 'Election not found.')
        return redirect('student_dashboard')
    
    # Check if election is ongoing
    if not election.is_ongoing():
        messages.error(request, 'This election is not currently active.')
        return redirect('student_dashboard')
    
    # Check if user has already voted
    if Vote.objects.filter(election_id=str(election._id), voter_email=request.user.email).exists():
        messages.warning(request, 'You have already voted in this election.')
        return redirect('student_dashboard')
    
    # Get form data
    candidate_id = request.POST.get('candidate_id')
    image_data = request.POST.get('voter_image')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    city = request.POST.get('city', '')
    country = request.POST.get('country', '')
    
    if not all([candidate_id, image_data, latitude, longitude]):
        messages.error(request, 'Missing required data. Please ensure camera and location permissions are granted.')
        return redirect('vote_page', election_id=election_id)
    
    # Verify candidate exists
    try:
        candidate = Candidate.objects.get(_id=ObjectId(candidate_id), election_id=str(election._id))
    except Candidate.DoesNotExist:
        messages.error(request, 'Invalid candidate selected.')
        return redirect('vote_page', election_id=election_id)
    
    # Process image
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'{request.user.email}_{election_id}.{ext}')
    except Exception as e:
        messages.error(request, 'Error processing image.')
        return redirect('vote_page', election_id=election_id)
    
    # Create vote
    vote = Vote(
        election_id=str(election._id),
        candidate_id=str(candidate._id),
        voter_email=request.user.email,
        voter_image=image_file,
        latitude=float(latitude),
        longitude=float(longitude),
        city=city,
        country=country,
        ip_address=get_client_ip(request)
    )
    vote.save()
    
    # Update user's location
    try:
        user = request.user
        user.latitude = float(latitude)
        user.longitude = float(longitude)
        user.city = city
        user.country = country
        user.last_location_update = timezone.now()
        user.save()
    except Exception as e:
        # Log error but don't fail the vote
        print(f"Error updating user location: {e}")
    
    messages.success(request, 'Your vote has been recorded successfully!')
    return redirect('vote_confirmation', election_id=election_id)



@login_required
def vote_confirmation(request, election_id):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    
    # --- SAFE ELECTION FETCHING ---
    from bson import ObjectId
    clean_eid = str(election_id).strip()
    election = None
    
    # Method 1: Direct PK
    try:
        election = Election.objects.filter(pk=clean_eid).first()
    except: pass

    # Method 2: ObjectId lookup
    if not election and len(clean_eid) == 24:
        try:
            election = Election.objects.filter(_id=ObjectId(clean_eid)).first()
        except: pass

    # Method 3: List find
    if not election:
        try:
            for e in Election.objects.all():
                if str(getattr(e, '_id', e.pk)) == clean_eid:
                    election = e
                    break
        except: pass

    if not election:
        messages.error(request, 'Election not found.')
        return redirect('student_dashboard')
    
    try:
        vote = Vote.objects.get(election_id=str(election._id), voter_email=request.user.email)
        candidate = Candidate.objects.get(_id=ObjectId(vote.candidate_id))
    except (Vote.DoesNotExist, Candidate.DoesNotExist):
        messages.error(request, 'Vote not found.')
        return redirect('student_dashboard')
    
    context = {
        'election': election,
        'candidate': candidate,
        'vote': vote
    }
    return render(request, 'student/confirmation.html', context)
