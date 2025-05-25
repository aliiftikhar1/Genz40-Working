import json
import re
import uuid
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from common.utils import EmailThread, get_client_ip
from django.templatetags.static import static
from .forms import PostContactForm, RegisterForm
from backend.models import CarConfiguration, BookedPackage , CustomUser, PostCommunity, PostCommunityJoiners, PostContactUs, PostNavItem, PostLandingPageImages, PostPackage, PostPayment, PostSubscribers
from django.contrib import messages
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from frontend.forms import PostSubscribeForm
from django.urls import path
from django.views import View
from django.urls import reverse
from backend.models import BookedPackage, ReservationNewFeatures, ReservationFeaturesPayment, DynamicPackages, FeaturesSection, PackageFeatureRoller, PackageFeatureRollerPlus, PackageFeatureBuilder
from backend.models import LearnMoreContent
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
import string
import random
from django.contrib.auth import login
from django.http import JsonResponse
import time  
import requests
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import HttpResponse
import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 
from .tokens import account_activation_token
from common.utils import send_otp, verify_otp
from django.core.cache import cache
from decimal import Decimal
from django.db.models import Sum
# Assuming these are your chat models (adjust based on your actual models)
from chat.models import ChatRoom, Message, ChatNotification  # Import your chat models
import channels.layers
from asgiref.sync import async_to_sync
import traceback
stripe.api_key = settings.STRIPE_SECRET_KEY

MAILCHIMP_API_URL = f"https://{settings.MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0"


def get_country_info(request):
    ip = get_client_ip(request)
    # response = requests.get(f'http://api.ipstack.com/{ip}?access_key={settings.IPSTACK_API_KEY}')
    # data = response.json()
    # country_code = data.get('country_code')
    return ip

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)

    car_list = []
    car_list.append({
            'image': section_1.image.url,
            'top_speed': '212 MPH',        # Make sure these fields exist
            'max_power': '710 BHP',
            'engine': '2640 cc',
            'acceleration': '5.4 secs',
        })
    car_list.append({
            'image': section_2.image.url,
            'top_speed': '250 MPH',        # Make sure these fields exist
            'max_power': '610 BHP',
            'engine': '2040 cc',
            'acceleration': '5.9 secs',
        })
    car_list.append({
            'image': section_3.image.url,
            'top_speed': '412 MPH',        # Make sure these fields exist
            'max_power': '810 BHP',
            'engine': '2840 cc',
            'acceleration': '4.4 secs',
        })
    items = PostNavItem.objects.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    # ip = get_country_info(request)
    # response = requests.get(f'https://ipinfo.io/{ip}/json')
    # data = response.json()
    # country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    # country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    context = {
        # 'country_code': country_code,
        # 'country_flag_url': country_flag_url,
        'section_1': section_1,
        'section_2': section_2,
        'section_3': section_3,
        'car_sections': car_list,
        'random_password': random_password,
        'items': items
    }

    return render(request, 'public/index.html', context)

def home(request):
    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
    items = PostNavItem.objects.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    # ip = get_country_info(request)
    # response = requests.get(f'https://ipinfo.io/{ip}/json')
    # data = response.json()
    # country_code = data.get('country')
    # # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    # country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    car_list = []
    car_list.append({
            'image': section_1.image.url,
            'top_speed': '212 MPH',        # Make sure these fields exist
            'max_power': '710 BHP',
            'engine': '2640 cc',
            'acceleration': '5.4 secs',
        })
    car_list.append({
            'image': section_2.image.url,
            'top_speed': '250 MPH',        # Make sure these fields exist
            'max_power': '610 BHP',
            'engine': '2040 cc',
            'acceleration': '5.9 secs',
        })
    car_list.append({
            'image': section_3.image.url,
            'top_speed': '412 MPH',        # Make sure these fields exist
            'max_power': '810 BHP',
            'engine': '2840 cc',
            'acceleration': '4.4 secs',
        })
    context = {
        # 'country_code': country_code,
        # 'country_flag_url': country_flag_url,
        'section_1': section_1,
        'section_2': section_2,
        'section_3': section_3,
        'car_sections': car_list,
        'random_password': random_password,
        'items': items
    }

    return render(request, 'public/index.html', context)

def tech_specs(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    context = {
        'items': items,
        'package_details': package_details
    }
    return render(request, 'public/technical_specs.html', context)



def learn_more(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    allitems = PostNavItem.objects.all()
    package_details = DynamicPackages.objects.filter(car_model=items).order_by('position')

    # Fetch LearnMoreContent for the current car
    learn_more_contents = LearnMoreContent.objects.filter(car=items)

    # Prepare Images and CardData from database
    Images = []
    CardData = []

    for content in learn_more_contents:
        # Extract image1 to image3 dynamically
        for i in range(1, 4):
            img_field = getattr(content, f'image{i}')
            if img_field:
                Images.append({"id": len(Images) + 1, "url": img_field.url})

        # Extract text1 to text3 dynamically
        for i in range(1, 4):
            txt_field = getattr(content, f'text{i}')
            if txt_field:
                CardData.append({"id": len(CardData) + 1, "details": txt_field})

    # Combine images and card texts
    combined_data = []
    min_length = min(len(Images), len(CardData))

    for i in range(min_length):
        combined_data.append({
            'image': Images[i],
            'card': CardData[i]
        })

    # Append remaining items if lists are unequal
    if len(Images) > len(CardData):
        for i in range(min_length, len(Images)):
            combined_data.append({'image': Images[i]})
    elif len(CardData) > len(Images):
        for i in range(min_length, len(CardData)):
            combined_data.append({'card': CardData[i]})

    # Load heading, subheading and all title images from the first LearnMoreContent entry
    TitleData = {
        "heading": items.title,
        "subheading": items.title,
        "title_image": None,
        "title_image_mobile": None,
        "title_image_front": None,
        "acceleration": None,
        "acceleration_unit": None,
        "acceleration_desc": None,
        "power_kw": None,
        "power_ps": None,
        "power_desc": None,
        "top_speed": None,
        "top_speed_unit": None,
        "top_speed_desc": None
    }

    if learn_more_contents.exists():
        first_content = learn_more_contents.first()
        TitleData = {
            "heading": first_content.heading or TitleData["heading"],
            "subheading": first_content.subheading or TitleData["subheading"],
            "title_image": first_content.title_image.url if first_content.title_image else None,
            "title_image_mobile": first_content.title_image_mobile.url if first_content.title_image_mobile else None,
            "title_image_front": first_content.title_image_front.url if first_content.title_image_front else None,
            "acceleration": first_content.acceleration,
            "acceleration_unit": first_content.acceleration_unit,
            "acceleration_desc": first_content.acceleration_desc,
            "power_kw": first_content.power_kw,
            "power_ps": first_content.power_ps,
            "power_desc": first_content.power_desc,
            "top_speed": first_content.top_speed,
            "top_speed_unit": first_content.top_speed_unit,
            "top_speed_desc": first_content.top_speed_desc
        }

    # Gallery images (can be moved to DB later)
    markI_gallery = [
        {"id": 1, "url": static('learn_more_images/Gallery/Mark I/IMG_1883.png'), "label": "body"},
        {"id": 2, "url": static('learn_more_images/Gallery/Mark I/IMG_1884.png'), "label": "body"},
        {"id": 3, "url": static('learn_more_images/Gallery/Mark I/IMG_1885.png'), "label": "body"},
        {"id": 4, "url": static('learn_more_images/Gallery/Mark I/IMG_1886.png'), "label": "body"},
        {"id": 5, "url": static('learn_more_images/Gallery/Mark I/IMG_1887.png'), "label": "body"},
        {"id": 6, "url": static('learn_more_images/Gallery/Mark I/IMG_1888.png'), "label": "body"},
        {"id": 7, "url": static('learn_more_images/Gallery/Mark I/IMG_1889.png'), "label": "body"},
        {"id": 8, "url": static('learn_more_images/Gallery/Mark I/IMG_1890.png'), "label": "body"},
        {"id": 9, "url": static('learn_more_images/Gallery/Mark I/IMG_1891.png'), "label": "body"},
        {"id": 10, "url": static('learn_more_images/Gallery/Mark I/IMG_1893.png'), "label": "body"},
        {"id": 11, "url": static('learn_more_images/Gallery/Mark I/IMG_1894.png'), "label": "body"},
        {"id": 12, "url": static('learn_more_images/Gallery/Mark I/IMG_1906.png'), "label": "intermediate"},
        {"id": 13, "url": static('learn_more_images/Gallery/Mark I/IMG_1909.png'), "label": "intermediate"},
        {"id": 14, "url": static('learn_more_images/Gallery/Mark I/IMG_1910.png'), "label": "intermediate"},
        {"id": 15, "url": static('learn_more_images/Gallery/Mark I/IMG_1911.png'), "label": "intermediate"},
        {"id": 16, "url": static('learn_more_images/Gallery/Mark I/IMG_1912.png'), "label": "intermediate"},
        {"id": 17, "url": static('learn_more_images/Gallery/Mark I/IMG_1914.png'), "label": "intermediate"},
        {"id": 18, "url": static('learn_more_images/Gallery/Chassis/IMG_1916.jpg'), "label": "chassis"},
        {"id": 19, "url": static('learn_more_images/Gallery/Chassis/IMG_1917.jpg'), "label": "chassis"},
        {"id": 20, "url": static('learn_more_images/Gallery/Chassis/IMG_1918.jpg'), "label": "chassis"},
        {"id": 21, "url": static('learn_more_images/Gallery/Chassis/IMG_1919.jpg'), "label": "chassis"},
    ]

    markII_gallery = [
        {"id": 1, "url": static('learn_more_images/Gallery/Mark II/IMG_1872.jpg'), "label": "body"},
        {"id": 2, "url": static('learn_more_images/Gallery/Mark II/IMG_1873.jpg'), "label": "body"},
        {"id": 3, "url": static('learn_more_images/Gallery/Mark II/IMG_1875.jpg'), "label": "body"},
        {"id": 4, "url": static('learn_more_images/Gallery/Mark II/IMG_1876.jpg'), "label": "body"},
        {"id": 5, "url": static('learn_more_images/Gallery/Mark II/IMG_1877.jpg'), "label": "body"},
        {"id": 6, "url": static('learn_more_images/Gallery/Mark II/IMG_1878.jpg'), "label": "body"},
        {"id": 7, "url": static('learn_more_images/Gallery/Mark II/IMG_1879.jpg'), "label": "body"},
        {"id": 8, "url": static('learn_more_images/Gallery/Mark II/IMG_1880.jpg'), "label": "body"},
        {"id": 9, "url": static('learn_more_images/Gallery/Mark II/IMG_1881.jpg'), "label": "body"},
        {"id": 10, "url": static('learn_more_images/Gallery/Chassis/IMG_1916.jpg'), "label": "chassis"},
        {"id": 11, "url": static('learn_more_images/Gallery/Chassis/IMG_1917.jpg'), "label": "chassis"},
        {"id": 12, "url": static('learn_more_images/Gallery/Chassis/IMG_1918.jpg'), "label": "chassis"},
        {"id": 13, "url": static('learn_more_images/Gallery/Chassis/IMG_1919.jpg'), "label": "chassis"},
    ]

    markIV_gallery = []

    # Choose gallery based on slug
    GalleryImages = []
    if slug == 'Mark-I':
        GalleryImages = markI_gallery
    elif slug == 'Mark-II':
        GalleryImages = markII_gallery
    elif slug == 'Mark-IV':
        GalleryImages = markIV_gallery

    context = {
        'allitems': allitems,
        'items': items,
        'package_details': package_details,
        'GalleryImages': GalleryImages,
        'TitleData': TitleData,
        'combined_data': combined_data,
        'learn_more_contents': learn_more_contents
    }

    return render(request, 'public/LearnMore.html', context)

def about(request):
    return render(request, 'public/about.html', {
        'navbar_style': 'dark'
    })

def blog(request):
    # items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog.html', {
        'navbar_style': 'dark'
    })

