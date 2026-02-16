from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Count
from .models import Election, Candidate, Vote
from accounts.models import User
from .utils import get_election_safely, clean_id_str
from bson import ObjectId
import json


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    total_elections = Election.objects.count()
    
    all_elections = Election.objects.all()
    active_elections = sum(1 for e in all_elections if e.is_ongoing())
    
    all_users = User.objects.all()
    total_students = sum(1 for u in all_users if not u.is_admin)

    total_votes = Vote.objects.count()
    
    recent_elections = Election.objects.all().order_by('-created_at')[:5]
    
    chart_labels = [e.title for e in recent_elections]
    chart_data = []
    for e in recent_elections:
        count = Vote.objects.filter(election_id=str(e._id)).count()
        chart_data.append(count)
    
    context = {
        'total_elections': total_elections,
        'active_elections': active_elections,
        'total_students': total_students,
        'total_votes': total_votes,
        'recent_elections': recent_elections,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'admin/dashboard.html', context)


@admin_required
def manage_elections(request):
    try:
        elections = list(Election.objects.all().order_by('-created_at'))
        for e in elections:
            try:
                e.vote_count = Vote.objects.filter(election_id=str(e._id)).count()
            except:
                e.vote_count = 0
    except Exception as e:
        messages.error(request, f"Error loading elections: {str(e)}")
        elections = []
    return render(request, 'admin/manage_elections.html', {'elections': elections})


