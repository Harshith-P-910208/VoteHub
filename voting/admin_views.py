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
from bson import ObjectId
from bson.errors import InvalidId
import json


def clean_id(id_str):
    """Clean MongoDB ObjectId string if it contains extra characters"""
    if not id_str:
        return None
    # Remove 'ObjectId(' and ')' if present
    s = str(id_str).replace("ObjectId('", "").replace("')", "").strip()
    return s


def admin_required(view_func):
    """Decorator to ensure user is admin"""
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
    # Get statistics
    # Get statistics using Python-side filtering to avoid Djongo boolean filter bugs
    total_elections = Election.objects.count()
    
    # Filter active elections in Python
    all_elections = Election.objects.all()
    active_elections = sum(1 for e in all_elections if e.is_ongoing())
    
    # Filter students in Python
    all_users = User.objects.all()
    total_students = sum(1 for u in all_users if not u.is_admin)

    total_votes = Vote.objects.count()
    
    # Get recent elections
    recent_elections = Election.objects.all().order_by('-created_at')[:5]
    
    # Prepare data for Chart.js
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
        # Add vote count to each election object (robust counting)
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
        
        # Parse dates to becoming timezone aware
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
        messages.error(request, f"Election not found (ID: {election_id})")
        return redirect('manage_elections')
    
    if request.method == 'POST':
        # Parse dates to becoming timezone aware
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
    
    context = {'election': election}
    return render(request, 'admin/edit_election.html', context)


@admin_required
def delete_election(request, election_id):
    if request.method != 'POST':
        return redirect('manage_elections')

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
        messages.error(request, f"Election not found (ID: {election_id})")
        return redirect('manage_elections')
    
    # Delete associated candidates and votes
    Candidate.objects.filter(election_id=str(election._id)).delete()
    Vote.objects.filter(election_id=str(election._id)).delete()
    
    election.delete()
    messages.success(request, 'Election deleted successfully!')
    return redirect('manage_elections')


@admin_required
def manage_candidates(request, election_id):
    try:
        # --- 1. SAFE ELECTION FETCHING ---
        from bson import ObjectId
        clean_eid = str(election_id).strip()
        election = None
        
        # Method 1: Direct PK
        try:
            election = Election.objects.filter(pk=clean_eid).first()
        except: pass

        # Method 2: ObjectId lookup (Most reliable for Djongo)
        if not election and len(clean_eid) == 24:
            try:
                election = Election.objects.filter(_id=ObjectId(clean_eid)).first()
            except: pass

        # Method 3: Direct ID string
        if not election:
            try:
                election = Election.objects.filter(id=clean_eid).first()
            except: pass

        # Method 4: List all and find (Backstop for weird query behavior)
        if not election:
            try:
                for e in Election.objects.all():
                    if str(getattr(e, '_id', e.pk)) == clean_eid:
                        election = e
                        break
            except: pass

        if not election:
            messages.error(request, f"Election not found (ID: {election_id})")
            return redirect('manage_elections')

        # --- 2. FAST CANDIDATE CREATION (POST) ---
        if request.method == 'POST':
            try:
                name = request.POST.get('name')
                description = request.POST.get('description')
                position = request.POST.get('position')
                image = request.FILES.get('image')

                if not all([name, description, position, image]):
                    messages.error(request, "Name, Position, Description, and Photo are required.")
                else:
                    # Step A: Create Candidate
                    election_ref_id = str(election._id) if hasattr(election, '_id') else str(election.pk)
                    
                    candidate = Candidate(
                        election_id=election_ref_id,
                        name=name,
                        description=description,
                        position=position,
                        image=image
                    )
                    candidate.save() 

                    if not messages.get_messages(request):
                        messages.success(request, "Candidate added successfully!")
                    
                    return redirect('manage_candidates', election_id=election_id)

            except Exception as e:
                error_msg = str(e)
                messages.error(request, f"Error adding candidate: {error_msg}")
                import traceback
                traceback.print_exc()

        # --- 3. SAFE CANDIDATE LISTING (Dicts to prevent Template Crashes) ---
        candidates_data = []
        try:
            election_ref_id = str(election._id) if hasattr(election, '_id') else str(election.pk)
            raw_candidates = Candidate.objects.filter(election_id=election_ref_id)
            
            for c in raw_candidates:
                try:
                    candidates_data.append({
                        'pk': str(c.pk), # Safe string ID
                        'name': c.name,
                        'position': c.position,
                        'description': c.description,
                        'image': c.image if c.image else None
                    })
                except:
                    continue
        except Exception as e:
            candidates_data = []
            messages.error(request, f"Error loading list: {e}")

        context = {
            'election': election,
            'election_id_str': str(election._id) if hasattr(election, '_id') else str(election.pk),
            'candidates': candidates_data, # Passing safe dicts
            'candidates_count': len(candidates_data)
        }
        return render(request, 'admin/manage_candidates.html', context)

    except Exception as fatal_error:
        # EMERGENCY CATCH: Return error as text to debug 500s
        import traceback
        return HttpResponse(f"CRITICAL ERROR IN VIEW:\n{traceback.format_exc()}", status=200)