def blog_details(request):
    # items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog_details.html', {
        'navbar_style': 'dark',
        # 'details': items
    })

def contact_us(request):
    return render(request, 'public/contact_us.html')

def terms_conditions(request):
    return render(request, 'public/terms_conditions.html')

def privacy_policy(request):
    return render(request, 'public/privacy_policy.html')

def subscribe_email(email):
    """Subscribe an email to Mailchimp Audience List."""
    url = f"{MAILCHIMP_API_URL}/lists/{settings.MAILCHIMP_LIST_ID}/members/"
    data = {
        "email_address": email,
        "status": "subscribed"  # Can be "pending" for double opt-in
    }
    headers = {
        "Authorization": f"apikey {settings.MAILCHIMP_API_KEY}"
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return {"message": "Successfully subscribed!"}
    else:
        return response.json()  # Return Mailchimp's error response
    
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def register_page(request):
    form = RegisterForm()
    random_password = generate_random_password()
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    context = {
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'random_password': random_password,
        'form': form
    }
    return render(request, 'registration/register.html', context)

def send_activation_email(request, user, random_password):
    current_site = get_current_site(request)
    subject = "Activate Your Account"
    print("User Details before sending activation email",current_site,user,random_password)
    html_content = render_to_string("email/activation_email.html", {
        "email": user.email,
        "password": random_password,
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    })
    
    plain_text = strip_tags(html_content)
    sender = settings.EMAIL_FROM
    recipient_list = [user.email]
    EmailThread(subject, html_content, recipient_list, sender).start()

# def send_activation_email(request, user, random_password):
   
#     current_site = get_current_site(request)
#     mail_subject = "Activate Your Account"
#     print("User Details before sending activation email",current_site,user,random_password)
#     html_message = render_to_string("email/activation_email.html", {
#         "email": user.email,
#         "password": random_password,
#         "user": user,
#         # "domain": 'http://178.128.150.238',
#         "domain": current_site.domain,
#         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#         "token": account_activation_token.make_token(user),
#     })
    
#     plain_message = strip_tags(html_message)
    
#     # Send mail with both HTML and plain text versions
#     send_mail(
#         subject=mail_subject,
#         message=plain_message,  # Plain text version
#         from_email=settings.EMAIL_FROM,
#         recipient_list=[user.email],
#         html_message=html_message  # HTML version
    # )

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .forms import RegisterForm
from backend.models import PostCommunityJoiners
from chat.models import ChatRoom  # Import ChatRoom model
from django.db import transaction


from backend.models import CustomUser
import logging

logger = logging.getLogger(__name__)

def get_register_community(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')  # Added phone number check
            user_phone_number = ''.join(filter(str.isdigit, phone_number))[:14]

            # Check if user already exists by email OR phone number
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    "message": "User with this email already exists.",
                    "is_success": False
                }, status=400)
            if CustomUser.objects.filter(phone_number=user_phone_number).exists():
                return JsonResponse({
                    "message": "User with this phone number already exists.",
                    "is_success": False
                }, status=400)

            form = RegisterForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.set_password(request.POST['password'])
                    user.is_active = True

                    # Format phone number if provided
                    if user.phone_number:
                        user.phone_number = ''.join(filter(str.isdigit, user.phone_number))[:14]

                    # Truncate zip_code if needed
                    if hasattr(user, 'zip_code') and user.zip_code:
                        user.zip_code = user.zip_code[:5]

                    user.save()
                    # Automatically log in the user after successful registration
                    from django.contrib.auth import login, authenticate

                    # Authenticate the user (using email as username)
                    user = authenticate(request, username=user.email, password=request.POST['password'])
                    if user is not None:
                        login(request, user)

                    admin_user = CustomUser.objects.filter(is_staff=True).first()

                    # Create chatroom
                    chatroom = ChatRoom.objects.create(
                        customer=user,
                        admin=admin_user,
                        room_name=f"chat_{str(user.id)}_{str(admin_user.id) if admin_user else '0'}_{timezone.now().timestamp()}",
                        subject="Genz40-Chat Support",
                        created_at=timezone.now()
                    )

                    # Create welcome message
                    unread_by = [user.id] if user else []
                    welcome_message = Message.objects.create(
                        chat_room=chatroom,
                        sender=admin_user,
                        content="Welcome to Genz40! Our support team is here to assist you. Feel free to ask any questions.",
                        timestamp=timezone.now(),
                        unread_by=unread_by
                    )

                    # Create notification
                    ChatNotification.objects.create(
                        user=user,
                        chat_room=chatroom,
                        count=1,
                    )

                    # Send WebSocket welcome message
                    channel_layer = channels.layers.get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"chat_{str(chatroom.id)}",
                        {
                            "type": "chat_message",
                            "message": {
                                "room_id": str(chatroom.id),
                                "sender_id": str(admin_user.id) if admin_user else None,
                                "sender_name": "Support Team",
                                "sender_role": "admin",
                                "message": welcome_message.content,
                                "timestamp": welcome_message.timestamp.isoformat(),
                                "is_read": user.id not in welcome_message.unread_by,
                            }
                        }
                    )

                    # Add user to all communities
                    add_user_to_all_communities(user)

                    # Send activation/welcome email
                    try:
                        html_content = render_to_string("email/welcome_email.html", {
                            'user': user,
                            'password': request.POST['password']
                        })
                        send_activation_email(request, user, request.POST['password'])
                    except Exception as e:
                        logger.warning(f"Failed to send welcome email: {str(e)}")

                    return JsonResponse({
                        "message": "Thank You for Joining. You have been added to the community chatrooms! A welcome email has been sent.",
                        "is_success": True,
                        "user_id": str(user.id)  # Convert UUID to string
                    })
            else:
                return JsonResponse({
                    "message": "Registration failed. Please check the form data.",
                    "is_success": False,
                    "errors": form.errors
                }, status=400)

        except Exception as e:
            logger.error(f"Error in community registration: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": f"Registration failed: {str(e)}",
                "is_success": False
            }, status=400)

    return JsonResponse({"message": "Invalid request method.", "is_success": False}, status=400)

