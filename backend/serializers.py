from rest_framework import serializers
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
    CustomUser,
)

class LandingPageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLandingPageImages
        fields = ['id', 'section', 'title', 'subtitle', 'image', 'web_image', 'is_active', 'position']

class NavItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNavItem
        fields = ['id', 'title', 'slug', 'content', 'is_active', 'position']

# class PackageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostPackage
#         fields = ['id', 'name', 'description', 'amount_due', 'image', 'is_active', 'position']

class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNavItem
        fields = ['id', 'title', 'slug', 'content', 'estimated_delivery', 'is_active']

class DynamicPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicPackages
        fields = ['id', 'name', 'description', 'reserveAmount', 'package_type', 'baseAmount', 'discountAmount']

class FeatureSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturesSection
        fields = ['id', 'name', 'description']

class BookedPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedPackage
        fields = '__all__'
        read_only_fields = ('reservation_number',)
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_email'] = instance.user.email if instance.user else None
        representation['car_model_title'] = instance.car_model.title if instance.car_model else None
        return representation


class PackageFeatureRollerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureRoller
        fields = '__all__'  # or you can manually list fields if you want more control


class PackageFeatureRollerPlusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureRollerPlus
        fields = '__all__'


class PackageFeatureBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureBuilder
        fields = '__all__'