@admin_required
def delete_candidate(request, candidate_id):
    try:
        clean_cid = clean_id(candidate_id)
        candidate = get_object_or_404(Candidate, pk=clean_cid)
        election_id = str(candidate.election_id)
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully!')
        return redirect('manage_candidates', election_id=election_id)
    except Exception as e:
        messages.error(request, f'Error deleting candidate: {str(e)}')
        return redirect('manage_elections')


@admin_required
def view_results(request, election_id):
    try:
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
            messages.error(request, f"Election not found (ID: {election_id})")
            return redirect('manage_elections')
        
        # Get all candidates for this election
        candidates = list(Candidate.objects.filter(election_id=str(election._id)))
        candidates_dict = {str(c._id): c for c in candidates}
        
        # Get all votes for this election (convert to list to avoid repeated queries)
        votes = list(Vote.objects.filter(election_id=str(election._id)).order_by('-voted_at'))
        total_votes = len(votes)
        
        # Calculate results per candidate
        results = []
        for candidate in candidates:
            # Filter votes in Python for reliability and speed
            vote_count = sum(1 for v in votes if v.candidate_id == str(candidate._id))
            
            percentage = 0
            if total_votes > 0:
                percentage = round((vote_count / total_votes) * 100, 2)
                
            results.append({
                'candidate': candidate,
                'votes': vote_count,
                'percentage': percentage
            })
        
        # Sort results by vote count descending
        results.sort(key=lambda x: x['votes'], reverse=True)
        
        # Prepare chart data (JSON safe)
        chart_labels = [r['candidate'].name for r in results]
        chart_data = [r['votes'] for r in results]
        
        # Fetch user profiles for the voter log
        voter_emails = list(set(v.voter_email for v in votes if v.voter_email))
        users = User.objects.filter(email__in=voter_emails)
        users_dict = {}
        for u in users:
            if u.email:
                users_dict[u.email.lower()] = u
                
        # Enrich vote objects for the audit log
        for vote in votes:
            # Match user profile
            v_email = (vote.voter_email or '').lower()
            profile = users_dict.get(v_email)
            
            if profile:
                vote.user_profile = profile
            else:
                # Robust fallback for missing profiles
                class MockProfile:
                    full_name = 'Unknown Voter'
                    student_id = 'N/A'
                    profile_image = None
                    profile_image_base64 = None
                vote.user_profile = MockProfile()
                
            # Match candidate name
            c = candidates_dict.get(vote.candidate_id)
            vote.candidate_name = c.name if c else "Unknown"
        
        context = {
            'election': election,
            'results': results,
            'total_votes': total_votes,
            'votes': votes,
            'chart_labels_json': json.dumps(chart_labels),
            'chart_data_json': json.dumps(chart_data)
        }
        return render(request, 'admin/results.html', context)
        
    except Exception as e:
        messages.error(request, f'Result Page Error: {str(e)}')
        return redirect('admin_dashboard')


@admin_required
def manage_students(request):
    """View to list and search students"""
    query = request.GET.get('q', '')
    
    # Get all users first (Djongo compatible)
    all_users = list(User.objects.all())
    
    # Filter non-admin users in Python
    students = [user for user in all_users if not user.is_admin]
    
    if query:
        # Search by name, email, or student_id
        query_lower = query.lower()
        students = [
            s for s in students 
            if query_lower in s.full_name.lower() 
            or query_lower in s.email.lower() 
            or query_lower in s.student_id.lower()
        ]
    else:
        # Sort by date_joined (newest first)
        students = sorted(students, key=lambda x: x.date_joined, reverse=True)
        
    context = {
        'students': students,
        'query': query
    }
    return render(request, 'admin/manage_students.html', context)


@admin_required
def delete_student(request, user_id):
    """Delete a student and their votes"""
    if request.method == 'POST':
        try:
            clean_uid = clean_id(user_id)
            student = User.objects.get(_id=ObjectId(clean_uid))
            
            # Prevent deleting admins (double check)
            if student.is_admin:
                messages.error(request, 'Cannot delete admin accounts from here.')
                return redirect('manage_students')
                
            # Delete associated votes
            Vote.objects.filter(voter_email=student.email).delete()
            
            # Delete student
            name = student.full_name
            student.delete()
            
            messages.success(request, f'Student "{name}" and their votes have been deleted.')
        except User.DoesNotExist:
            messages.error(request, 'Student not found.')
            
    return redirect('manage_students')