@admin_required
def create_election(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not all([title, description, start_date, end_date]):
            messages.error(request, 'All fields are required.')
            return render(request, 'admin/create_election.html')
        
        try:
            aware_start = timezone.make_aware(parse_datetime(start_date))
            aware_end = timezone.make_aware(parse_datetime(end_date))
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date format.')
            return render(request, 'admin/create_election.html')
            
        election = Election(
            title=title,
            description=description,
            start_date=aware_start,
            end_date=aware_end,
            created_by=request.user.email,
            is_active=True
        )
        election.save()
        
        messages.success(request, f'Election "{title}" created successfully!')
        return redirect('manage_candidates', election_id=election._id)
    
    return render(request, 'admin/create_election.html')


@admin_required
def edit_election(request, election_id):
    election = get_election_safely(election_id)

    if not election:
        messages.error(request, "Election not found.")
        return redirect('manage_elections')
    
    if request.method == 'POST':
        try:
            aware_start = timezone.make_aware(parse_datetime(request.POST.get('start_date')))
            aware_end = timezone.make_aware(parse_datetime(request.POST.get('end_date')))
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date format.')
            return render(request, 'admin/edit_election.html', {'election': election})
            
        election.title = request.POST.get('title')
        election.description = request.POST.get('description')
        election.start_date = aware_start
        election.end_date = aware_end
        election.is_active = request.POST.get('is_active') == 'on'
        election.save()
        
        messages.success(request, 'Election updated successfully!')
        return redirect('manage_elections')
    
    return render(request, 'admin/edit_election.html', {'election': election})


@admin_required
def delete_election(request, election_id):
    if request.method != 'POST':
        return redirect('manage_elections')

    election = get_election_safely(election_id)
    if not election:
        messages.error(request, "Election not found.")
        return redirect('manage_elections')
    
    Candidate.objects.filter(election_id=str(election._id)).delete()
    Vote.objects.filter(election_id=str(election._id)).delete()
    
    election.delete()
    messages.success(request, 'Election deleted successfully!')
    return redirect('manage_elections')


@admin_required
def manage_candidates(request, election_id):
    election = get_election_safely(election_id)
    if not election:
        messages.error(request, "Election not found.")
        return redirect('manage_elections')

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            position = request.POST.get('position')
            image = request.FILES.get('image')

            if not all([name, description, position, image]):
                messages.error(request, "Name, Position, Description, and Photo are required.")
            else:
                election_ref_id = str(election._id) if hasattr(election, '_id') else str(election.pk)
                candidate = Candidate(
                    election_id=election_ref_id,
                    name=name,
                    description=description,
                    position=position,
                    image=image
                )
                candidate.save() 
                messages.success(request, "Candidate added successfully!")
                return redirect('manage_candidates', election_id=election_id)

        except Exception as e:
            messages.error(request, f"Error adding candidate: {str(e)}")

    candidates_data = []
    try:
        election_ref_id = str(election._id) if hasattr(election, '_id') else str(election.pk)
        raw_candidates = Candidate.objects.filter(election_id=election_ref_id)
        
        for c in raw_candidates:
            candidates_data.append({
                'pk': str(c.pk),
                'name': c.name,
                'position': c.position,
                'description': c.description,
                'image': c.image if c.image else None
            })
    except Exception as e:
        messages.error(request, f"Error loading list: {e}")

    context = {
        'election': election,
        'election_id_str': str(election._id) if hasattr(election, '_id') else str(election.pk),
        'candidates': candidates_data,
        'candidates_count': len(candidates_data)
    }
    return render(request, 'admin/manage_candidates.html', context)


@admin_required
def delete_candidate(request, candidate_id):
    try:
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        election_id = str(candidate.election_id)
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully!')
        return redirect('manage_candidates', election_id=election_id)
    except Exception as e:
        messages.error(request, f'Error deleting candidate: {str(e)}')
        return redirect('manage_elections')


@admin_required
def view_results(request, election_id):
    election = get_election_safely(election_id)
    if not election:
        messages.error(request, "Election not found.")
        return redirect('manage_elections')
        
    candidates = list(Candidate.objects.filter(election_id=str(election._id)))
    candidates_dict = {str(c._id): c for c in candidates}
    
    votes = list(Vote.objects.filter(election_id=str(election._id)).order_by('-voted_at'))
    total_votes = len(votes)
    
    results = []
    for candidate in candidates:
        vote_count = sum(1 for v in votes if v.candidate_id == str(candidate._id))
        percentage = round((vote_count / total_votes) * 100, 2) if total_votes > 0 else 0
            
        results.append({
            'candidate': candidate,
            'votes': vote_count,
            'percentage': percentage
        })
    
    results.sort(key=lambda x: x['votes'], reverse=True)
    
    chart_labels = [r['candidate'].name for r in results]
    chart_data = [r['votes'] for r in results]
    
    voter_emails = list(set(v.voter_email for v in votes if v.voter_email))
    users_dict = {u.email.lower(): u for u in User.objects.filter(email__in=voter_emails) if u.email}
            
    for vote in votes:
        v_email = (vote.voter_email or '').lower()
        vote.user_profile = users_dict.get(v_email)
        
        if not vote.user_profile:
            class MockProfile:
                full_name = 'Unknown Voter'
                student_id = 'N/A'
                profile_image = None
                profile_image_base64 = None
            vote.user_profile = MockProfile()
            
        candidate_obj = candidates_dict.get(vote.candidate_id)
        vote.candidate_name = candidate_obj.name if candidate_obj else "Unknown"
    
    context = {
        'election': election,
        'results': results,
        'total_votes': total_votes,
        'votes': votes,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data)
    }
    return render(request, 'admin/results.html', context)


@admin_required
def manage_students(request):
    query = request.GET.get('q', '')
    all_users = list(User.objects.all())
    students = [user for user in all_users if not user.is_admin]
    
    if query:
        query_lower = query.lower()
        students = [
            s for s in students 
            if query_lower in s.full_name.lower() 
            or query_lower in s.email.lower() 
            or query_lower in s.student_id.lower()
        ]
    else:
        students = sorted(students, key=lambda x: x.date_joined, reverse=True)
        
    return render(request, 'admin/manage_students.html', {'students': students, 'query': query})


@admin_required
def delete_student(request, user_id):
    if request.method == 'POST':
        try:
            student = User.objects.get(_id=ObjectId(user_id))
            if student.is_admin:
                messages.error(request, 'Admin accounts cannot be deleted.')
            else:
                Vote.objects.filter(voter_email=student.email).delete()
                name = student.full_name
                student.delete()
                messages.success(request, f'Student "{name}" and their data have been removed.')
        except User.DoesNotExist:
            messages.error(request, 'Student not found.')
            
    return redirect('manage_students')