def add_user_to_community_chatroom(user, community):
    """
    Add a user to the community chatroom, creating one if it doesn't exist.
    """
    try:
        community_name = community.name if community else "General Community"
        chatroom_subject = f"{community_name} Chat"
        
        # Try to find existing community chatroom
        chatroom = ChatRoom.objects.filter(
            community=community,
            chat_type='community'
        ).first()

        admin_user = CustomUser.objects.filter(is_staff=True).first()

        if not chatroom:
            # Create new chatroom if none exists
            chatroom = ChatRoom.objects.create(
                chat_type='community',
                subject=chatroom_subject,
                admin=admin_user,
                community=community,
                room_name=f"community_chat_{uuid.uuid4().hex}",
                is_active=True
            )
            
            # Add all existing community members to the new chatroom
            community_members = PostCommunityJoiners.objects.filter(
                community=community,
                is_active=True
            ).values_list('user', flat=True)
            chatroom.members.add(*community_members)

        # Add the user to the chatroom members if not already present
        if not chatroom.members.filter(id=user.id).exists():
            chatroom.members.add(user)
            
        try:
            send_welcome_message(chatroom, user)
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}", exc_info=True)
            # Continue even if welcome message fails
            pass

    except Exception as e:
        logger.error(f"Error adding user to community chatroom: {str(e)}", exc_info=True)
        raise

def send_welcome_message(chatroom, user):
    """
    Send a welcome message to the community chatroom.
    """
    try:
        admin_user = CustomUser.objects.filter(is_staff=True).first()

        welcome_message = Message.objects.create(
            chat_room=chatroom,
            sender=admin_user,
            content=f"Welcome {user.get_full_name() or user.email} to the {chatroom.community.name} community!",
            message_type='text'
        )

        notification, created = ChatNotification.objects.get_or_create(
            user=user,
            chat_room=chatroom,
            defaults={'count': 1}
        )
        if not created:
            notification.increment()
                    
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{str(chatroom.id)}",
            {
                "type": "chat_message",
                "message": {
                    "room_id": str(chatroom.id),
                    "sender_id": str(admin_user.id) if admin_user else None,
                    "sender_name": "Support Team",
                    "sender_role": "admin",
                    "message": welcome_message.content,
                    "timestamp": welcome_message.timestamp.isoformat(),
                    "is_read": user.id not in welcome_message.unread_by,
                }
            }
        )
    except Exception as e:
        logger.error(f"Error sending welcome message: {str(e)}", exc_info=True)
        raise

def get_register(request):
    if request.method != 'POST':
        return register_page(request)

    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')

    # Check existing email and phone number
    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({"message": "This email is already registered!", 'is_success': False})
    
    if CustomUser.objects.filter(phone_number=phone_number).exists():
        return JsonResponse({"message": "This phone number is already registered!", 'is_success': False})

    if CustomUser.objects.filter(email=email, phone_number=phone_number).exists():
        return JsonResponse({"message": "Already joined.", 'is_success': False})

    form = RegisterForm(request.POST)
    if not form.is_valid():
        errors = form.errors.as_json()
        return JsonResponse({"message": f"Invalid form data: {errors}", 'is_success': False})

    try:
        user = form.save(commit=False)
        user.set_password(request.POST['password1'])
        user.is_active = True

        # Format phone number
        if user.phone_number:
            user.phone_number = ''.join(filter(str.isdigit, user.phone_number))[:14]

        # Truncate zip_code if needed
        if hasattr(user, 'zip_code') and user.zip_code:
            user.zip_code = user.zip_code[:5]

        user.save()

        # Find admin user (fallback to None)
        admin_user = CustomUser.objects.filter(is_staff=True).first()

        # Create chatroom
        chatroom = ChatRoom.objects.create(
            customer=user,
            admin=admin_user,
            room_name=f"chat_{str(user.id)}_{str(admin_user.id) if admin_user else '0'}_{timezone.now().timestamp()}",
            subject="Genz40-Chat Support",
            created_at=timezone.now()
        )

        # Create welcome message
        unread_by = [user.id] if user else []
        welcome_message = Message.objects.create(
            chat_room=chatroom,
            sender=admin_user,
            content="Welcome to Genz40! Our support team is here to assist you. Feel free to ask any questions.",
            timestamp=timezone.now(),
            unread_by=unread_by
        )

        # Create notification
        ChatNotification.objects.create(
            user=user,
            chat_room=chatroom,
            count=1,
        )

        # Send WebSocket welcome message
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{str(chatroom.id)}",
            {
                "type": "chat_message",
                "message": {
                    "room_id": str(chatroom.id),
                    "sender_id": str(admin_user.id) if admin_user else None,
                    "sender_name": "Support Team",
                    "sender_role": "admin",
                    "message": welcome_message.content,
                    "timestamp": welcome_message.timestamp.isoformat(),
                    "is_read": user.id not in welcome_message.unread_by,
                }
            }
        )

        # Send activation email
        html_content = render_to_string("email/welcome_email.html", {
            'user': user,
            'password': request.POST['password1']
        })
        send_activation_email(request, user, request.POST['password1'])

        # Add to community
        add_user_to_all_communities(user)

        return JsonResponse({
            "message": "Successfully added. Please check mailbox for password.",
            "is_success": True
        })

    except Exception as e:
        # Print full traceback for debug in dev
        print("Traceback:", traceback.format_exc())
        return JsonResponse({
            "message": f"Registration failed: {str(e)}",
            "is_success": False
        })
    

def add_user_to_all_communities(user):
    try:
        communities = PostCommunity.objects.all()
        if not communities.exists():
            logger.warning("No communities found when adding user.")
            return

        for community in communities:
            # Add user to each community if not already joined
            joiner, created = PostCommunityJoiners.objects.get_or_create(
                user=user,
                community=community,
                defaults={'is_active': True}
            )
            if created:
                try:
                    add_user_to_community_chatroom(user, community)
                except Exception as e:
                    logger.error(f"Error adding user to community chatroom: {str(e)}", exc_info=True)
                    # Continue with other communities even if one fails
                    continue
    except Exception as e:
        logger.error(f"Error adding user to all communities: {str(e)}", exc_info=True)
        raise


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        # return JsonResponse({"message": 'Your account has been activated successfully!'})
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('customer_login')
    else:
        messages.error(request, 'Invalid activation link!')
        return redirect('customer_login')
        # return JsonResponse({"message": 'Invalid activation link!'})
    
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({"message": 'Login successfully.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Invalid username or password.', 'is_success': False})
    else:
        return render(request, 'registration/login.html')
  
def subscribe(request):
    if request.method == 'POST':
        subscribe_email(request.POST['email'])
        if not PostSubscribers.objects.filter(email=request.POST['email']).exists():
            form = PostSubscribeForm(request.POST)
            if form.is_valid():
                form.save()
                subscribe_email(request.POST['email'])
                subject = 'Thank you for Newsletter subscribe - www.genz40.com'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [settings.ADMIN_EMAIL]
                c = {'name': 'Salman'}
                html_content = render_to_string('email/subscribe_user.html', c)
                send_mail(subject, html_content, email_from, recipient_list, fail_silently=False,
                            html_message=html_content)
                return JsonResponse({"message": 'Successfully subscribed.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Already subscribed.', 'is_success': False})

