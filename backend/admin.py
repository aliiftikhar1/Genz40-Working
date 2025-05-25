from django.contrib import admin
from django.contrib import messages
from adminsortable2.admin import SortableAdminMixin
from backend.models import (
    CustomUser, PostCommunity, PostReview, PostBlog, PostMeta, PostNavItem,
    PostPackage, PostPackageDetail, PostPackageFeature, PostPart, PostCharging,
    PostAccessories, PostPaint, PostImage, PostSubscribers, PostWheels,
    PostLandingPageImages, PostPayment, PostOrderStatus, PostSubStatus,
    CarConfiguration, BookedPackage, BookedPackageImage, DynamicPackages,
    FeaturesSection, PackageFeatureRoller, PackageFeatureRollerPlus,
    PackageFeatureBuilder, PostCommunityJoiners, PostContactUs,
    ReservationFeaturesPayment, ReservationNewFeatures, LearnMoreContent
)

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_image', 'social_user_image')}),
        ('Address', {'fields': ('street_address_1', 'street_address_2', 'city', 'state', 'country', 'zip_code', 'latitude', 'longitude')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_block', 'is_delete', 'is_email_verified', 'is_phone_number_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Review Admin
@admin.register(PostReview)
class PostReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('name', 'city', 'review')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)

# Blog Admin
@admin.register(PostBlog)
class PostBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'publish')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    ordering = ('-publish',)

# Meta Admin
@admin.register(PostMeta)
class PostMetaAdmin(admin.ModelAdmin):
    list_display = ('user', 'meta_title', 'page_title', 'created_at')
    search_fields = ('meta_title', 'meta_keywords', 'user__email')

# NavItem Admin with sorting
@admin.register(PostNavItem)
class PostNavItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    list_filter = ('is_active', 'parent')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('position',)

# Image Admin
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('nav_item', 'image', 'thumbnail')
    list_filter = ('nav_item',)
    search_fields = ('nav_item__title',)

# Package Admin with inlines
class PackageDetailsInline(admin.TabularInline):
    model = PostPackageDetail
    extra = 1
    classes = ('collapse',)

class PackageFeatureInline(admin.TabularInline):
    model = PostPackageFeature
    extra = 1
    classes = ('collapse',)

@admin.register(PostPackage)
class PackageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('nav_item', 'name', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('nav_item__title', 'name', 'description')
    inlines = [PackageDetailsInline, PackageFeatureInline]
    ordering = ('position',)

# Package Detail Admin
@admin.register(PostPackageDetail)
class PackageDetailAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'service_type', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'service_type', 'description')
    ordering = ('position',)

# Package Feature Admin
@admin.register(PostPackageFeature)
class PackageFeatureAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'name', 'value', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'name', 'value')
    ordering = ('position',)

# Parts Admin
@admin.register(PostPart)
class PackagePartsAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'parts_name', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'parts_name')
    ordering = ('position',)

# Charging Admin
@admin.register(PostCharging)
class PackageChargingAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'charging_name', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'charging_name')
    ordering = ('position',)

# Accessories Admin
@admin.register(PostAccessories)
class PackageAccessoriesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'accessories_name', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'accessories_name')
    ordering = ('position',)

# Paint Admin
@admin.register(PostPaint)
class PackagePaintAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'paint_name', 'amount', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'paint_name')
    ordering = ('position',)

# Wheels Admin
@admin.register(PostWheels)
class PostWheelsAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'wheel_name', 'wheel_amount', 'wheel_size', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    search_fields = ('package__name', 'wheel_name')
    ordering = ('position',)

# Landing Page Images Admin
@admin.register(PostLandingPageImages)
class PostLandingPageImagesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'section', 'tag', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    list_filter = ('section', 'tag', 'is_active')
    search_fields = ('title', 'subtitle')
    ordering = ('position',)

# Subscribers Admin
@admin.register(PostSubscribers)
class PostSubscribersAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'

# Community Admin
@admin.register(PostCommunity)
class PostCommunityAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at')
    search_fields = ('name', 'user__email')
    list_filter = ('is_active',)

