from PIL import Image
from django.core.exceptions import ValidationError
from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from common.utils import validate_file_extension
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role='customer', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_alpha_validator = RegexValidator(r'^[a-zA-Z]', message='name must be alphabet')
    first_name = models.CharField(max_length=30, blank=True, null=True, validators=[is_alpha_validator])
    last_name = models.CharField(max_length=30, blank=True, null=True, validators=[is_alpha_validator])
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{14,14}$',
                                 message="Phone number must be entered Up to 14 digits allowed")
    phone_number = models.CharField(max_length=14,
                                    blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    street_address_1 = models.CharField(max_length=250, null=True, blank=True)
    street_address_2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_img/', validators=[validate_file_extension], null=True,
                                      blank=True)
    social_user_image = models.CharField(max_length=512, null=True, blank=True)
    provider = models.CharField(max_length=64, null=True, blank=True, default='genz40')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_login = models.DateTimeField(auto_now_add = True, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        # Return full name or a fallback (e.g., username)
        return f"{self.first_name} {self.last_name}".strip() or self.username

    class Meta:
        db_table = 'custom_users'


REVIEW_STATUS = (
    (1, "Approved"),
    (0, "Pending"),
    (2, "Declined")
)

# Define Default Steps
DEFAULT_STATUSES = [
    {"name": "Order Confirmed", "is_active": True},
    {"name": "In Production", "is_active": False},
    {"name": "Built", "is_active": False},
    {"name": "Shipped", "is_active": False},
    {"name": "Final Preparation", "is_active": False},
]


class PostReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, blank=True, null=True, )
    city = models.CharField(max_length=120, blank=True, null=True, )
    rating = models.CharField(max_length=120, blank=True, null=True, )
    review = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True, choices=REVIEW_STATUS, default='0', )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'reviews'


# Blog models.
class PostBlog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])

    class Meta:
        db_table = 'blogs'


# Meta data models.
class PostMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False)
    meta_title = models.CharField(max_length=70)
    meta_keywords = models.CharField(max_length=100, blank=True, null=True)
    meta_desc = models.TextField(blank=True, null=True, max_length=170)
    page_title = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'meta_datas'


class PostNavItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    estimated_delivery = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.is_active:
            self.children.update(is_active=False)

    def get_active_children(self):
        return self.children.filter(is_active=True).order_by('position')

    def get_absolute_url(self):
        return reverse('navitem_detail', kwargs={'slug': self.slug})
        # return reverse('car_details', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['position']
        db_table = 'nav_items'


def validate_image_count(value):
    if value.nav_item.images.count() >= 10:
        raise ValidationError('You can only upload up to 10 images.')


class PostImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            validate_image_count(self)
        super().save(*args, **kwargs)
        if not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.image)
            super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 200)):
        from PIL import Image as PILImage
        from io import BytesIO
        from django.core.files.base import ContentFile

        img = Image.open(image).convert('RGB')
        # img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG')
        thumb_file = ContentFile(thumb_io.getvalue(), 'thumb_' + image.name)
        return thumb_file


class PostPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='details')
    name = models.CharField(max_length=100)
    amount = models.IntegerField(blank=True, default=0)
    amount_reserve = models.IntegerField(blank=True, default=0)
    amount_due = models.IntegerField(blank=True, default=0)
    estimated_delivery = models.DateTimeField(default=timezone.now)
    offer_valid = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    image = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']
        db_table = 'packages'


class PostPackageDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='package_details')
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.package.name} - {self.service_type}"

    class Meta:
        ordering = ['position']
        db_table = 'package_details'


class PostPackageFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='feature_details')
    name = models.CharField(max_length=100)
    amount = models.IntegerField(blank=True, default=0)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.package.name} - {self.name}"

    class Meta:
        ordering = ['position']
        db_table = 'package_features'


class PostPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='part_details')
    parts_name = models.CharField(max_length=70)
    parts_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='parts_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'parts'


class PostCharging(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='charging_details')
    charging_name = models.CharField(max_length=70)
    charging_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='charging_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'charging'


class PostAccessories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='accessories_details')
    accessories_name = models.CharField(max_length=70)
    accessories_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='accessories_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'accessories'