def navitem_detail(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package = items.details.filter(is_active=True).order_by('position')
    return render(request, 'public/navitem_detail.html',
                  {'items': items,
                   'packages': package})

def car_configurator(request,slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')

    # configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id),car_model_id=items.id)
    amount_due = package_details[0].amount_due
    # print("**********----*****Existing Configurations are : ",configure_vehicles)
    return render(request, 'public/CarConfigurator.html', {'items': items,
                                                        #    'existing_configurations':configure_vehicles,
                                                           'packages': package_details,
                                                           'amount_due': amount_due,
                                                           'slug': slug})

def new_car_configurator(request,slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    # configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id),car_model_id=items.id)
    amount_due = package_details[0].amount_due
    random_password = generate_random_password()
    # print("**********----*****Existing Configurations are : ",configure_vehicles)
    return render(request, 'public/Car-Configurator/MainFile.html', {'items': items,
                                                        #    'existing_configurations':configure_vehicles,
                                                           'packages': package_details,
                                                           'random_password':random_password,
                                                           'amount_due': amount_due,
                                                           'slug': slug})
    
def car_details(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    print('---------package', package_details[0].amount_due)
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    return render(request, 'public/car_details.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password})

def reserve_now(request, slug):
    email = request.GET.get('email', '')
    if not PostSubscribers.objects.filter(email=email).exists():
        PostSubscribers.objects.create(email=email)
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    return render(request, 'public/reserve_now.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password,
                    'email': email})

def lock_your_price_now(request, slug, packageId):
    email = request.user.email if request.user.is_authenticated else request.GET.get('email', '')
    
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = DynamicPackages.objects.filter(id=packageId).order_by('position')
    
    amount_due = package_details[0].reserveAmount
    random_password = generate_random_password()
    ip = get_country_info(request)
    
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        country_code = data.get('country')
        country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    except:
        country_code = 'US'  # default
        country_flag_url = f'https://www.flagsapi.com/US/flat/64.png'
    
    context = {
        'items': items,
        'package': package_details[0],
        'amount_due': amount_due,
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'random_password': random_password,
        'email': email,
        'user': request.user if request.user.is_authenticated else None
    }
    
    return render(request, 'public/lock_your_price_now.html', context)

def reserve_configuration_now(request, slug):
    email = request.GET.get('email', '')
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    return render(request, 'public/lock_your_price_now.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password,
                    'email': email})


def save_contact(request):
    if request.method == 'POST':
        mail_subject = "Thank you for contacting us"
        context = {
        'admin': 'Salman',
        'name': request.POST['name'],
        'email': request.POST['email'],
        'phone_number': request.POST['phone_number'],
        'car': request.POST['car'],
        'comments': request.POST['comments']
        }
        html_content = render_to_string("email/contact_admin.html", context)  # HTML content
        plain_text = strip_tags(html_content) 

        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_content, 
         )
        if not PostContactUs.objects.filter(email=request.POST['email']).exists():
            form = PostContactForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
            else:
                return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        
def generate_reference_number():
    # Get today's date in MMDDYY format
    today_date = datetime.datetime.today().strftime('%m%d%y')
    # Get the last inserted number from the database
    last_entry = PostPayment.objects.order_by('-created_at').first()  # Get last record
    last_number = int(last_entry.rn_number[-4:]) if last_entry else 1004  # Start from 1000 if no entry exists
    # Increment the last number
    new_number = last_number + 1
    # Generate the new reference number
    reference_number = f"RN{today_date}{new_number:04d}"  # Ensures 4-digit number format
    return reference_number

def create_account_before_checkout(request):
    if request.method == 'POST':
        # new_ref = generate_reference_number()
        amount = request.POST['amount']  # Amount in cents (e.g., $50.00)
        product_name = request.POST['package_name']
        email = request.POST['email']
        package_id = request.POST['package_id']
        user = CustomUser.objects.filter(email=email, phone_number=request.POST['phone_number']).first()
        if user:
            # Both email and phone exist in the same account → Proceed further
            login(request, user)
            fullName = user.first_name+ ' '+user.last_name
            session_data = {'product_name': product_name, 'amount': amount, 
                                    'email':user.email, 'fullName':fullName, 'id':user.id, 'car_slug':request.POST['car_slug'], 'package_id':package_id,
                                    'car_model':request.POST['car_model'], 'price':request.POST['price'], 'title': request.POST['package_name'],
                                    'success_url': request.build_absolute_uri(f'/car/reservation_success/'),
                                    'cancel_url': request.build_absolute_uri(f'/car/reservation-checkout/'),
                                    }
            # Ensure session_data is returned as a JSON response
            return JsonResponse({"message": "Success.", 'is_success': True, 'session_data': session_data})
                        
        # Check if a user already exists with the same email or phone number
        email_exists = CustomUser.objects.filter(email=email).exists()
        phone_exists = CustomUser.objects.filter(phone_number=request.POST['phone_number']).exists()

        if email_exists and phone_exists:
            return JsonResponse({"message": "This email and phone number belong to different users.", 'is_success': False})
        elif email_exists:
            return JsonResponse({"message": "This email is already registered.", 'is_success': False})
        elif phone_exists:
            return JsonResponse({"message": "This phone number is already registered.", 'is_success': False})
        else:
            print('-----not')
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(request.POST['password1'])
                user.zip_code = request.POST['zip_code']
                user.save()
                # user = form.get_user()
                login(request, user)
                subject = "Welcome to Our Platform - www.genz40.com"
                recipient_list = [user.email]
                sender = settings.EMAIL_FROM  # Ensure this is set in settings.py
                # Render HTML email template
                html_content = render_to_string("email/welcome_email.html", {'user': user, 'password': request.POST['password1']})
                # Send email in background
                EmailThread(subject, html_content, recipient_list, sender).start()

                if(user.id):
                    fullName = user.first_name+ ' '+user.last_name
                    session_data = {'product_name': product_name, 'amount': amount, 
                                    'email':user.email, 'fullName':fullName, 'id':user.id, 'car_slug':request.POST['car_slug'], 'package_id':package_id,
                                    'car_model':request.POST['car_model'], 'price':request.POST['price'], 'title': request.POST['package_name'],
                                    'success_url': request.build_absolute_uri(f'/car/reservation_success/'),
                                    'cancel_url': request.build_absolute_uri(f'/car/reservation-checkout/'),
                                    }
                    return JsonResponse({"message": "Success.", 'is_success': True, 'session_data': session_data})

def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            email = data.get("email")
            product_name = data.get("product_name")
            amount = data.get("amount")
            full_name = data.get("full_name")
            user_id = data.get("id")

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': "usd",
                        'product_data': {
                            'name': product_name,
                            'description': 'This reservation will save your position in line. When you car is available for production, we will invite you to configure and choose from dozens of options to make it complete personalized and unique.',
                            'images': ['https://genz40.com/static/images/genz/mark1-builder4.png'],
                        },
                        'unit_amount': int(amount) * 100,  
                    },
                    'quantity': 1,
                }],
                mode='payment',
               success_url=f"{data['success_url']}{data['booking_id']}/{{CHECKOUT_SESSION_ID}}",
               cancel_url=f"{data['cancel_url']}{data['booking_id']}",
                customer_email=email,
                metadata={
                    'full_name': full_name,
                    'email': email,
                    'product_name': product_name,
                    'description': str(user_id), #Passing Userid
                },
                payment_intent_data={
                'description': str(user_id), #Passing Userid
                "metadata": {
                    'product_name': product_name
                },
                },
            )
            return JsonResponse({"is_success": True, "checkout_url": session.url})
        except Exception as e:
            return JsonResponse({"is_success": False, "message": str(e)})

    return JsonResponse({"is_success": False, "message": "Invalid request"})

def payment_success(request):
    return render(request, 'public/payment/success.html', {'is_footer_required': False})

def payment_cancel(request):
    return render(request, 'public/payment/cancel.html', {'is_footer_required': False})

# STRIPE_WEBHOOK_KEY= 'whsec_559bd2071b3e1bf765d4ad825586dcaab38522c998fcccd802bc40f1d90f84c9'

@csrf_exempt  # Webhooks don't require CSRF protection
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_KEY
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.created':
        payment_intent = event['data']['object']
        # getting user id
        user_id = payment_intent.get('description')
        user_uuid = uuid.UUID(user_id)
        PostPayment.objects.create(
            user_id=user_uuid,
            package_name=payment_intent['metadata']['product_name'],
            stripe_payment_id=payment_intent['id'],
            amount='100',  # Convert to dollars
            rn_number=payment_intent['metadata']['new_ref'], #RN0130251005
            currency='usd',
            status='created',
        )
    elif event['type'] == 'charge.updated':
        payment_intent = event['data']['object']
        payment = PostPayment.objects.get(stripe_payment_id=payment_intent['payment_intent'])
        payment.status = payment_intent['status']
        payment.save()

        mail_subject = "New car reserved - GEN-Z 40"
        context = {
        'admin': 'Salman'
        }
        html_content = render_to_string("email/contact_admin.html", context)  # HTML content
        plain_text = strip_tags(html_content) 
        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_FROM,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_content, 
         )
    elif event['type'] == 'payment_intent.succeeded':
        print('=======================')
    else:
        print(f"Unhandled event type: {event['type']}")

    return JsonResponse({'success': True})

