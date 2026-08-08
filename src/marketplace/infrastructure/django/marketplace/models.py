import uuid

from django.db import models


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
