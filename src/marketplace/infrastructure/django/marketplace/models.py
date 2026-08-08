import uuid

from django.db import models

from src.organizations.infrastructure.django.organizations.models import (
    OrganizationModel,
)


class ServiceCategoryModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_service_categories"

    def __str__(self):
        return self.name


class ServiceModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    category = models.ForeignKey(
        ServiceCategoryModel,
        on_delete=models.PROTECT,
        related_name="services",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_services"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="marketplace_services_category_slug_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["category", "is_active"],
                name="mkt_srv_cat_active_idx",
            ),
        ]

    def __str__(self):
        return self.name


class ProviderModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    organization = models.ForeignKey(
        OrganizationModel,
        on_delete=models.PROTECT,
        related_name="marketplace_providers",
    )
    display_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_providers"
        indexes = [
            models.Index(
                fields=["organization", "is_active"],
                name="mkt_prv_org_active_idx",
            ),
        ]

    def __str__(self):
        return self.display_name


class ProviderServiceModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    provider = models.ForeignKey(
        ProviderModel,
        on_delete=models.PROTECT,
        related_name="provider_services",
    )
    service = models.ForeignKey(
        ServiceModel,
        on_delete=models.PROTECT,
        related_name="provider_services",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_provider_services"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "service"],
                name="mkt_prv_srv_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["provider", "is_active"],
                name="mkt_ps_prv_act_idx",
            ),
            models.Index(
                fields=["service", "is_active"],
                name="mkt_ps_srv_act_idx",
            ),
        ]