@login_required
def dashboard(request):
    header = 'Dashboard'
    print('-request.user.role', request.user.role)
    if request.user.role == 'admin':
        return render(request, "admin/dashboard.html", {'header': header })
    elif request.user.role == 'customer':
        return redirect('my_vehicles')
        # return render(request, "customer/dashboard.html", {'header': header })
    else:
        section_1 = get_object_or_404(PostLandingPageImages, section=1)
        section_2 = get_object_or_404(PostLandingPageImages, section=2)
        section_3 = get_object_or_404(PostLandingPageImages, section=3)
        random_password = generate_random_password()
        ip = get_country_info(request)
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        country_code = data.get('country')
        # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
        country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
        context = {
            'country_code': country_code,
            'country_flag_url': country_flag_url,
            'section_1': section_1,
            'section_2': section_2,
            'section_3': section_3,
            'random_password': random_password
        }

        return render(request, 'public/index.html', context)
        # return render(request, "customer/dashboard.html", {'header': header })
        # return redirect('index')
  
@login_required
def my_vehicles(request):
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    booked_packages = BookedPackage.objects.filter(user=str(request.user.id)).exclude(status='cancelled')
    print('-----configure_vehicles', configure_vehicles)
    # amount_due = order_vehicles[0].amount_due
    context = {
        'configure_vehicles':configure_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles,
        'booked_packages': booked_packages
    }
    return render(request, 'customer/reserved_vehicles/my_vehicles.html', context, {'is_footer_required': True})


@login_required
def my_configurations(request):
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    print('-----configure_vehicles', configure_vehicles)
    # amount_due = order_vehicles[0].amount_due
    context = {
        'configure_vehicles':configure_vehicles,
        'reserverd_vehicles':reserverd_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles
    }
    return render(request, 'customer/reserved_vehicles/my_configurations.html', context, {'is_footer_required': True})
@login_required
def my_package_bookings(request):
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    booked_packages = BookedPackage.objects.filter(user=str(request.user.id))
    
    context = {
        'configure_vehicles':configure_vehicles,
        'reserverd_vehicles':reserverd_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles,
        'booked_packages': booked_packages
    }
    return render(request, 'customer/reserved_vehicles/my_package_bookings.html', context, {'is_footer_required': True})


@login_required
def my_vehicle_details(request, id):
    reserverd_vehicle = PostPayment.objects.get(id=id)
    context = {
        'reserverd_vehicle':reserverd_vehicle
    }
    return render(request, 'customer/reserved_vehicles/vehicle_details.html', context, {'is_footer_required': True})

@login_required
def payment_history(request):
    # Get successful reservation payments for the current user
    reservation_payments = PostPayment.objects.filter( user=request.user, status='succeeded' ).select_related('rn_number').order_by('-created_at')
    
    # Get successful feature payments for the current user
    new_feature_payments = ReservationFeaturesPayment.objects.filter(
         reservation_feature__booked_package__user=request.user, payment_status='completed' 
    ).select_related(
        'reservation_feature',
        'reservation_feature__booked_package'
    ).order_by('-payment_date')
    
    context = {
        'reservation_payments': reservation_payments,
        'new_feature_payments': new_feature_payments,
        'is_footer_required': True
    }
    return render(request, 'customer/reserved_vehicles/payments.html', context)

@login_required
def profile_settings(request):
    return render(request, 'customer/profile/profile_settings.html', {'is_footer_required': True})

@login_required
def customer_message(request):
    return render(request, 'customer/message/message.html', {'is_footer_required': True})


def customer_community_message(request):
    if request.user.is_authenticated:
        return render(request, 'customer/message/communityChat.html', {'is_footer_required': True})
    else:
        return render(request, 'public/community_register.html', {'is_footer_required': True})

@login_required
def email_verify_from_dashboard(request):
    if request.user.is_authenticated:
        current_site = get_current_site(request)
        mail_subject = "Activate Your Account"
        context = {
            "user": request.user.first_name +' '+ request.user.last_name,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(request.user.pk)),
            "token": account_activation_token.make_token(request.user),
        }
        
        html_content = render_to_string("email/send_email_verification.html", context)  # HTML content
        plain_text = strip_tags(html_content) 

        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_FROM,
        recipient_list=[request.user.email],
        html_message=html_content, 
    )
        return JsonResponse({"is_success": True, "message": "Activation mail sent successfully."})
    else:
        return JsonResponse({"is_success": False, "message": "Failed to sent. Please try again."})

def clean_phone_number(phone_number):
    """Removes all non-numeric characters from a phone number."""
    return re.sub(r"\D", "", phone_number)
                  
@login_required
def send_otp_view(request):
    """Send OTP to the phone number"""
    user = get_object_or_404(CustomUser, id=request.user.id)
    phone_number = user.phone_number
    if not phone_number:
        return JsonResponse({"message": "Phone number is required", "is_success": False})

     # Check OTP request count
    cache_key = f"otp_attempts_{phone_number}"
    attempts = cache.get(cache_key, 0)

    if attempts >= settings.OTP_REQUEST_LIMIT:
        return JsonResponse({"message": "Too many OTP requests. Try again later.", "is_success": False})

    cleaned_number = clean_phone_number(phone_number)
    
    # Fetch country dialing code using an external API
    phone_response = requests.get(f"https://restcountries.com/v3.1/alpha/{user.country}")
    phone_data = phone_response.json()
    
    if phone_data:
        cleaned_number = f"{phone_data[0]['idd']['root']}"+cleaned_number
        # Send OTP using Twilio
        status_otp = send_otp(cleaned_number)

        # Update request count
        cache.set(cache_key, attempts + 1, settings.OTP_TIME_WINDOW)

        return JsonResponse({"message": "OTP sent", "status": status_otp, "is_success": True})

def otp_verify_page(request):
    return render(request, "customer/otp_verification.html")

@login_required
def verify_otp_view(request):
    """Verify the OTP entered by the user"""
    user = get_object_or_404(CustomUser, id=request.user.id)
    phone_number = user.phone_number
    if not phone_number:
        return JsonResponse({"message": "Phone number is required", "is_success": False})

    cleaned_number = clean_phone_number(phone_number)
    # Fetch country dialing code using an external API
    phone_response = requests.get(f"https://restcountries.com/v3.1/alpha/{user.country}")
    phone_data = phone_response.json()
    
    if phone_data:
        cleaned_number = f"{phone_data[0]['idd']['root']}"+cleaned_number
        data = json.loads(request.body)  # Parse JSON request body
        otp_code = data.get("otp")
        if not cleaned_number or not otp_code:
            return JsonResponse({"message": "Phone number and OTP are required", "is_success": False})

        # Verify OTP
        status_otp = verify_otp(cleaned_number, otp_code)
        if status_otp == "approved":
            user = get_object_or_404(CustomUser, phone_number=phone_number)
            user.is_phone_number_verified = True
            user.save()
            return JsonResponse({"message": "Phone number verified", "is_success": True})

    return JsonResponse({"message": "Invalid OTP", "is_success": False})

def car_selector(request):
    return render(request, "public/car_selector.html")  # Ensure this matches your template name


@login_required
def view_configuration(request, config_id):
    """
    View a specific saved configuration
    """
    configuration = get_object_or_404(CarConfiguration, id=config_id, user=request.user)
    slug = configuration.car_model.slug if hasattr(configuration.car_model, 'slug') else None
    
    context = {
        'configuration': configuration,
        'car_model': configuration.car_model,
        'config_id': config_id,
        'amount_due': configuration.total_price,
        'slug': slug  # Add the slug to the context
    }
    
    return render(request, 'public/view_configuration.html', context)


@login_required
def checkout(request):
    """
    View a cheout out page
    """
    return render(request, 'public/payment/checkout.html')


@login_required
def reservation_checkout(request, id):
    """
    View the reservation checkout page.
    """
    booked_package = get_object_or_404(BookedPackage, id=id)
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    context = {
        'user_details': request.user,
        'booked_package': booked_package,  # singular for clarity
        'country_code': country_code,
        'country_flag_url': country_flag_url,
    }

    return render(request, 'public/payment/reservation_checkout.html', context)



