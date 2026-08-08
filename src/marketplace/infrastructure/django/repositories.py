from uuid import UUID

from src.marketplace.application.ports import (
    ServiceCategoryRepository,
    ServiceRepository,
)
from src.marketplace.domain.entities import Service, ServiceCategory
from src.marketplace.infrastructure.django.marketplace.models import (
    ServiceModel,
    ServiceCategoryModel,
)


class DjangoServiceCategoryRepository(ServiceCategoryRepository):
    @staticmethod
    def _to_entity(model: ServiceCategoryModel) -> ServiceCategory:
        return ServiceCategory(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, service_category: ServiceCategory) -> ServiceCategory:
        model, _ = ServiceCategoryModel.objects.update_or_create(
            id=service_category.id,
            defaults={
                "name": service_category.name,
                "slug": service_category.slug,
                "description": service_category.description,
                "is_active": service_category.is_active,
                "created_at": service_category.created_at,
                "updated_at": service_category.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(
        self,
        service_category_id: UUID,
    ) -> ServiceCategory | None:
        try:
            model = ServiceCategoryModel.objects.get(id=service_category_id)
        except ServiceCategoryModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_slug(self, slug: str) -> ServiceCategory | None:
        try:
            model = ServiceCategoryModel.objects.get(slug=slug)
        except ServiceCategoryModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active(self) -> list[ServiceCategory]:
        models = ServiceCategoryModel.objects.filter(
            is_active=True,
        ).order_by("created_at")

        return [self._to_entity(model) for model in models]


class DjangoServiceRepository(ServiceRepository):
    @staticmethod
    def _to_entity(model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, service: Service) -> Service:
        model, _ = ServiceModel.objects.update_or_create(
            id=service.id,
            defaults={
                "category_id": service.category_id,
                "name": service.name,
                "slug": service.slug,
                "description": service.description,
                "is_active": service.is_active,
                "created_at": service.created_at,
                "updated_at": service.updated_at,
            },
        )

        return self._to_entity(model)

    def get_by_id(self, service_id: UUID) -> Service | None:
        try:
            model = ServiceModel.objects.get(id=service_id)
        except ServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def get_by_category_and_slug(
        self,
        category_id: UUID,
        slug: str,
    ) -> Service | None:
        try:
            model = ServiceModel.objects.get(
                category_id=category_id,
                slug=slug,
            )
        except ServiceModel.DoesNotExist:
            return None

        return self._to_entity(model)

    def list_active_by_category(
        self,
        category_id: UUID,
    ) -> list[Service]:
        models = ServiceModel.objects.filter(
            category_id=category_id,
            is_active=True,
        ).order_by("name", "id")

        return [self._to_entity(model) for model in models]
