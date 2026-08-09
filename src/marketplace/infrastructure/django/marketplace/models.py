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


class ServiceRequestModel(models.Model):
    class Status(models.TextChoices):
        CAPTURED = "captured", "Captured"
        QUALIFYING = "qualifying", "Qualifying"
        QUALIFIED = "qualified", "Qualified"
        OPEN = "open", "Open"
        CANCELLED = "cancelled", "Cancelled"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    organization = models.ForeignKey(
        OrganizationModel,
        on_delete=models.PROTECT,
        related_name="service_requests",
    )
    service = models.ForeignKey(
        ServiceModel,
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    raw_description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CAPTURED,
    )
    requester_name = models.CharField(
        max_length=255,
        default="",
        blank=True,
    )
    requester_email = models.EmailField(
        default="",
        blank=True,
    )
    requester_phone = models.CharField(
        max_length=50,
        default="",
        blank=True,
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_service_requests"
        indexes = [
            models.Index(
                fields=["organization", "status"],
                name="mkt_sr_org_status_idx",
            ),
            models.Index(
                fields=["service", "status"],
                name="mkt_sr_srv_status_idx",
            ),
        ]


class OpportunityModel(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    service_request = models.OneToOneField(
        ServiceRequestModel,
        on_delete=models.PROTECT,
        related_name="opportunity",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    max_accesses = models.PositiveIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunities"
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="mkt_opp_st_cr_idx",
            ),
        ]


class OpportunityAccessModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    opportunity = models.ForeignKey(
        OpportunityModel,
        on_delete=models.PROTECT,
        related_name="accesses",
    )
    provider = models.ForeignKey(
        ProviderModel,
        on_delete=models.PROTECT,
        related_name="opportunity_accesses",
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunity_accesses"
        constraints = [
            models.UniqueConstraint(
                fields=["opportunity", "provider"],
                name="mkt_opp_acc_uniq",
            ),
        ]


class OpportunityInvitationModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    opportunity = models.ForeignKey(
        OpportunityModel,
        on_delete=models.PROTECT,
        related_name="invitations",
    )
    provider = models.ForeignKey(
        ProviderModel,
        on_delete=models.PROTECT,
        related_name="opportunity_invitations",
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunity_invitations"
        constraints = [
            models.UniqueConstraint(
                fields=["opportunity", "provider"],
                name="mkt_opp_inv_uniq",
            ),
        ]


class OpportunityInterestModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    invitation = models.OneToOneField(
        OpportunityInvitationModel,
        on_delete=models.PROTECT,
        related_name="interest",
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunity_interests"


class EconomicSettlementModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    interest = models.OneToOneField(
        OpportunityInterestModel,
        on_delete=models.PROTECT,
        related_name="economic_settlement",
    )
    method = models.CharField(max_length=50)
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)
    pricing_source = models.CharField(max_length=100, null=True, blank=True)
    pricing_configuration_id = models.UUIDField(null=True, blank=True)
    pricing_resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_economic_settlements"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_minor__gte=0),
                name="mkt_settlement_amount_gte_zero",
            )
        ]


class CreditWalletModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    organization = models.OneToOneField(
        OrganizationModel,
        on_delete=models.PROTECT,
        related_name="credit_wallet",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_credit_wallets"


class CreditLedgerEntryModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    wallet = models.ForeignKey(
        CreditWalletModel,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    direction = models.CharField(max_length=20)
    units = models.BigIntegerField()
    reason = models.CharField(max_length=255)
    reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_credit_ledger_entries"
        indexes = [
            models.Index(fields=["wallet", "created_at"], name="mkt_wallet_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(units__gt=0),
                name="mkt_credit_ledger_units_gt_zero",
            )
        ]


class OpportunityUnlockPricingConfigurationModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    scope = models.SlugField(max_length=50, unique=True)
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunity_unlock_pricing_configurations"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_minor__gt=0),
                name="mkt_unlock_price_amount_gt_zero",
            ),
        ]
        indexes = [
            models.Index(
                fields=["scope", "is_active"],
                name="mkt_unl_price_scope_act",
            ),
        ]


class OpportunityContactReadAuditModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    authenticated_user_id = models.UUIDField()
    provider_id = models.UUIDField()
    opportunity_id = models.UUIDField()
    service_request_id = models.UUIDField()
    action = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "marketplace_opportunity_contact_read_audits"
        indexes = [
            models.Index(
                fields=["provider_id", "created_at"],
                name="mkt_opp_cr_prov_idx",
            ),
            models.Index(
                fields=["opportunity_id", "created_at"],
                name="mkt_opp_cr_opp_idx",
            ),
        ]