@csrf_exempt
def process_reservation_payment(request):
    print("Process reservation function called")
    if request.method == 'POST':
        try:
            user_id = request.user.id or request.POST.get('user_id')
            print("User id is : ",user_id)
            custom_user = CustomUser.objects.get(id=user_id)
            first_name = custom_user.first_name
            last_name = custom_user.last_name
            email = custom_user.email
            phone_number = custom_user.phone_number
            package_id = request.POST.get('package_id')

            print("User Id is : ",str(user_id))

            try:
                custom_user = CustomUser.objects.get(id=user_id)
                print("CUstomer user found",custom_user)
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})

            booked_package = BookedPackage.objects.get(id=package_id)
            
            customer = stripe.Customer.create(
                email=email,
                name=f"{first_name} {last_name}",
                phone=phone_number,
                metadata={
                    'package_id': str(package_id),
                    'user_email': email,
                }
            )

            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booked_package.car_model.title,
                        'description': f"Payment for {booked_package.title} Package of {booked_package.car_model.title}",
                        'images': ['https://genz40.com/static/images/genz/mark1-builder4.png'],
                    },
                    'unit_amount': int(float(100) * 100),  # amount in cents
                },
                'quantity': 1,
            }]

            session_data = {
                'customer_id': customer.id,
                'line_items': line_items,
                'package_id': str(package_id),
                'success_url': request.build_absolute_uri(
                            f'/car/reservation_success/{package_id}/'
                            ) + '{CHECKOUT_SESSION_ID}'+'/',
                
                'cancel_url': request.build_absolute_uri(
                    f'/car/reservation-checkout/{package_id}/'
                ),
                'metadata': {
                    'product_name':booked_package.car_model.title,
                    'package_id': str(package_id),
                    'user_email': email,
                    'descripton':f" Payment for {booked_package.title} Package of {booked_package.car_model.title}"
                },
                'payment_intent_data':{
                'description': f" Payment for {booked_package.title} Package of {booked_package.car_model.title}",
                "metadata": {
                    'product_name':booked_package.car_model.title, 
                },
                },
            }

            return JsonResponse({
                'is_success': True,
                'session_data': session_data,
                'message': 'Payment session prepared successfully'
            })

        except BookedPackage.DoesNotExist:
            return JsonResponse({
                'is_success': False,
                'message': 'Package not found'
            }, status=404)
        
        except Exception as e:
            return JsonResponse({
                'is_success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'is_success': False,
        'message': 'Invalid request method'
    }, status=405)




@csrf_exempt
def create_package_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                customer=data['customer_id'],
                payment_method_types=['card'],
                line_items=data['line_items'],
                mode='payment',
                success_url=f"{data['success_url']}{{CHECKOUT_SESSION_ID}}",
                cancel_url=data['cancel_url'],
                metadata=data['metadata'],
                payment_intent_data=data['payment_intent_data']
            )
            
            return JsonResponse({
                'is_success': True,
                'checkout_url': session.url,
                'message': 'Checkout session created successfully'
            })

        except Exception as e:
            return JsonResponse({
                'is_success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'is_success': False,
        'message': 'Invalid request method'
    }, status=405)



def reservation_success(request, id, sessionId):
    try:
        booked_package = BookedPackage.objects.get(id=id)
        remaining_payment_after_reserve = booked_package.price - Decimal('100.00')
        booked_package.status = 'confirmed'
        booked_package.build_status = 'payment_done'
        booked_package.remaining_price = remaining_payment_after_reserve
        booked_package.save()

        if sessionId:
            session = stripe.checkout.Session.retrieve(sessionId)
            print("Session Response is : ", session)
            
            booked_package_instance = BookedPackage.objects.get(reservation_number=booked_package.reservation_number)
            PostPayment.objects.create(
                user=booked_package.user,  
                rn_number=booked_package_instance,  
                stripe_payment_id=session.payment_intent,
                amount=100,  
                regarding="reserve",
                currency="usd",
                status="succeeded",  
                package_name=booked_package.title,
            )
        subject = "Reservation Confirmation - GEN-Z 40"
        current_site = get_current_site(request)
        context = {
                'user': request.user,
                'booked_package': booked_package,
                'amount': 100,  # Convert to string for template
                'payment_date': booked_package.updated_at,
                'domain': current_site.domain,
                'reservation_number': booked_package.reservation_number,
            }
        html_content = render_to_string('email/payment_successful.html', context)

        plain_text = strip_tags(html_content)
        receipient_list = [booked_package.user.email, settings.ADMIN_EMAIL]
        sender = settings.EMAIL_FROM
        
        EmailThread(subject, html_content, receipient_list, sender).start()
        return render(request, 'public/payment/success.html', {'is_footer_required': False})
    
    except Exception as e:
        print(f"Error in reservation_success: {str(e)}")
        return render(request, 'public/payment/error.html', {'error': str(e), 'is_footer_required': False})



from itertools import groupby
from operator import attrgetter

def reservation_details(request, id):
    """
    View the reservation checkout page.
    """
    booked_package = get_object_or_404(BookedPackage, reservation_number=id)
    package_type = booked_package.package.package_type
    car = booked_package.car_model.slug
    pending_features = booked_package.new_features.filter(status='pending')
    
    remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

    initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
    midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
    balance_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))

    payments = PostPayment.objects.filter(rn_number=id)

    # ip = get_country_info(request)
    # response = requests.get(f'https://ipinfo.io/{ip}/json')
    # data = response.json()
    # country_code = data.get('country')
    # country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    car_image = None
    if booked_package.car_model.images.exists():
        car_image = booked_package.car_model.images.first()
        
    # Process extra_features to get feature names
    extra_features_list = []
    extra_features_ids = []
    if booked_package.extra_features:
        features_data = booked_package.extra_features.split(',')
        feature_ids = []
        
        for item in features_data:
            parts = item.split(':')
            feature_id = parts[0]
            option = parts[1] if len(parts) > 1 else None
            
            try:
                if package_type == 'roller':
                    if car == 'Mark-I':
                        feature = PackageFeatureRoller.objects.get(id=feature_id, in_mark_I=True)
                    elif car == 'Mark-II':
                        feature = PackageFeatureRoller.objects.get(id=feature_id, in_mark_II=True)
                    else:
                        feature = PackageFeatureRoller.objects.get(id=feature_id, in_mark_IV=True)
                elif package_type == 'builder':
                    if car == 'Mark-I':
                        feature = PackageFeatureBuilder.objects.get(id=feature_id, in_mark_I=True)
                    elif car == 'Mark-II':
                        feature = PackageFeatureBuilder.objects.get(id=feature_id, in_mark_II=True)
                    else:
                        feature = PackageFeatureBuilder.objects.get(id=feature_id, in_mark_IV=True)
                    
                else:
                    if car == 'Mark-I':
                        feature = PackageFeatureRollerPlus.objects.get(id=feature_id, in_mark_I=True)
                    elif car == 'Mark-II':
                        feature = PackageFeatureRollerPlus.objects.get(id=feature_id, in_mark_II=True)
                    else:
                        feature = PackageFeatureRollerPlus.objects.get(id=feature_id, in_mark_IV=True)
                    
                feature_name = feature.name
                
                # If there's an option, append it to the feature name
                if option and hasattr(feature, f'{option}_price'):
                    option_name = getattr(feature, option, None)
                    if option_name:
                        feature_name = f"{feature_name} ({option_name})"
                
                extra_features_list.append(feature)
                extra_features_ids.append(feature_id)
            except (PackageFeatureRoller.DoesNotExist, ValueError):
                continue


    if package_type == 'roller':
        FeatureModel = PackageFeatureRoller
    elif package_type == 'builder':
        FeatureModel = PackageFeatureBuilder
    else:
        FeatureModel = PackageFeatureRollerPlus

    # Get IDs of new_features
    new_feature_ids = [str(f.feature_id) for f in booked_package.new_features.all()]

    newly_added_features = booked_package.new_features.filter(status='completed')

    included_features = FeatureModel.objects.filter(
            included=True
        )
    
    if car == 'Mark-I':
        unselected_features = FeatureModel.objects.filter(
            disabled=False,
            included=False,
            in_mark_I=True
        ).exclude(
            id__in=extra_features_ids + new_feature_ids
        ).order_by('section__name')

        unselected_feature_ids = FeatureModel.objects.filter(
            disabled=False,
            included=False,
            in_mark_I=True
        ).exclude(
            id__in=extra_features_ids + new_feature_ids
        ).values_list('id', flat=True)
    elif car == 'Mark-II':
            unselected_features = FeatureModel.objects.filter(
                disabled=False,
                included=False,
                in_mark_II=True
            ).exclude(
                id__in=extra_features_ids + new_feature_ids
            ).order_by('section__name')

            unselected_feature_ids = FeatureModel.objects.filter(
                disabled=False,
                included=False,
                in_mark_II=True
            ).exclude(
                id__in=extra_features_ids + new_feature_ids
            ).values_list('id', flat=True)
    else:
        unselected_features = FeatureModel.objects.filter(
            disabled=False,
            included=False,
            in_mark_IV=True
        ).exclude(
            id__in=extra_features_ids + new_feature_ids
        ).order_by('section__name')

        unselected_feature_ids = FeatureModel.objects.filter(
            disabled=False,
            included=False,
            in_mark_IV=True
        ).exclude(
            id__in=extra_features_ids + new_feature_ids
        ).values_list('id', flat=True)
    

    print('New Features IDs:', new_feature_ids)
    print('Extra Features IDs:', extra_features_ids)
    print('Unselected Features Query:', str(unselected_features.query))  # This shows the raw SQL
    print('Unselected Features Count:', unselected_features.count())
    print('Unselected Features Ids:', unselected_feature_ids)


    has_pending_features = booked_package.new_features.filter(status='pending').exists()
    new_pending_features = booked_package.new_features.filter(status='pending')
    pending_features_total = booked_package.new_features.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    



    # now i am group the features on the base of category
    # Group included_features by section
    included_features_grouped = []
    for key, group in groupby(included_features.order_by('section__name'), key=attrgetter('section.name')):
        included_features_grouped.append({
            'section': key,
            'features': list(group)
        })

    # Group extra_features_list by section
    extra_features_grouped = []
    if extra_features_list:
        for key, group in groupby(sorted(extra_features_list, key=attrgetter('section.name')), key=attrgetter('section.name')):
            extra_features_grouped.append({
                'section': key,
                'features': list(group)
            })

    # Group newly_added_features by section
    newly_added_features_grouped = []
    if newly_added_features.exists():
        for key, group in groupby(newly_added_features.order_by('features__section__name'), key=lambda x: x.features.section.name if x.features else None):
            newly_added_features_grouped.append({
                'section': key,
                'features': list(group)
            })
    context = {
        'user_details': request.user,
        'booked_package': booked_package,
        'payments': payments,
        # 'country_code': country_code,
        # 'country_flag_url': country_flag_url,
        'car_image': car_image,
        'remaining_payment_after_reserve': remaining_payment_after_reserve,
        'initial_payment': initial_payment,
        'midway_payment': midway_payment,
        'balance_payment': balance_payment,
        'reservation_features': unselected_features,
        'has_pending_features': has_pending_features,
        'included_features': included_features,
        'newly_added_features':newly_added_features,
        'new_pending_features': new_pending_features,
        'pending_features_total': pending_features_total,
        'extra_features_names': extra_features_list,
        'pending_features': pending_features,

        'included_features_grouped': included_features_grouped,
        'extra_features_grouped': extra_features_grouped,
        'newly_added_features_grouped': newly_added_features_grouped,
    }

    return render(request, 'public/reservation_details.html', context)


