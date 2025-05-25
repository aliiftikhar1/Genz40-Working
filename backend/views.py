import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, PostCommunity, PostCommunityJoiners, PostPackageDetail, PostPackageFeature, PostPart, PostCharging, PostPaint, PostPayment, PostSubscribers
from .forms import CustomPasswordResetForm, CustomPasswordResetConfirmForm, PostPackageDetailForm, PostPackageFeatureForm, PostPartForm, PostChargingForm, PostPaintForm, \
    ImageModelForm
from .forms import RegisterForm, PostPackageForm, PostNavItemForm
from .models import PostPackage, PostNavItem,CarConfiguration,ReservationFeaturesPayment, ReservationNewFeatures
from .models import  DynamicPackages, FeaturesSection, PackageFeatureRoller, PackageFeatureRollerPlus, PackageFeatureBuilder
import string
import random
from common.utils import get_client_ip, send_custom_email
import requests
from decimal import Decimal
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import BookedPackage
from .serializers import BookedPackageSerializer
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

def clean_price_value(value):
    if value is None or value == '':
        return None
    try:
        # Ensure we're working with a string without any currency symbols or commas
        clean_value = str(value).replace('$', '').replace(',', '')
        return Decimal(clean_value)
    except:
        raise ValueError(f"'{value}' is not a valid decimal number")

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class CustomSortableUpdateView(View):
    def post(self, request, *args, **kwargs):
        # Handle sorting update logic here
        # This is just an example, you'll need to implement the actual sorting logic
        return JsonResponse({'status': 'ok'})

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def get_country_info(request):
    ip = get_client_ip(request)
    return ip

def register(request):
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    form = RegisterForm()
    random_password = generate_random_password()
    context = {
            'country_code': country_code,
            'country_flag_url': country_flag_url,
            'random_password': random_password,
            'form': form
        }

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(random_password)
            user = form.save()
             # Create a new UserProfile record
            # PostCommunity.objects.create(user=user, name='GENZ40', description='community_description')  # Modify or add fields as necessary
            # login(request, user)

            # template_name = "email/welcome_email.html"
            # subject = request.POST.get('subject', 'Default Subject')
            # message = request.POST.get('message', 'No message provided.')
            # recipient_email = request.POST.get('email', 'arvind.blues@gmail.com')
            # context = {
            #     'user': user,
            #     'password': random_password
            # }
            # send_custom_email(
            #     template_name,
            #     subject=subject,
            #     message=context,
            #     recipient_list=[recipient_email],
            # )


            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()
        # # ip = get_country_info(request)
        # response = requests.get(f'https://ipinfo.io/{ip}/json')
        # data = response.json()
        # country_code = data.get('country')
        # # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
        # country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    return render(request, 'registration/register.html', context)


# def custom_login(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             print('--------user details', user)
#             return redirect('dashboard')
#         else:
#             messages.error(request, 'Invalid username or password')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    form_class = CustomPasswordResetForm
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm
    success_message = "Your password has been reset successfully. You can now log in with the new password."
    success_url = reverse_lazy('customer_login')


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_message = "Your password has been changed successfully."
    success_url = reverse_lazy('password_change_done')


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')


# @login_required
# def dashboard(request):
#     header = 'Dashboard'
#     if request.user.role == 'admin':
#         return render(request, "admin/dashboard.html", {'header': header })
#     else:
#         return render(request, "customer/dashboard.html", {'header': header })


@login_required
def navitem_list(request):
    nav_items = PostNavItem.objects.all().order_by('position')
    return render(request, 'admin/navbar/list.html', {'nav_items': nav_items})


@login_required
def navitem_add(request):
    if request.method == 'POST':
        form = PostNavItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Added successfully')
            return redirect('navitem_list')
    else:
        form = PostNavItemForm()
    return render(request, 'admin/navbar/form.html', {'form': form})


