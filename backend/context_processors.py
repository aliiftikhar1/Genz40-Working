# myapp/context_processors.py
from .models import PostNavItem
from django.conf import settings
from django.contrib.auth.models import AnonymousUser



def nav_items(request):
    # Get only active parent items
    nav_items = PostNavItem.objects.filter(parent__isnull=True, is_active=True).order_by('position')
    for item in nav_items:
        # Assign active children to a new attribute
        item.active_children = item.get_active_children()
    return {'nav_items': nav_items}


# def nav_items(request):
#     return {
#         'nav_items': PostNavItem.objects.filter(parent__isnull=True, is_active=True).order_by('position')
#     }

def add_user_to_context(request):
    user_data = {}

    if request.user and isinstance(request.user, AnonymousUser):
        print("User is anonymous")
        user_data['is_authenticated'] = False
        user_data['user_id'] = None
    else:
        # print("------------------------------------User Looged In COntext Preprocessor------------------------------------")
        user_data['is_authenticated'] = True
        user_data['user_id'] = str(request.user.id)  # Ensure you convert the UUID to a string if necessary
        user_data['email'] = request.user.email
        user_data['first_name'] = request.user.first_name
        user_data['last_name'] = request.user.last_name
        first = request.user.first_name or ""
        last = request.user.last_name or ""
        full_name = f"{first} {last}".strip()
        user_data['full_name'] = full_name if full_name else None
        # user_data['full_name'] = request.user.first_name + ' '+ request.user.last_name
        user_data['is_delete'] = request.user.is_delete
        user_data['phone_number'] = request.user.phone_number
        user_data['is_email_verified'] = request.user.is_email_verified
        user_data['is_phone_number_verified'] = request.user.is_phone_number_verified
        user_data['zip_code'] = request.user.zip_code
        user_data['base_url'] = settings.BASE_URL
        user_data['role'] = request.user.role
    return {'user_data': user_data}