@csrf_exempt
def initiate_build_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reservation_number = data.get('reservation_number')
            booked_package = get_object_or_404(BookedPackage, reservation_number=reservation_number)

            remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

            initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            final_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))


            amount = Decimal('0')
            build_type = booked_package.build_type

            if build_type == 'initial_payment':
                amount = initial_payment
                previous_type = 'initial_payment'
            elif build_type == 'midway_payment':
                amount = midway_payment
                previous_type = 'midway_payment'
            elif build_type == 'final_payment':
                amount = final_payment
                previous_type = 'final_payment'

            print("Amount is", amount)

            customer = stripe.Customer.create(
                email=booked_package.user.email,
                name=f"{booked_package.user.first_name} {booked_package.user.last_name}",
                metadata={
                    'reservation_number': reservation_number,
                    'package_id': str(booked_package.id),
                    'user_id': str(booked_package.user.id),
                    'build_type': booked_package.build_type,
                    'build_status': booked_package.build_status
                }
            )

            # Create line item for Stripe checkout
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Build Payment - {booked_package.car_model.title}",
                        'description': f"Payment for {booked_package.build_type} stage of {booked_package.title} package",
                    },
                    'unit_amount': int(float(amount) * 100),  # amount in cents
                },
                'quantity': 1,
            }]

            # Prepare session data
            session_data = {
                'customer_id': customer.id,
                'line_items': line_items,
                'package_id': str(booked_package.id),
                'reservation_number': reservation_number,
                'success_url': request.build_absolute_uri(
                            f'/reservation/build-payment-success/{booked_package.id}/'
                            ) + '{CHECKOUT_SESSION_ID}'+'/',
                
                'cancel_url': request.build_absolute_uri(
                    f'/car/reservation-details/{booked_package.id}/'
                ),
                'metadata': {
                    'reservation_number': reservation_number,
                    'build_type': booked_package.build_type,
                    'build_status': booked_package.build_status,
                    'payment_type': 'build_payment'
                },
                'payment_intent_data': {
                    'description': f"Build payment for {booked_package.title} (Reservation: {reservation_number})",
                    'metadata': {
                        'reservation_number': reservation_number,
                        'build_type': booked_package.build_type,
                        'package_id': str(booked_package.id)
                    }
                }
            }

            return JsonResponse({
                'success': True,
                'session_data': session_data,
                'message': 'Payment session prepared successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
def create_build_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                customer=data['customer_id'],
                payment_method_types=['card'],
                line_items=data['line_items'],
                mode='payment',
                success_url=data['success_url'],
                cancel_url=data['cancel_url'],
                metadata=data['metadata'],
                payment_intent_data=data['payment_intent_data']
            )
            
            return JsonResponse({
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

def build_payment_success(request, id, sessionId):
    print("Session id is: ", sessionId)
    try:
        booked_package = get_object_or_404(BookedPackage, id=id)
        remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

    # Calculate payments based on percentages from booked_package
        initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
        midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
        balance_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))

        amount = Decimal('0.00')
        previous_type = ''


        if booked_package.build_type == 'initial_payment':
            previous_type = booked_package.build_type
            amount = initial_payment
            booked_package.status = 'in_progress'
            booked_package.build_status = 'payment_done'
        elif booked_package.build_type == 'midway_payment':
            previous_type = booked_package.build_type
            amount = midway_payment
            booked_package.build_status = 'payment_done'
        elif booked_package.build_type == 'final_payment':
            previous_type = booked_package.build_type
            amount = balance_payment
            booked_package.build_status = 'payment_done'

        booked_package.remaining_price = booked_package.remaining_price - amount
        booked_package.save()

        current_site = get_current_site(request)
        print("Current site is : ",current_site)
        payment_date = timezone.now().strftime('%B %d, %Y')
        context = {
            'user': request.user,
            'booked_package': booked_package,
            'message': "Your " + ( "Initial Payment" if previous_type == 'initial_payment' else "Mid Way Payment " if previous_type == 'midway_payment' else "Final Balance Payment" if previous_type == 'final_payment' else "Order"  ) + " has been successfully processed.",
            'amount': str(amount),
            'payment_date': payment_date,
            'domain': current_site.domain,
            'reservation_number': booked_package.reservation_number,
        }

        # Render email template
        subject = 'Payment Confirmation - GEN-Z 40'
        html_content = render_to_string('email/payment_successful.html', context)
        plain_text = strip_tags(html_content)
        receipient_list = [booked_package.user.email, settings.ADMIN_EMAIL]
        sender = settings.EMAIL_FROM
        
        EmailThread(subject, html_content, receipient_list, sender).start()
        
        # send_mail(
        #     subject=subject,  
        #     message=plain_text,
        #     from_email=settings.EMAIL_FROM,
        #     recipient_list=[booked_package.user.email],  
        #     fail_silently=False,
        #     html_message=html_content
        # )

        if not sessionId:
            raise ValueError("No session ID provided")

        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(sessionId)
        print("Session Data is: ", session)
        
        # Create payment record
        booked_package_instance = BookedPackage.objects.get(reservation_number=booked_package.reservation_number)
        PostPayment.objects.create(
                user=booked_package.user,  
                rn_number=booked_package_instance,  
                stripe_payment_id=session.payment_intent,
                amount=float(amount),
                regarding=previous_type,
                currency="usd",
                status="succeeded",  
                package_name=booked_package.title,
        )
       
        

        return render(request, 'public/payment/success.html', {
            'is_footer_required': False,
            'message': 'Build payment completed successfully! A confirmation email has been sent.'
        })
    
    except Exception as e:
        # Log the error and show error page
        print(f"Error in build_payment_success: {str(e)}")
        return render(request, 'public/payment/success.html', {
            'is_footer_required': False,
            'message': 'Payment completed but there was an issue updating our records or sending the confirmation email. Please contact support.'
        })
    
def send_test_email(request,id):
    booked_package = get_object_or_404(BookedPackage, id=id)
    amount = 100
    current_site = get_current_site(request)
    try:
        context = {
                'user': request.user,
                'booked_package': booked_package,
                'amount': str(amount),  # Convert to string for template
                'payment_date': booked_package.updated_at,
                'domain': current_site.domain,
                'reservation_number': booked_package.reservation_number,
            }
        
        # Render the HTML template
        html_content = render_to_string('email/payment_successful.html', context)
        plain_text = strip_tags(html_content)  # Create a plain text version
        
        send_mail(
            subject="Test Email from Django",
            message=plain_text,  # Plain text version
            from_email=settings.EMAIL_FROM,
            recipient_list=["alijanali0091@gmail.com"],
            fail_silently=False,
            html_message=html_content  # HTML version
        )
        return HttpResponse("HTML Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")
    


def add_reservation_feature(request, reservation_number):
    """
    Add new features to a booked package via AJAX.
    """
    reservation = get_object_or_404(BookedPackage, reservation_number=reservation_number)
    
    if request.method == 'POST':
        try:
            # Get features data from form
            features_data = json.loads(request.POST.get('features_data', '[]'))
            
            if not features_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Please select at least one feature.'
                }, status=400)

            # Process each feature
            for feature in features_data:
                feature_name = feature.get('name')
                feature_id = feature.get('id')
                description = feature.get('description')
                amount = feature.get('amount')

                # Validate required fields
                if not all([feature_name, description, amount]):
                    return JsonResponse({
                        'success': False,
                        'message': 'All fields are required for feature: ' + feature_name
                    }, status=400)

                # Validate amount
                try:
                    amount = Decimal(amount)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid amount format for feature: ' + feature_name
                    }, status=400)

                # Create new feature with pending status
                ReservationNewFeatures.objects.create(
                    booked_package=reservation,
                    feature_id=feature_id,
                    features=feature_name,
                    amount=amount,
                    status='pending'
                )

            return JsonResponse({
                'success': True,
                'message': 'Features added successfully. They are pending approval.',
                'reservation_number': reservation_number
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid features data format.'
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

def delete_reservation_feature(request, reservation_number, feature_id):
    """
    Delete a feature from a booked package via AJAX.
    """
    reservation = get_object_or_404(BookedPackage, reservation_number=reservation_number)
    
    if request.method == 'DELETE':
        try:
            feature = get_object_or_404(
                ReservationNewFeatures, 
                id=feature_id, 
                booked_package=reservation
            )
            
            # Only allow deletion if feature is pending or rejected
            if feature.status not in ['pending', 'rejected']:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot delete features that are approved or completed.'
                }, status=400)
                
            feature.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Feature deleted successfully.',
                'feature_id': feature_id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)