class PostPaint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='paint_details')
    paint_name = models.CharField(max_length=70)
    paint_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='paint_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'paint'


class PostWheels(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='wheels_details')
    wheel_name = models.CharField(max_length=70)
    wheel_desc = models.TextField(blank=True, null=True, max_length=170)
    wheel_amount = models.IntegerField(blank=True, default=0)
    wheel_size = models.CharField(max_length=64, blank=True, default=0)
    wheel_color = models.CharField(max_length=64, blank=True, default=0)
    wheel_offset = models.CharField(max_length=64, blank=True, default=0)
    image = models.ImageField(upload_to='wheels_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'wheels'


class PostLandingPageImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='landing_images')
    title = models.CharField(max_length=100)
    title_data = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=400)
    section = models.IntegerField(blank=True, default=0)
    tag = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='landing_pages_images/', null=True, blank=True)
    web_image = models.ImageField(upload_to='web_landing_pages_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']
        db_table = 'landing_pages_images'


class PostSubscribers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'subscribers'


class PostCommunity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='communities')
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.name

    class Meta:
        db_table = 'community'

class PostCommunityJoiners(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('backend.CustomUser', on_delete=models.CASCADE, related_name='new_community_joiners')
    community = models.ForeignKey('backend.PostCommunity', on_delete=models.CASCADE, related_name='joiners' )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        community_name = self.community.name if self.community.name else "Unnamed Community"
        return f"{self.user.email} in {community_name}"

    class Meta:
        db_table = 'community_joiners'
        unique_together = ('user', 'community')
        indexes = [
            models.Index(fields=['user', 'community']),
            models.Index(fields=['is_active']),
        ]

    def clean(self):
        """Validate that the user hasn't already joined this community."""
        if self.pk is None:  # Only check for new instances
            if PostCommunityJoiners.objects.filter(user=self.user, community=self.community).exists():
                raise ValidationError(
                    f"User {self.user.email} is already a member of {self.community.name or 'this community'}"
                )

    def save(self, *args, **kwargs):
        """Update timestamp and sync with chatroom membership."""
        # Validate the instance
        self.clean()

        # Update timestamp for existing instances
        if self.pk:
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)

        # Sync with community chatroom membership
        ChatRoom = apps.get_model('chat', 'ChatRoom')  # Lazy load ChatRoom
        chatrooms = ChatRoom.objects.filter(community=self.community, chat_type='community')
        for chatroom in chatrooms:
            if self.is_active:
                if not chatroom.members.filter(id=self.user.id).exists():
                    chatroom.members.add(self.user)
            else:
                if chatroom.members.filter(id=self.user.id).exists():
                    chatroom.members.remove(self.user)

class PostContactUs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.IntegerField(blank=True, null=True)
    car = models.CharField(max_length=30, blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'contact_us'




class CarConfiguration(models.Model):
    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='car_configurations')
    car_model = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='configurations')
    
    # --- Exterior Customization ---
    exterior_color = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Metallic Blue"
    wheel_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "19-inch Sport Alloy"
    wheel_color = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Black"
    grille_style = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Gloss Black"
    roof_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Panoramic Sunroof"
    mirror_style = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Auto-Folding"
    lighting_package = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Matrix LED"
    decals = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Racing Stripes"

    # --- Interior Customization ---
    upholstery_material = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Nappa Leather"
    interior_color = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Chestnut Brown"
    seat_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Ventilated Massage Seats"
    dashboard_trim = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Carbon Fiber"
    steering_wheel = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Heated Sport Steering"

    # --- Performance & Drivetrain ---
    engine_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "V8 Hybrid"
    transmission = models.CharField(max_length=50, blank=True, null=True)  # e.g., "8-Speed Automatic"
    drivetrain = models.CharField(max_length=50, blank=True, null=True)  # e.g., "AWD"
    suspension = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Adaptive Air Suspension"
    exhaust_system = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Sport Exhaust"

    # --- Technology & Infotainment ---
    infotainment_system = models.CharField(max_length=50, blank=True, null=True)  # e.g., "12-inch Touchscreen"
    sound_system = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Bose Premium"
    heads_up_display = models.BooleanField(default=False)
    connectivity_package = models.CharField(max_length=50, blank=True, null=True)  # e.g., "5G Wi-Fi Hotspot"

    # --- Safety & Assistance ---
    autonomous_driving_level = models.CharField(max_length=20, blank=True, null=True)  # e.g., "Level 2"
    parking_assist = models.BooleanField(default=False)
    blind_spot_monitoring = models.BooleanField(default=False)
    night_vision = models.BooleanField(default=False)

    # --- Packages & Accessories ---
    luxury_package = models.BooleanField(default=False)
    sport_package = models.BooleanField(default=False)
    winter_package = models.BooleanField(default=False)
    offroad_package = models.BooleanField(default=False)
    towing_hitch = models.BooleanField(default=False)
    roof_rack = models.BooleanField(default=False)

    # --- Pricing ---
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    exterior_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interior_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    performance_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tech_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    package_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    

    # --- Metadata ---
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_saved = models.BooleanField(default=False)  # True when user saves config
    is_ordered = models.BooleanField(default=False)  # True when converted to order

    def calculate_total_price(self):
        """Dynamically calculate total based on selections."""
        self.total_price = (
            self.base_price +
            self.exterior_price +
            self.interior_price +
            self.performance_price +
            self.tech_price +
            self.package_price
        )
        return self.total_price

    def save(self, *args, **kwargs):
        # self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s {self.car_model.title} Config (${self.total_price})"

    class Meta:
        ordering = ['-created_at']
        db_table = 'car_configurations'