@login_required
def navitem_edit(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    if request.method == 'POST':
        form = PostNavItemForm(request.POST, instance=nav_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Updated successfully')
            return redirect('navitem_list')
    else:
        form = PostNavItemForm(instance=nav_item)
    return render(request, 'admin/navbar/form.html', {'form': form, 'content': nav_item.content})


@login_required
def navitem_activate(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    nav_item.is_active = True
    nav_item.save()
    messages.success(request, 'Activated successfully')
    return redirect('navitem_list')


@login_required
def navitem_deactivate(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    nav_item.is_active = False
    nav_item.save()
    messages.success(request, 'Deactivated successfully')
    return redirect('navitem_list')


@login_required
def upload_images(request):
    if request.method == 'POST':
        form = ImageModelForm(request.POST, request.FILES)
        # nav_id = form.data['nav_item']
        if form.is_valid():
            form.save()
            # nav_id = form.cleaned_data['nav_item']
            # for img in request.FILES.getlist('image'):
            # PostImage.objects.create(nav_item=nav_id , image=img)
            messages.success(request, 'Image uploaded successfully')
            return redirect('create_parent_and_images')
    else:
        form = ImageModelForm()
    return render(request, 'admin/navbar/add_images.html', {'form': form})

@login_required
def customer_list(request):
    header = 'Customers'
    cutomers = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'admin/customer/list.html', {'cutomers': cutomers,'header':header})


@login_required
def package_list(request):
    all_package_list = DynamicPackages.objects.all().order_by('position')
    context = {
    'packages': all_package_list,
    'package_types': DynamicPackages.PACKAGE_TYPES,
    'car_models': PostNavItem.objects.all()  # Or your car model queryset
}
    return render(request, 'admin/package/list.html', context)

@login_required
def all_chats(request):
    return render(request, 'admin/chat/index.html')

# views.py
@login_required
def booked_package_list(request):
    all_booked_package_list = BookedPackage.objects.all().order_by('reservation_number')
    
    # Custom serialization for features
    def serialize_features(queryset):
        features = []
        for feature in queryset:
            options = []
            if feature.option1:
                options.append({
                    'value': 'option1',
                    'label': feature.option1,
                    'price': float(feature.option1_price)
                })
            if feature.option2:
                options.append({
                    'value': 'option2',
                    'label': feature.option2,
                    'price': float(feature.option2_price)
                })
                
            features.append({
                'id': str(feature.id),
                'title': feature.name,
                'type': feature.type,
                'price': float(feature.price),
                'options': options,
                'included': feature.included
            })
        return json.dumps(features)
    

    all_roller_features = serialize_features(PackageFeatureRoller.objects.all())
    all_roller_plus_features = serialize_features(PackageFeatureRollerPlus.objects.all())
    all_builder_features = serialize_features(PackageFeatureBuilder.objects.all())
    
    nav_items = PostNavItem.objects.all()
    return render(request, 'admin/booked_package/list.html', {
        'booked_packages': all_booked_package_list,
        'nav_items': nav_items,
        'all_roller_features': all_roller_features,
        'all_roller_plus_features': all_roller_plus_features,
        'all_builder_features': all_builder_features,
    })

# @login_required
# def package_add(request):
#     if request.method == 'POST':
#         form = PostPackageForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Package added successfully')
#             return redirect('package_list')
#     else:
#         form = PostPackageForm()
#     return render(request, 'admin/package/form.html', {'form': form})


csrf_exempt  # Only if you're having CSRF issues - better to properly handle CSRF
@require_http_methods(["POST"])
def package_add(request):
    try:
        data = request.POST
        # Validate required fields
        required_fields = ['name', 'package_type', 'car_model', 'description', 
                         'baseAmount', 'discountAmount', 'reserveAmount']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'{field} is required'}, status=400)
        
        # Create new package
        package = DynamicPackages(
            name=data['name'],
            package_type=data['package_type'],
            car_model_id=data['car_model'],
            description=data['description'],
            baseAmount=data['baseAmount'],
            discountAmount=data['discountAmount'],
            reserveAmount=data['reserveAmount']
        )
        package.save()
        
        return JsonResponse({'success': True, 'message': 'Package created successfully'})
    
    except PostNavItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid car model'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt  # Only if you're having CSRF issues - better to properly handle CSRF
@require_http_methods(["POST"])
def package_edit(request, pk):
    try:
        package = get_object_or_404(DynamicPackages, pk=pk)
        data = request.POST
        
        # Validate required fields
        required_fields = ['name', 'package_type', 'car_model', 'description', 
                         'baseAmount', 'discountAmount', 'reserveAmount']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'{field} is required'}, status=400)
        
        # Update package
        package.name = data['name']
        package.package_type = data['package_type']
        package.car_model_id = data['car_model']
        package.description = data['description']
        package.baseAmount = data['baseAmount']
        package.discountAmount = data['discountAmount']
        package.reserveAmount = data['reserveAmount']
        package.save()
        
        return JsonResponse({'success': True, 'message': 'Package updated successfully'})
    
    except PostNavItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid car model'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt  # Only if you're having CSRF issues - better to properly handle CSRF