# Community Joiners Admin
@admin.register(PostCommunityJoiners)
class PostCommunityJoinersAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    search_fields = ('user__email',)
    list_filter = ('is_active',)

# Contact Us Admin
@admin.register(PostContactUs)
class PostContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'car', 'created_at')
    search_fields = ('name', 'email', 'car')
    date_hierarchy = 'created_at'

# Car Configuration Admin
@admin.register(CarConfiguration)
class CarConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'car_model', 'exterior_color', 'total_price', 'is_saved', 'is_ordered', 'created_at')
    list_filter = ('car_model', 'is_saved', 'is_ordered')
    search_fields = ('user__email', 'car_model__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

# Dynamic Packages Admin
@admin.register(DynamicPackages)
class DynamicPackagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'car_model', 'baseAmount', 'discountAmount', 'reserveAmount', 'position', 'created_at')
    list_filter = ('package_type', 'car_model')
    search_fields = ('name', 'car_model__title')
    ordering = ('position',)
    list_editable = ('position',)

# Features Section Admin
@admin.register(FeaturesSection)
class FeaturesSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

# Package Feature Roller Admin with copy actions
@admin.register(PackageFeatureRoller)
class PackageFeatureRollerAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'type', 'price', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    list_filter = ('section', 'type', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    search_fields = ('name', 'section__name')
    actions = ['copy_to_roller_plus', 'copy_to_builder']
    
    def copy_to_roller_plus(self, request, queryset):
        count = 0
        for feature in queryset:
            if not PackageFeatureRollerPlus.objects.filter(name=feature.name, section=feature.section).exists():
                PackageFeatureRollerPlus.objects.create(
                    section=feature.section,
                    name=feature.name,
                    type=feature.type,
                    price=feature.price,
                    option1=feature.option1,
                    option2=feature.option2,
                    option1_price=feature.option1_price,
                    option2_price=feature.option2_price,
                    checked=feature.checked,
                    disabled=feature.disabled,
                    included=feature.included,
                    in_mark_I=feature.in_mark_I,
                    in_mark_II=feature.in_mark_II,
                    in_mark_IV=feature.in_mark_IV
                )
                count += 1
        messages.success(request, f'Successfully copied {count} features to Roller Plus')
    copy_to_roller_plus.short_description = "Copy selected features to Roller Plus"
    
    def copy_to_builder(self, request, queryset):
        count = 0
        for feature in queryset:
            if not PackageFeatureBuilder.objects.filter(name=feature.name, section=feature.section).exists():
                PackageFeatureBuilder.objects.create(
                    section=feature.section,
                    name=feature.name,
                    type=feature.type,
                    price=feature.price,
                    option1=feature.option1,
                    option2=feature.option2,
                    option1_price=feature.option1_price,
                    option2_price=feature.option2_price,
                    checked=feature.checked,
                    disabled=feature.disabled,
                    included=feature.included,
                    in_mark_I=feature.in_mark_I,
                    in_mark_II=feature.in_mark_II,
                    in_mark_IV=feature.in_mark_IV
                )
                count += 1
        messages.success(request, f'Successfully copied {count} features to Builder')
    copy_to_builder.short_description = "Copy selected features to Builder"

# Package Feature RollerPlus Admin
@admin.register(PackageFeatureRollerPlus)
class PackageFeatureRollerPlusAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'type', 'price', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    list_filter = ('section', 'type', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    search_fields = ('name', 'section__name')

# Package Feature Builder Admin
@admin.register(PackageFeatureBuilder)
class PackageFeatureBuilderAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'type', 'price', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    list_filter = ('section', 'type', 'checked', 'disabled', 'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    search_fields = ('name', 'section__name')

# Booked Package Admin
class BookedPackageImageInline(admin.TabularInline):
    model = BookedPackageImage
    extra = 1
    readonly_fields = ('uploaded_at',)

@admin.register(BookedPackage)
class BookedPackageAdmin(admin.ModelAdmin):
    list_display = ('reservation_number', 'user', 'car_model', 'package', 'price', 'status', 'build_type', 'build_status', 'created_at')
    list_filter = ('status', 'build_type', 'build_status', 'car_model', 'package')
    search_fields = ('reservation_number', 'user__email', 'car_model__title', 'package__name')
    readonly_fields = ('reservation_number', 'created_at', 'updated_at')
    inlines = [BookedPackageImageInline]
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('reservation_number', 'user', 'car_model', 'package', 'title')
        }),
        ('Details', {
            'fields': ('price', 'remaining_price', 'extra_features')
        }),
        ('Status', {
            'fields': ('status', 'build_type', 'build_status', 'build_payment_amount', 'build_message')
        }),
        ('Payment Percentages', {
            'fields': ('initial_payment_percentage', 'midway_payment_percentage', 'final_payment_percentage'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Booked Package Image Admin
@admin.register(BookedPackageImage)
class BookedPackageImageAdmin(admin.ModelAdmin):
    list_display = ('booked_package', 'build_type', 'uploaded_at')
    list_filter = ('build_type', 'uploaded_at')
    search_fields = ('booked_package__reservation_number',)
    readonly_fields = ('uploaded_at',)

# Payment Admin
@admin.register(PostPayment)
class PostPaymentAdmin(admin.ModelAdmin):
    list_display = ('rn_number', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'type', 'created_at')
    search_fields = ('rn_number__reservation_number', 'user__email', 'stripe_payment_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

# Order Status Admin
class SubStatusInline(admin.TabularInline):
    model = PostSubStatus
    extra = 1
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PostOrderStatus)
class PostOrderStatusAdmin(admin.ModelAdmin):
    list_display = ('payment', 'status', 'is_active', 'position', 'status_updated_date')
    list_filter = ('is_active', 'status')
    search_fields = ('payment__rn_number__reservation_number', 'status')
    list_editable = ('is_active', 'position')
    inlines = [SubStatusInline]
    ordering = ('position',)

# Sub Status Admin
@admin.register(PostSubStatus)
class PostSubStatusAdmin(admin.ModelAdmin):
    list_display = ('order_status', 'name', 'is_active', 'position')
    list_filter = ('is_active', 'order_status__status')
    search_fields = ('name', 'order_status__status')
    list_editable = ('is_active', 'position')
    ordering = ('position',)

# Reservation New Features Admin
class ReservationFeaturesPaymentInline(admin.TabularInline):
    model = ReservationFeaturesPayment
    extra = 1
    readonly_fields = ('payment_date', 'created_at')

@admin.register(ReservationNewFeatures)
class ReservationNewFeaturesAdmin(admin.ModelAdmin):
    list_display = ('booked_package', 'features', 'amount', 'status', 'created_at')
    list_filter = ('status', 'booked_package__car_model')
    search_fields = ('booked_package__reservation_number', 'features')
    inlines = [ReservationFeaturesPaymentInline]
    readonly_fields = ('created_at', 'updated_at')

# Reservation Features Payment Admin
@admin.register(ReservationFeaturesPayment)
class ReservationFeaturesPaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation_feature', 'amount', 'payment_status', 'payment_method', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('reservation_feature__booked_package__reservation_number', 'transaction_id')
    readonly_fields = ('payment_date', 'created_at', 'updated_at')
    date_hierarchy = 'payment_date'




from chat.models import ChatRoom, Message, ChatNotification

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'customer', 'admin', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('room_name', 'customer__email', 'admin__email')
    raw_id_fields = ('customer', 'admin')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'sender', 'timestamp')  # Removed 'is_read'
    list_filter = ('timestamp',)  # Removed 'is_read'
    search_fields = ('content', 'sender__email')
    raw_id_fields = ('chat_room', 'sender')

@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_room', 'count', 'last_updated')
    list_filter = ('last_updated',)
    raw_id_fields = ('user', 'chat_room')

@admin.register(LearnMoreContent)
class LearnMoreContentAdmin(admin.ModelAdmin):
    list_display = ('car', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('car__title',)