class DynamicPackages(models.Model):
    PACKAGE_TYPES = (
        ('roller', 'Roller Package'),
        ('roller_plus', 'Roller Plus Package'),
        ('builder', 'Builder Package'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    car_model = models.ForeignKey('PostNavItem', on_delete=models.CASCADE, related_name='packages')
    description = models.TextField()
    baseAmount = models.DecimalField(max_digits=10, decimal_places=2)
    discountAmount = models.DecimalField(max_digits=10, decimal_places=2)
    reserveAmount = models.DecimalField(max_digits=10, decimal_places=2)
    position = models.DecimalField(max_digits=10,decimal_places=0,default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_package_type_display()}) - {self.car_model}"

    class Meta:
        db_table = 'dynamic_packages'
        verbose_name_plural = 'Dynamic Packages'


class FeaturesSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} "

    class Meta:
        db_table = 'dynamic_features_sections'
        verbose_name_plural = 'Features Sections'


class PackageFeatureRoller(models.Model):
    FEATURE_TYPE_CHOICES = (
        ('checkbox', 'Checkbox'),
        ('radiobox', 'Radiobox'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey('FeaturesSection', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=FEATURE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    option1 = models.CharField(max_length=100, blank=True, null=True)
    option2 = models.CharField(max_length=100, blank=True, null=True)
    option1_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    option2_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    checked = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    included = models.BooleanField(default=False)
    in_rollerPlus = models.BooleanField(
        default=True,
        verbose_name="Available in Roller Plus",
        help_text="Whether this feature is available in Roller Plus models"
    )
    in_mark_I = models.BooleanField(
        default=True,
        verbose_name="Available in Mark I",
        help_text="Whether this feature is available in Mark I models"
    )
    in_mark_II = models.BooleanField(
        default=True,
        verbose_name="Available in Mark II",
        help_text="Whether this feature is available in Mark II models"
    )
    in_mark_IV = models.BooleanField(
        default=True,
        verbose_name="Available in Mark IV",
        help_text="Whether this feature is available in Mark IV models"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'all_roller_package_features'
        verbose_name_plural = 'All Roller Package Features'

    @classmethod
    def get_feature_name_by_id(cls, feature_id):
        """
        Returns the name of a feature given its ID.
        
        Args:
            feature_id: The UUID of the feature (can be string or UUID object)
        
        Returns:
            str: The name of the feature if found, None otherwise
        """
        try:
            if isinstance(feature_id, str):
                feature_id = uuid.UUID(feature_id)
                
            feature = cls.objects.filter(id=feature_id).first()
            return feature.name if feature else None
        except (ValueError, AttributeError):
            return None
        
    def __str__(self):
        return f"{self.name} - {self.section}"
    

class PackageFeatureRollerPlus(models.Model):
    FEATURE_TYPE_CHOICES = (
        ('checkbox', 'Checkbox'),
        ('radiobox', 'Radiobox'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey('FeaturesSection', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=FEATURE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    option1 = models.CharField(max_length=100, blank=True, null=True)
    option2 = models.CharField(max_length=100, blank=True, null=True)
    option1_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    option2_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    checked = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    included = models.BooleanField(default=False)
    in_mark_I = models.BooleanField(
        default=True,
        verbose_name="Available in Mark I",
        help_text="Whether this feature is available in Mark I models"
    )
    in_mark_II = models.BooleanField(
        default=True,
        verbose_name="Available in Mark II",
        help_text="Whether this feature is available in Mark II models"
    )
    in_mark_IV = models.BooleanField(
        default=True,
        verbose_name="Available in Mark IV",
        help_text="Whether this feature is available in Mark IV models"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'all_rollerplus_package_features'
        verbose_name_plural = 'All Roller Plus Package Features'

    def __str__(self):
        return f"{self.name} - {self.section} "
    

class PackageFeatureBuilder(models.Model):
    FEATURE_TYPE_CHOICES = (
        ('checkbox', 'Checkbox'),
        ('radiobox', 'Radiobox'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey('FeaturesSection', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=FEATURE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    option1 = models.CharField(max_length=100, blank=True, null=True)
    option2 = models.CharField(max_length=100, blank=True, null=True)
    option1_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    option2_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    checked = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    included = models.BooleanField(default=False)
    
    # New fields for car model compatibility
    in_mark_I = models.BooleanField(
        default=True,
        verbose_name="Available in Mark I",
        help_text="Whether this feature is available in Mark I models"
    )
    in_mark_II = models.BooleanField(
        default=True,
        verbose_name="Available in Mark II",
        help_text="Whether this feature is available in Mark II models"
    )
    in_mark_IV = models.BooleanField(
        default=True,
        verbose_name="Available in Mark IV",
        help_text="Whether this feature is available in Mark IV models"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'all_builder_package_features'
        verbose_name_plural = 'All Builder Package Features'
        # abstract = True

    def __str__(self):
        return f"{self.name} - {self.section} "




class BookedPackage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
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
    
    BUILD_STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('payment_done', 'Payment Done'),
        ('completed', 'Completed'),
        ('awaiting_payment', 'Awaiting Payment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='booked_Package_configuration')
    car_model = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='package_car')
    title = models.CharField(max_length=255)
    package = models.ForeignKey(DynamicPackages, on_delete=models.CASCADE, related_name='booked_Package_id')
    extra_features = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remaining_price = models.IntegerField(default=0, null=True)
    initial_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=40)
    midway_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=40)
    final_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    
    # New fields
    build_type = models.CharField(max_length=30, choices=BUILD_TYPE_CHOICES, default='order_confirmed')
    build_status = models.CharField(max_length=20, choices=BUILD_STATUS_CHOICES, default='in_progress')
    build_payment_amount = models.IntegerField(default=0)
    build_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            today = timezone.now().date()
            month = today.strftime('%m')
            day = today.strftime('%d')
            year = today.strftime('%Y')
            
            # Find the highest existing number in the system
            last_reservation = BookedPackage.objects.order_by('-reservation_number').first()
            
            if last_reservation:
                # Extract the last 4 digits from the existing reservation number
                last_number = int(last_reservation.reservation_number[-4:])
                new_number = last_number + 1
            else:
                # Start from 1000 if no reservations exist
                new_number = 1000
                
            self.reservation_number = f"RN{month}{day}{year}{new_number:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.reservation_number}"
    
    def get_build_status_display(self):
        """
        Returns the human-readable status label.
        You can customize this if you need special logic.
        """
        return dict(self.BUILD_STATUS_CHOICES).get(self.build_status, self.build_status)
    
    @property
    def BUILD_TYPE_CHOICES_index(self):
        for index, (value, label) in enumerate(self.BUILD_TYPE_CHOICES):
            if value == self.build_type:
                return index
        return 0
    


class PostPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False)
    rn_number = models.ForeignKey(BookedPackage, on_delete=models.CASCADE, to_field='reservation_number', related_name='payments')
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    regarding = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50, default="stripe", blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="usd", blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    package_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        db_table = 'payment'


class PostOrderStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(PostPayment, on_delete=models.CASCADE, related_name="order_statuses")
    status = models.CharField(max_length=255, blank=True, null=True)
    position = models.PositiveIntegerField()  # Defines the order of steps
    is_active = models.BooleanField(default=False)
    status_updated_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["position"]  # Ensures steps are retrieved in correct order
        db_table = 'order_status'

    def __str__(self):
        return f"{self.status} - {'Active' if self.is_active else 'Inactive'}"

    # Signal to create statuses when an order is created
    @receiver(post_save, sender=PostPayment)
    def create_order_statuses(sender, instance, created, **kwargs):
        if created:  # Only create statuses for new orders
            for index, status in enumerate(DEFAULT_STATUSES, start=1):
                PostOrderStatus.objects.create(
                    payment=instance,
                    status=status["name"],
                    position=index,
                    is_active=status["is_active"]
                )

class PostSubStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_status = models.ForeignKey(PostOrderStatus, on_delete=models.CASCADE, related_name="sub_statuses")
    name = models.CharField(max_length=255)
    position = models.PositiveIntegerField()  # Defines sub-status order
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        db_table = 'order_sub_status'

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
    

class BookedPackageImage(models.Model):
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
    
    booked_package = models.ForeignKey(
        BookedPackage,
        on_delete=models.CASCADE,
        related_name='images'
    )
    build_type = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to='booked_package_images/%Y/%m/%d/',
        blank=True,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Booked Package Image'
        verbose_name_plural = 'Booked Package Images'

    def get_build_type_display(self):
        """
        Returns the human-readable status label.
        You can customize this if you need special logic.
        """
        return dict(self.BUILD_TYPE_CHOICES).get(self.build_type, self.build_type)

    def __str__(self):
        return f"Image for {self.booked_package.reservation_number} - {self.get_build_type_display()}"
    

class ReservationNewFeatures(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booked_package = models.ForeignKey(BookedPackage, on_delete=models.CASCADE, related_name='new_features')
    features = models.TextField(help_text="Describe the new features to be added")
    feature_id =   models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"New features for {self.booked_package.reservation_number} - {self.status}"
    
class ReservationFeaturesPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('online_payment', 'Online Payment'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation_feature = models.ForeignKey(ReservationNewFeatures, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for feature {self.reservation_feature.id} - {self.payment_status}"
    
    class Meta:
        ordering = ['-payment_date']
        
    @property
    def is_completed(self):
        return self.payment_status == 'completed'
        
    @property
    def booked_package(self):
        """Shortcut to access the booked package associated with this payment"""
        return self.reservation_feature.booked_package
    





class LearnMoreContent(models.Model):
    car = models.ForeignKey(PostNavItem, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)
    subheading = models.CharField(max_length=255)
    title_image = models.ImageField(upload_to='learn_more_images/')
    title_image_mobile = models.ImageField(upload_to='learn_more_images/')
    title_image_front = models.ImageField(upload_to='learn_more_images/')
    # Car stats fields
    acceleration = models.CharField(max_length=20, blank=True, null=True)  # e.g., "3.9"
    acceleration_unit = models.CharField(max_length=10, blank=True, null=True, default="s")
    acceleration_desc = models.CharField(max_length=100, blank=True, null=True, default="Acceleration 0 - 100 km/h with Sport Chrono Package")
    power_kw = models.CharField(max_length=10, blank=True, null=True)  # e.g., "290"
    power_ps = models.CharField(max_length=10, blank=True, null=True)  # e.g., "394"
    power_desc = models.CharField(max_length=100, blank=True, null=True, default="Power (kW)/Power (PS)")
    top_speed = models.CharField(max_length=10, blank=True, null=True)  # e.g., "294"
    top_speed_unit = models.CharField(max_length=10, blank=True, null=True, default="km/h")
    top_speed_desc = models.CharField(max_length=100, blank=True, null=True, default="Top speed")
    # Additional image fields
    image1 = models.ImageField(upload_to='learn_more_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='learn_more_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='learn_more_images/', blank=True, null=True)
    # Additional text fields
    text1 = models.TextField(blank=True, null=True)
    text2 = models.TextField(blank=True, null=True)
    text3 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.car.title} - {self.subheading}"