@require_http_methods(["POST"])
def package_delete(request, pk):
    try:
        package = get_object_or_404(DynamicPackages, pk=pk)
        package.delete()
        return JsonResponse({'success': True, 'message': 'Package deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# @login_required
# def package_edit(request, pk):
#     package = get_object_or_404(PostPackage, pk=pk)
#     if request.method == 'POST':
#         form = PostPackageForm(request.POST, request.FILES, instance=package)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Package updated successfully')
#             return redirect('package_list')
#     else:
#         form = PostPackageForm(instance=package)
#     return render(request, 'admin/package/form.html', {'form': form, 'description': package.description})


# @login_required
# def package_activate(request, pk):
#     package = get_object_or_404(PostPackage, pk=pk)
#     package.is_active = True
#     package.save()
#     messages.success(request, 'Activated successfully')
#     return redirect('package_list')


# @login_required
# def package_deactivate(request, pk):
#     package = get_object_or_404(PostPackage, pk=pk)
#     package.is_active = False
#     package.save()
#     messages.success(request, 'Deactivated successfully')
#     return redirect('package_list')


@login_required
def packages(request):
    header = 'Packages'
    return render(request, "admin/package/list.html", {'header': header, })


def create_or_edit_item(request, model, form_class, template_name, pk=None):
    if pk:
        instance = get_object_or_404(model, pk=pk)
    else:
        instance = None

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('item_list')  # Change to your desired success URL
    else:
        form = form_class(instance=instance)

    return render(request, template_name, {'form': form})


def toggle_active_status(request, model, pk):
    item = get_object_or_404(model, pk=pk)
    item.is_active = not item.is_active
    item.save()
    return redirect('item_list')  # Change to your desired success URL


# Specific views for each model
def create_or_edit_post_package_detail(request, pk=None):
    return create_or_edit_item(request, PostPackageDetail, PostPackageDetailForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_package_feature(request, pk=None):
    return create_or_edit_item(request, PostPackageFeature, PostPackageFeatureForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_part(request, pk=None):
    return create_or_edit_item(request, PostPart, PostPartForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_charging(request, pk=None):
    return create_or_edit_item(request, PostCharging, PostChargingForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_paint(request, pk=None):
    return create_or_edit_item(request, PostPaint, PostPaintForm, 'admin/package/common_form.html', pk)


def toggle_post_package_detail(request, pk):
    return toggle_active_status(request, PostPackageDetail, pk)


def toggle_post_package_feature(request, pk):
    return toggle_active_status(request, PostPackageFeature, pk)


def toggle_post_part(request, pk):
    return toggle_active_status(request, PostPart, pk)


def toggle_post_charging(request, pk):
    return toggle_active_status(request, PostCharging, pk)


def toggle_post_paint(request, pk):
    return toggle_active_status(request, PostPaint, pk)


def all_package_details(request, pk):
    package = PostPackage.objects.get(id=pk)
    package_details = PostPackageDetail.objects.filter(package=str(package.id))
    # package_features = PostPackageFeature.objects.all()
    # parts = PostPart.objects.all()
    # charging = PostCharging.objects.all()
    # paints = PostPaint.objects.all()

    context = {
        'package': package,
        'package_details': package_details,
        'package_features': 'package_features',
        'parts': 'parts',
        'charging': 'charging',
        'paints': 'paints'
    }
    return render(request, 'admin/package/details.html', context)

@login_required
def reserved_car_list(request):
    all_rn_numbers = BookedPackage.objects.values_list('reservation_number', flat=True).distinct()
    payments = PostPayment.objects.filter(status='succeeded').order_by('-created_at')
    return render(request, 'admin/reserved_cars/list.html', {'payments': payments, 'all_rn_numbers': all_rn_numbers})

@login_required
def add_payment(request):
    all_rn_numbers = BookedPackage.objects.values_list('reservation_number', flat=True).distinct()
    
    if request.method == 'POST':
        try:
            rn_number = request.POST.get('rn_number')
            booked_package = BookedPackage.objects.get(reservation_number=rn_number)

            remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

            initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            balance_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))

            payment_build_type = request.POST.get('regarding') 
            payment_amount = request.POST.get('amount')
            if payment_build_type == 'initial_payment' and Decimal(payment_amount) != Decimal(initial_payment):
                messages.error(request, f'Initial payment amount should be {initial_payment}')
                return redirect('add_payment')
            elif payment_build_type == 'midway_payment' and Decimal(payment_amount) != Decimal(midway_payment):
                messages.error(request, f'Midway payment amount should be {midway_payment}')
                return redirect('add_payment')
            elif payment_build_type == 'final_payment' and Decimal(payment_amount) != Decimal(balance_payment):
                messages.error(request, f'Final payment amount should be {balance_payment}')
                return redirect('add_payment')

            booked_package.build_status = 'payment_done'
            booked_package.save()
            
            payment = PostPayment.objects.create(
                user=request.user,
                rn_number=booked_package,
                stripe_payment_id=request.POST.get('stripe_payment_id', ''),
                regarding=request.POST.get('regarding'),
                package_name=booked_package.title,
                type=request.POST.get('type'),
                amount=request.POST.get('amount'),
                currency=request.POST.get('currency'),
                status=request.POST.get('status'),
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            messages.success(request, 'Payment added successfully!')
            return redirect('reserved_car_list')
        except BookedPackage.DoesNotExist:
            messages.error(request, 'Invalid RN Number')
        except Exception as e:
            messages.error(request, f'Error adding payment: {str(e)}')
    
    return render(request, 'admin/reserved_cars/addPayment.html', {'all_rn_numbers': all_rn_numbers})

# Feature Payments COde Started

@login_required
def reservation_new_features(request):
    all_rn_numbers = BookedPackage.objects.values_list('reservation_number', flat=True).distinct()
    
    # Start with all pending features
    all_features = ReservationNewFeatures.objects.all().order_by('-status')
    
    # Apply reservation number filter if provided
    rn_filter = request.GET.get('rn_filter')
    if rn_filter:
        all_features = all_features.filter(booked_package__reservation_number=rn_filter)
    
    return render(request, 'admin/feature_payments/Features.html', {
        'all_features': all_features,
        'all_rn_numbers': all_rn_numbers
    })

@login_required
def feature_payment(request):
    all_rn_numbers = BookedPackage.objects.values_list('reservation_number', flat=True).distinct()
    payments = ReservationFeaturesPayment.objects.filter(payment_status='completed').order_by('-created_at')
    return render(request, 'admin/feature_payments/list.html', {'payments': payments, 'all_rn_numbers': all_rn_numbers})

@login_required
def add_feature_payment(request):
    all_rn_numbers = BookedPackage.objects.values_list('reservation_number', flat=True).distinct()
    
    # Initialize variables
    booked_package = None
    filtered_features = ReservationNewFeatures.objects.none()
    
    if request.method == 'GET':
        # Handle filtering based on GET parameters
        rn_number = request.GET.get('rn_number')
        feature_id = request.GET.get('feature_id')
        
        if rn_number:
            try:
                booked_package = BookedPackage.objects.get(reservation_number=rn_number)
                filtered_features = ReservationNewFeatures.objects.filter(
                    booked_package=booked_package,
                    status='pending'
                )
                
                if feature_id:
                    try:
                        selected_feature = ReservationNewFeatures.objects.get(
                            id=feature_id,
                            booked_package=booked_package
                        )
                        # You could add more context about the selected feature here
                    except ReservationNewFeatures.DoesNotExist:
                        messages.error(request, 'Invalid feature selected')
            except BookedPackage.DoesNotExist:
                messages.error(request, 'Invalid reservation number')
    
    if request.method == 'POST':
        try:
            feature_id = request.POST.get('reservation_feature')
            reservation_feature = ReservationNewFeatures.objects.get(id=feature_id)
            
            # Create the payment object from form data
            payment = ReservationFeaturesPayment.objects.create(
                reservation_feature=reservation_feature,
                amount=Decimal(request.POST.get('amount')),
                payment_date=request.POST.get('payment_date') or timezone.now(),
                payment_status=request.POST.get('payment_status'),
                payment_method=request.POST.get('payment_method'),
                transaction_id=request.POST.get('transaction_id', ''),
                payment_notes=request.POST.get('payment_notes', '')
            )
            
            # If payment is completed, update the feature status
            if payment.is_completed:
                reservation_feature.status = 'completed'
                reservation_feature.save()
                
                if payment.booked_package:
                    booked_package = payment.booked_package
                    booked_package.build_status = 'payment_done'
                    booked_package.save()
            
            messages.success(request, 'Payment added successfully!')
            return redirect('feature_payment')
            
        except ReservationNewFeatures.DoesNotExist:
            messages.error(request, 'Invalid Reservation Feature')
        except Exception as e:
            messages.error(request, f'Error adding payment: {str(e)}')
    
    context = {
        'all_rn_numbers': all_rn_numbers,
        'filtered_features': filtered_features,
        'booked_package': booked_package,
        'selected_rn': request.GET.get('rn_number', ''),
        'selected_feature': request.GET.get('feature_id', ''),
    }
    return render(request, 'admin/feature_payments/addPayment.html', context)

# Feature Payment Code Ends

@login_required
def community_member_list(request):
    header = 'Community Members'
    members = PostCommunityJoiners.objects.all().order_by('-created_at')
    return render(request, 'admin/community_members.html', {'members': members,'header':header})

@login_required
def subscriber_list(request):
    header = 'Subscribers'
    subscribers = PostSubscribers.objects.all().order_by('-created_at')
    return render(request, 'admin/subscribers.html', {'subscribers': subscribers,'header':header})







# car configurator page
@login_required
def save_car_configuration(request):
    """
    Save the car configuration from the form submission
    """
    if request.method == 'POST':
        try:
            # Get the car model
            slug = request.POST.get('car_slug')
            car_model_id = request.POST.get('car_model')
            # print("car model id is: ", car_model_id, "slug is: ", slug)
            car_model = get_object_or_404(PostNavItem, id=car_model_id)

            print("car model is: ", car_model.id)
            totalPrice = request.POST.get('total_price')

            print("TOtal price is: ", request.POST.get('total_price'))
            
            # Create a new configuration or update if exists
            config, created = CarConfiguration.objects.get_or_create(
                user=request.user,
                car_model=car_model,
                is_saved=True,
                defaults={
                    # Exterior options
                    'exterior_color': request.POST.get('exterior_color'),
                    'wheel_type': request.POST.get('wheel_type'),
                    'wheel_color': request.POST.get('wheel_color'),
                    'grille_style': request.POST.get('grille_style'),
                    'roof_type': request.POST.get('roof_type'),
                    'mirror_style': request.POST.get('mirror_style'),
                    'lighting_package': request.POST.get('lighting_package'),
                    'decals': request.POST.get('decals'),
                    
                    # Interior options
                    'upholstery_material': request.POST.get('upholstery_material'),
                    'interior_color': request.POST.get('interior_color'),
                    'seat_type': request.POST.get('seat_type'),
                    'dashboard_trim': request.POST.get('dashboard_trim'),
                    'steering_wheel': request.POST.get('steering_wheel'),
                    
                    # Performance options
                    'engine_type': request.POST.get('engine_type'),
                    'transmission': request.POST.get('transmission'),
                    'drivetrain': request.POST.get('drivetrain'),
                    'suspension': request.POST.get('suspension'),
                    'exhaust_system': request.POST.get('exhaust_system'),
                    
                    # Technology options
                    'infotainment_system': request.POST.get('infotainment_system'),
                    'sound_system': request.POST.get('sound_system'),
                    'heads_up_display': request.POST.get('heads_up_display') == 'true',
                    'connectivity_package': request.POST.get('connectivity_package'),
                    
                    # Safety options
                    'autonomous_driving_level': request.POST.get('autonomous_driving_level'),
                    'parking_assist': request.POST.get('parking_assist') == 'true',
                    'blind_spot_monitoring': request.POST.get('blind_spot_monitoring') == 'true',
                    'night_vision': request.POST.get('night_vision') == 'true',
                    
                    # Package options
                    'luxury_package': request.POST.get('luxury_package') == 'true',
                    'sport_package': request.POST.get('sport_package') == 'true',
                    'winter_package': request.POST.get('winter_package') == 'true',
                    'offroad_package': request.POST.get('offroad_package') == 'true',
                    'towing_hitch': request.POST.get('towing_hitch') == 'true',
                    'roof_rack': request.POST.get('roof_rack') == 'true',
                    
                    # Price information
                    'exterior_price': request.POST.get('exterior_price'),
                    'interior_price': request.POST.get('interior_price'),
                    'performance_price': request.POST.get('performance_price'),
                    'tech_price': request.POST.get('tech_price'),
                    'package_price': request.POST.get('package_price'),
                    'base_price': request.POST.get('base_price'),
                    'total_price': request.POST.get('total_price'),
                }
            )
            
            # If configuration already existed, update its fields
            if not created:
                # Update exterior options
                config.exterior_color = request.POST.get('exterior_color')
                config.wheel_type = request.POST.get('wheel_type')
                config.wheel_color = request.POST.get('wheel_color')
                config.grille_style = request.POST.get('grille_style')
                config.roof_type = request.POST.get('roof_type')
                config.mirror_style = request.POST.get('mirror_style')
                config.lighting_package = request.POST.get('lighting_package')
                config.decals = request.POST.get('decals')
                
                # Update interior options
                config.upholstery_material = request.POST.get('upholstery_material')
                config.interior_color = request.POST.get('interior_color')
                config.seat_type = request.POST.get('seat_type')
                config.dashboard_trim = request.POST.get('dashboard_trim')
                config.steering_wheel = request.POST.get('steering_wheel')
                
                # Update performance options
                config.engine_type = request.POST.get('engine_type')
                config.transmission = request.POST.get('transmission')
                config.drivetrain = request.POST.get('drivetrain')
                config.suspension = request.POST.get('suspension')
                config.exhaust_system = request.POST.get('exhaust_system')
                
                # Update technology options
                config.infotainment_system = request.POST.get('infotainment_system')
                config.sound_system = request.POST.get('sound_system')
                config.heads_up_display = request.POST.get('heads_up_display') == 'true'
                config.connectivity_package = request.POST.get('connectivity_package')
                
                # Update safety options
                config.autonomous_driving_level = request.POST.get('autonomous_driving_level')
                config.parking_assist = request.POST.get('parking_assist') == 'true'
                config.blind_spot_monitoring = request.POST.get('blind_spot_monitoring') == 'true'
                config.night_vision = request.POST.get('night_vision') == 'true'
                
                # Update package options
                config.luxury_package = request.POST.get('luxury_package') == 'true'
                config.sport_package = request.POST.get('sport_package') == 'true'
                config.winter_package = request.POST.get('winter_package') == 'true'
                config.offroad_package = request.POST.get('offroad_package') == 'true'
                config.towing_hitch = request.POST.get('towing_hitch') == 'true'
                config.roof_rack = request.POST.get('roof_rack') == 'true'
                
                # Update price information
                config.exterior_price = clean_price_value(request.POST.get('exterior_price'))
                config.interior_price = clean_price_value(request.POST.get('interior_price'))
                config.performance_price = clean_price_value(request.POST.get('performance_price'))
                config.tech_price =clean_price_value( request.POST.get('tech_price'))
                config.package_price = clean_price_value(request.POST.get('package_price'))
                config.base_price = clean_price_value(request.POST.get('base_price'))
                config.total_price = clean_price_value(totalPrice)
                
                config.save()
            
            messages.success(request, 'Your car configuration has been saved successfully!')
            return redirect('car_configuration_detail', config_id=config.id)
            # return redirect('view_configuration', config_id=config.id)
            
        except Exception as e:
            messages.error(request, f'Error saving configuration: {str(e)}')
            return redirect( 'car_configurator_slug',slug)
    
    # If not POST, redirect to car models
    return redirect('car_models')

def car_models(request):
    """
    Display available car models to configure
    """
    car_models = PostNavItem.objects.all()
    
    context = {
        'car_models': car_models
    }
    
    return render(request, 'public/car_models.html', context)

@login_required
def saved_configurations(request):
    """
    Display all saved configurations for the logged-in user
    """
    configurations = CarConfiguration.objects.filter(user=request.user, is_saved=True)
    
    context = {
        'configurations': configurations
    }
    
    return render(request, 'public/saved_configurations.html', context)

# @login_required
# def view_configuration(request, config_id):
#     """
#     View a specific saved configuration
#     """
#     configuration = get_object_or_404(CarConfiguration, id=config_id, user=request.user)
    
#     context = {
#         'config': configuration,
#         'items': configuration.car_model,
#         'amount_due': configuration.total_price,
        
#     }
    
#     return render(request, 'public/view_configuration.html', context)




# new configurations system


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_booked_packages(request):
    """
    Get all booked packages
    """
    packages = BookedPackage.objects.all()
    serializer = BookedPackageSerializer(packages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booked_package_by_id(request, pk):
    """
    Get a booked package by ID
    """
    print("****~~~~~****~~~~~GOOT ID",pk)
    try:
        package = BookedPackage.objects.get(pk=pk)
        serializer = BookedPackageSerializer(package)
        return Response(serializer.data)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booked_packages_by_user_id(request, user_id):
    """
    Get all booked packages for a specific user
    """
    packages = BookedPackage.objects.filter(user_id=user_id)
    serializer = BookedPackageSerializer(packages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_booked_package(request):
    """
    Create a new booked package
    """
    data = request.data.copy() 
    data['user'] = request.user.id
    data['package'] = data['package_id']
    print("The data for saving package is :",data)
    serializer = BookedPackageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_booked_package(request, pk):
    """
    Update an existing booked package
    """
    try:
        package = BookedPackage.objects.get(pk=pk)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = request.data
    print("Fetched Data : ", data)
    
    # Check for existing payments
    initial_payment_exists = PostPayment.objects.filter(
        rn_number=data['reservation_number'], 
        regarding='initial_payment'
    ).exists()
    
    mid_way_exists = PostPayment.objects.filter(
        rn_number=data['reservation_number'], 
        regarding='midway_payment'
    ).exists()
    
    final_balance_exists = PostPayment.objects.filter(
        rn_number=data['reservation_number'], 
        regarding='final_payment'
    ).exists()

    if initial_payment_exists and Decimal(data['initial_payment_percentage']) != Decimal(package.initial_payment_percentage):
        return Response(
            {"error": "Initial Payment Percentage can not be changed after payment."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if mid_way_exists and Decimal(data['midway_payment_percentage']) != Decimal(package.midway_payment_percentage):
        return Response(
            {"error": "Mid Way Payment Percentage can not be changed after payment."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if final_balance_exists and Decimal(data['final_payment_percentage']) != Decimal(package.final_payment_percentage):
        return Response(
            {"error": "Final Payment Percentage can not be changed after payment."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not initial_payment_exists and data['build_type'] in [ 'chassis_complete','midway_payment','final_payment', 'body_complete', 'assembly', 'built','quality_check', 'available_for_delivery']:
        return Response(
            {"error": "Reservation can not be proceeded next without initital payment"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not mid_way_exists and data['build_type'] in ['assembly', 'built', 'final_payment' , 'quality_check', 'available_for_delivery']:
        return Response(
            {"error": "Reservation can not be proceeded next without midway payment"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not final_balance_exists and data['build_type'] in ['quality_check', 'available_for_delivery']:
        return Response(
            {"error": "Reservation can not be proceeded next without final balance payment"},
            status=status.HTTP_400_BAD_REQUEST
        ) 

    
    # Check if cancellation is allowed based on payment status
    if (data['status'] == 'pending' or data['status'] == 'confirmed') and initial_payment_exists:
        return Response(
            {"error": "You cannot cancel the reservation because initial payment has been done."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if data['build_type'] in ['order_confirmed', 'chassis_complete', 'body_complete'] and mid_way_exists:
        return Response(
            {"error": "You cannot cancel the reservation because mid way payment has been done."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if data['build_type'] in ['order_confirmed', 'chassis_complete', 'body_complete', 'assembly', 'built'] and final_balance_exists:
        return Response(
            {"error": "You cannot cancel the reservation because final balance payment has been done."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    serializer = BookedPackageSerializer(package, data=data)
    if serializer.is_valid():
        serializer.save()
        newpackage = BookedPackage.objects.get(pk=pk)
        current_site = get_current_site(request)
        context = {
            'user': newpackage.user,
            'booked_package': newpackage,
            'message': "Your reservation has been promoted to "+ newpackage.build_type + " ( "+ newpackage.build_status + " ) " +"phase of build process.",
            'domain': current_site.domain,
            'reservation_number': newpackage.reservation_number,
        }

        # Render email template
        subject = 'Reservation Updates - GEN-Z 40'
        html_content = render_to_string('email/status_updation.html', context)
        plain_text = strip_tags(html_content)
        
        print("Subject:", subject, "HTML Content length:", len(html_content), "Plain Text length:", len(plain_text))
        
        send_mail(
            subject=subject,  
            message=plain_text,
            from_email=settings.EMAIL_FROM,
            recipient_list=[newpackage.user.email],  
            fail_silently=False,
            html_message=html_content
        )
    
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_booked_package(request, pk):
    """
    Delete a booked package
    """
    try:
        package = BookedPackage.objects.get(pk=pk)
        package.delete()
        return Response({"message": "Booked package deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django import forms
from .models import BookedPackage, BookedPackageImage

# Define build type choices manually
BUILD_TYPE_CHOICES = [
        ('order_confirmed', 'Order Confirmed'),
        ('initial_payment', 'Initial Payment'),
        ('chassis_complete', 'Chassis Complete'),
        ('body_complete', 'Body Complete'),
        ('midway_payment', 'Mid Way Payment'),
        ('assembly', 'Assembly'),
        ('built', 'Built'),
        ('final_payment', 'Final Payment'),
        ('quality_check', 'Quality Check'),
        ('available_for_delivery', 'Available For Delivery'),
]

# Manual form for image uploads
class PackageImageUploadForm(forms.Form):
    build_type = forms.ChoiceField(
        choices=BUILD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Build Stage'
    )
    images = forms.FileField(
        required=True,
        label='Images'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional: Add notes about these images'}),
        required=False,
        label='Description'
    )

    def clean_images(self):
        images = self.files.getlist('images')
        if not images:
            raise forms.ValidationError("At least one image is required.")
        for image in images:
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Only image files are allowed.")
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Each image must be less than 5MB.")
        return images

# Manual form for updating build type
class ImageBuildTypeForm(forms.ModelForm):
    class Meta:
        model = BookedPackageImage
        fields = ['build_type']
        widgets = {
            'build_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'build_type': 'Build Stage',
        }

    build_type = forms.ChoiceField(
        choices=BUILD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Build Stage'
    )

@login_required
def package_detail(request, package_id):
    """Display details of a booked package"""
    package = get_object_or_404(BookedPackage, id=package_id)
    images = BookedPackageImage.objects.filter(booked_package=package)
    context = {
        'package': package,
        'images': images,
        'build_types': BUILD_TYPE_CHOICES,
    }
    return render(request, 'admin/booked_package/PackageDetails.html', context)

@login_required
def upload_package_images(request, package_id):
    """Upload multiple images for a booked package"""
    package = get_object_or_404(BookedPackage, id=package_id)
    
    if request.user != package.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to upload images to this package.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PackageImageUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        
        if form.is_valid() and files:
            build_type = form.cleaned_data['build_type']
            description = form.cleaned_data['description']
            
            for image_file in files:
                BookedPackageImage.objects.create(
                    booked_package=package,
                    image=image_file,
                    build_type=build_type,
                    description=description
                )
            
            messages.success(request, f"{len(files)} image(s) uploaded successfully.")
            return redirect('package_detail', package_id=package.id)
    else:
        form = PackageImageUploadForm()
    
    context = {
        'package': package,
        'form': form,
        'build_types': BUILD_TYPE_CHOICES,
    }
    return render(request, 'admin/booked_package/UploadReservationImage.html', context)

@login_required
def delete_package_image(request, image_id):
    """Delete a specific package image"""
    image = get_object_or_404(BookedPackageImage, id=image_id)
    package = image.booked_package
    
    # Check if user has permission to delete
    if request.user != package.user and not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        messages.error(request, "You don't have permission to delete this image.")
        return redirect('package_detail', package_id=package.id)
    
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Delete the image file
        image.image.delete(save=False)
        # Delete the record
        image.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "Image deleted successfully.")
        return redirect('package_detail', package_id=package.id)
    
    return redirect('package_detail', package_id=package.id)

@login_required
def update_image_build_type(request, image_id):
    """Update the build type of a specific image"""
    image = get_object_or_404(BookedPackageImage, id=image_id)
    package = image.booked_package
    
    # Check if user has permission
    if request.user != package.user and not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        messages.error(request, "You don't have permission to update this image.")
        return redirect('package_detail', package_id=package.id)
    
    if request.method == 'POST':
        form = ImageBuildTypeForm(request.POST, instance=image)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, "Image build type updated successfully.")
            return redirect('package_detail', package_id=package.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ImageBuildTypeForm(instance=image)
    
    context = {
        'form': form,
        'image': image,
        'package': package,
    }
    return render(request, 'admin/booked_package/UploadReservationImage.html', context)



# For mobile application views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from .models import (
    PostLandingPageImages,
    PostNavItem,
    PostPackage,
    DynamicPackages,
    FeaturesSection,
    PackageFeatureRoller,
    PackageFeatureRollerPlus,
    PackageFeatureBuilder,
    BookedPackage,
    PostPayment
)
from .serializers import (
    LandingPageImageSerializer,
    NavItemSerializer,
    CarDetailSerializer,
    DynamicPackageSerializer,
    FeatureSectionSerializer,
    BookedPackageSerializer,
    PackageFeatureBuilderSerializer,
    PackageFeatureRollerSerializer,
    PackageFeatureRollerPlusSerializer

)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_landing_images(request):
    """API endpoint to get all landing page images"""
    images = PostLandingPageImages.objects.all().order_by('section')
    serializer = LandingPageImageSerializer(images, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_nav_items(request):
    """API endpoint to get all active navigation items"""
    items = PostNavItem.objects.filter(is_active=True).order_by('position')
    serializer = NavItemSerializer(items, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_car_details(request, slug):
    """API endpoint to get details for a specific car model"""
    try:
        car = PostNavItem.objects.get(slug=slug, is_active=True)
        # packages = car.details.filter(is_active=True).order_by('position')
        
        car_serializer = CarDetailSerializer(car)
        # package_serializer = PackageSerializer(packages, many=True)
        
        return Response({
            'success': True,
            'car': car_serializer.data,
            # 'packages': package_serializer.data
        })
    except PostNavItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Car model not found'
        }, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dynamic_packages(request, car_model_slug):
    """API endpoint to get dynamic packages for a car model"""
    try:
        car_model = PostNavItem.objects.get(slug=car_model_slug)
        packages = DynamicPackages.objects.filter(car_model=car_model).order_by('position')
        
        serializer = DynamicPackageSerializer(packages, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except PostNavItem.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Car model not found'
        }, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_feature_sections(request):
    """API endpoint to get all feature sections"""
    sections = FeaturesSection.objects.all().order_by('created_at')
    serializer = FeatureSectionSerializer(sections, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_features_by_type(request, feature_type, slug):
    """API endpoint to get features by type (roller, rollerplus, builder)"""
    try:
        feature = None
        serializer_class = None

        if feature_type == 'roller':
            if slug == 'Mark-I':
                feature = PackageFeatureRoller.objects.filter(in_mark_I=True)
            elif slug == 'Mark-II':
                feature = PackageFeatureRoller.objects.filter(in_mark_II=True)
            else:
                feature = PackageFeatureRoller.objects.filter(in_mark_IV=True)
            serializer_class = PackageFeatureRollerSerializer

        elif feature_type == 'builder':
            if slug == 'Mark-I':
                feature = PackageFeatureBuilder.objects.filter(in_mark_I=True)
            elif slug == 'Mark-II':
                feature = PackageFeatureBuilder.objects.filter(in_mark_II=True)
            else:
                feature = PackageFeatureBuilder.objects.filter(in_mark_IV=True)
            serializer_class = PackageFeatureBuilderSerializer

        elif feature_type == 'rollerplus':
            if slug == 'Mark-I':
                feature = PackageFeatureRollerPlus.objects.filter(in_mark_I=True)
            elif slug == 'Mark-II':
                feature = PackageFeatureRollerPlus.objects.filter(in_mark_II=True)
            else:
                feature = PackageFeatureRollerPlus.objects.filter(in_mark_IV=True)
            serializer_class = PackageFeatureRollerPlusSerializer

        else:
            return Response({
                'success': False,
                'message': 'Invalid feature type'
            }, status=400)

        # Serialize the data
        serializer = serializer_class(feature, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        }, status=200)

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_reservation_details(request, reservation_number):
    """API endpoint to get reservation details"""
    try:
        reservation = BookedPackage.objects.get(reservation_number=reservation_number)
        
        # Serialize the reservation data
        reservation_data = {
            'id': reservation.id,
            'reservation_number': reservation.reservation_number,
            'car_model': reservation.car_model.title,
            'package': reservation.title,
            'price': str(reservation.price),
            'status': reservation.status,
            'build_status': reservation.build_status,
            'created_at': reservation.created_at,
            'updated_at': reservation.updated_at,
        }
        
        # Get payments for this reservation
        payments = PostPayment.objects.filter(rn_number=reservation).order_by('-created_at')
        payments_data = [{
            'id': payment.id,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'regarding': payment.regarding,
            'created_at': payment.created_at
        } for payment in payments]
        
        return Response({
            'success': True,
            'reservation': reservation_data,
            'payments': payments_data
        })
    except BookedPackage.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Reservation not found'
        }, status=404)

# New API Views for Login and User Reservations
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@authentication_classes([])  # No session, no CSRF
@permission_classes([AllowAny])
def user_login(request):
    """API endpoint for user login with JWT Token"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=400)
            
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=401)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Protect with Bearer Token
def get_user_reservations(request):
    """API endpoint to get all reservations for the authenticated user"""
    try:
        user = request.user  # Get user from the Bearer token automatically
        reservations = BookedPackage.objects.filter(user=user).exclude(status='cancelled')
        serializer = BookedPackageSerializer(reservations, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)
    


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def user_logout(request):
#     """API endpoint to log out the user by blacklisting the refresh token."""
#     try:
#         # Get the refresh token from request
#         refresh_token = request.data.get("refresh_token")
        
#         if refresh_token is None:
#             return Response({
#                 "success": False,
#                 "message": "Refresh token is required for logout."
#             }, status=400)
        
#         token = RefreshToken(refresh_token)
#         token.blacklist()  # Blacklist the token (requires setup)
        
#         return Response({
#             "success": True,
#             "message": "Logout successful."
#         })
    
#     except Exception as e:
#         return Response({
#             "success": False,
#             "message": str(e)
#         }, status=500)