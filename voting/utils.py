from .models import Election
from bson import ObjectId

def get_election_safely(id_str):
    """
    Robustly fetch an election object by its ID, handling different 
    possible ID formats from MongoDB/Djongo.
    """
    if not id_str:
        return None
        
    clean_id = str(id_str).strip()
    
    # Attempt direct lookup
    try:
        election = Election.objects.filter(pk=clean_id).first()
        if election:
            return election
    except:
        pass
        
    # Attempt ObjectId lookup if valid format
    if len(clean_id) == 24:
        try:
            election = Election.objects.filter(_id=ObjectId(clean_id)).first()
            if election:
                return election
        except:
            pass
            
    # Fallback: List scan (last resort)
    try:
        for e in Election.objects.all():
            if str(getattr(e, '_id', e.pk)) == clean_id:
                return e
    except:
        pass
        
    return None

def clean_id_str(id_obj):
    """Helper to get a clean string ID from a MongoDB field"""
    if not id_obj:
        return ""
    return str(id_obj).replace("ObjectId('", "").replace("')", "").strip()