@csrf_exempt
def initiate_feature_payment(request, feature_id=None):
    """
    Initiate payment for a single feature or all pending features.
    Validates user ownership and feature status, creates a Stripe customer,
    and prepares data for the checkout session.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)

        data = json.loads(request.body)
        reservation_number = data.get('reservation_number')
        if not reservation_number:
            return JsonResponse({
                'success': False,
                'message': 'Reservation number is required'
            }, status=400)

        booked_package = get_object_or_404(
            BookedPackage,
            reservation_number=reservation_number,
            user=request.user
        )

        # Create or retrieve Stripe customer
        customer = stripe.Customer.create(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}",
            metadata={
                'reservation_number': reservation_number,
                'user_id': str(request.user.id),
                'package_id': str(booked_package.id)
            }
        )

        if feature_id:
            # Single feature payment
            feature = get_object_or_404(
                ReservationNewFeatures,
                id=feature_id,
                booked_package=booked_package
            )

            if feature.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': 'Feature not available for payment'
                }, status=400)

            line_items = [create_line_item(
                name=f"Feature: {feature.features}",
                description=f"{feature.features} for {booked_package.car_model.title}",
                amount=feature.amount
            )]
            
            metadata = {
                'feature_id': str(feature.id),
                'reservation_number': reservation_number,
                'is_pay_all': 'false',
                'user_id': str(request.user.id)
            }
        else:
            # Pay all pending features
            pending_features = booked_package.new_features.filter(status='pending')
            if not pending_features.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No pending features available'
                }, status=400)

            total_amount = sum(f.amount for f in pending_features)
            line_items = [create_line_item(
                name=f"Multiple Features for {booked_package.car_model.title}",
                description=f"Payment for {pending_features.count()} features",
                amount=total_amount
            )]
            
            metadata = {
                'feature_ids': ','.join(str(f.id) for f in pending_features),
                'reservation_number': reservation_number,
                'is_pay_all': 'true',
                'user_id': str(request.user.id)
            }

        session_data = {
            'customer_id': customer.id,
            'line_items': line_items,
            'success_url': build_success_url(request, reservation_number),
            'cancel_url': request.build_absolute_uri(
                reverse('reservation_details', args=[reservation_number])
            ),
            'metadata': metadata,
            'payment_intent_data': {
                'description': f"Feature payment for {booked_package.car_model.title}",
                'metadata': metadata
            }
        }

        return JsonResponse({
            'success': True,
            'session_data': session_data,
            'message': 'Payment session prepared'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({'success': False, 'message': f'Stripe error: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def create_line_item(name, description, amount):
    """Helper to create Stripe line item"""
    return {
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': name, 'description': description},
            'unit_amount': int(Decimal(str(amount)) * 100)  # Convert to cents
        },
        'quantity': 1
    }

def build_success_url(request, reservation_number):
    """Helper to build success URL with session ID"""
    return (request.build_absolute_uri(
        f'/feature/feature-payment-success/{reservation_number}/'
    ) + '{CHECKOUT_SESSION_ID}/')

@csrf_exempt
def create_feature_checkout_session(request):
    """Create Stripe checkout session"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        data = json.loads(request.body)
        session = stripe.checkout.Session.create(
            customer=data['customer_id'],
            payment_method_types=['card'],
            line_items=data['line_items'],
            mode='payment',
            success_url=data['success_url'],
            cancel_url=data['cancel_url'],
            metadata=data['metadata'],
            payment_intent_data=data['payment_intent_data']
        )

        return JsonResponse({
            'success': True,
            'checkout_url': session.url,
            'session_id': session.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def new_feature_payment_success(request, id, sessionId):
    """Handle successful payment"""
    try:
        session = stripe.checkout.Session.retrieve(sessionId)
        if session.payment_status != 'paid':
            messages.error(request, "Payment not completed")
            return redirect('reservation_details', id=id)

        booked_package = get_object_or_404(
            BookedPackage,
            reservation_number=id,
            user=request.user
        )

        if session.metadata.get('is_pay_all') == 'true':
            handle_pay_all_features(request, session, booked_package)
        else:
            handle_single_feature(request, session, booked_package)

        return redirect('reservation_details', id=id)

    except Exception as e:
        messages.error(request, f"Error processing payment: {str(e)}")
        return redirect('reservation_details', id=id)

def handle_pay_all_features(request, session, booked_package):
    """Process payment for all features"""
    feature_ids = session.metadata.get('feature_ids', '').split(',')
    features = ReservationNewFeatures.objects.filter(
        id__in=feature_ids,
        booked_package=booked_package,
        status='pending'
    )
    
    for feature in features:
        feature.status = 'completed'
        feature.save()
        create_payment_record(feature, session.payment_intent)
    
    messages.success(request, f"Payment successful! {features.count()} features added")

def handle_single_feature(request, session, booked_package):
    """Process payment for single feature"""
    feature = get_object_or_404(
        ReservationNewFeatures,
        id=session.metadata.get('feature_id'),
        booked_package=booked_package,
        status='pending'
    )
    
    feature.status = 'completed'
    feature.save()
    create_payment_record(feature, session.payment_intent)
    send_confirmation_email(request, booked_package, feature)
    messages.success(request, f"Payment successful! Feature added")

def create_payment_record(feature, payment_intent):
    """Create payment record in database"""
    ReservationFeaturesPayment.objects.create(
        reservation_feature=feature,
        amount=feature.amount,
        payment_status='completed',
        payment_method='card',
        transaction_id=payment_intent
    )

def send_confirmation_email(request, booked_package, feature):
    """Send payment confirmation email"""
    subject = "Feature Payment Confirmation"
    context = {
        'user': request.user,
        'booked_package': booked_package,
        'feature': feature,
        'amount': feature.amount,
        'domain': get_current_site(request).domain
    }
    
    html_content = render_to_string('email/payment_successful.html', context)
    email = EmailMessage(
        subject,
        strip_tags(html_content),
        settings.EMAIL_FROM,
        [booked_package.user.email, settings.ADMIN_EMAIL],
    )
    email.send()

    # Dynamic Package Page
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from decimal import Decimal


def dynamic_configurator(request, car_model_slug):
    car_model = get_object_or_404(PostNavItem, slug=car_model_slug)
    
    packages = DynamicPackages.objects.filter(car_model=car_model).order_by('position')
    
    sections = FeaturesSection.objects.all().order_by('created_at')
    
    rollerfeatures = PackageFeatureRoller.objects.all().order_by('created_at')
    rollerplusfeatures = PackageFeatureRollerPlus.objects.all().order_by('created_at')
    builderfeatures = PackageFeatureBuilder.objects.all().order_by('created_at')
    
    context = {
        'car_model': car_model,
        'packages': packages,
        'sections': sections,
        'rollerfeatures': rollerfeatures,
        'rollerplusfeatures': rollerplusfeatures,
        'builderfeatures': builderfeatures,
    }
    
    return render(request, 'public/DynamicConfigurator/configurator.html', context)