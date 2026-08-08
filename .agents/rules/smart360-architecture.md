# Smart360 V3 Workspace Architecture Rules

## Project identity

Smart360 v3 is:

- Python 3.12+
- Django 6.x
- PostgreSQL
- Modular Monolith
- Hexagonal Architecture
- pragmatic DDD
- Ports and Adapters
- UUID-based principal entities
- multi-tenant through Organization + Membership

## Dependency direction

Preserve:

interfaces -> application -> domain

infrastructure implements ports defined by application/domain.

Domain must remain pure Python.

Domain must not import:

- Django
- ORM
- HTTP
- serializers
- settings
- framework-specific objects

Application must not import Django ORM models.

## Framework principle

Register explicitly:

"Django is a framework used by Smart360.
Django is not Smart360."

Business rules must not live accidentally inside Django models, views or serializers.

## Marketplace separation

Preserve these distinct concepts:

- Service
- Provider
- ProviderService
- ServiceRequest
- Opportunity
- OpportunityAccess

Never merge their responsibilities without explicit architectural review.

## Matching vs monetization

Register prominently:

"Matching determines suitability.
Monetization determines commercial access and distribution among eligible candidates."

Payment, bid, subscription or credits must never make an technically ineligible Provider eligible.

## Technical eligibility

Candidate Discovery answers:

"Who can?"

Matching answers:

"Who is better?"

Monetization answers:

"Who commercially receives/accesses the opportunity and under what economic conditions?"

Never merge these questions.

## Scope discipline

For every task:

- inspect existing implementation first
- make the smallest coherent change
- preserve unrelated changes
- avoid speculative models
- avoid speculative fields
- avoid premature infrastructure
- do not add dependencies unless necessary
- do not modify previous migrations
- do not refactor unrelated code

## Git safety

Never perform without explicit user authorization:

- git commit
- git push
- git reset
- git clean
- force operations
- deploy

## Validation

For marketplace changes, normally validate with:

```bash
.venv/bin/python manage.py test \
  src.marketplace.domain.tests \
  src.marketplace.application.tests \
  src.marketplace.infrastructure.django.marketplace.tests \
  -v 2

.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
git diff --check
git status --short
git diff
```

Avoid generic Django discovery if a known namespace discovery issue remains.

## Existing architecture documents

Before significant architectural work, consult:

- [AGENTS.md](file:///home/marcelo/projetos/smart360-v3/AGENTS.md) (relative path: `../../AGENTS.md`)
- [SMART360_ARCHITECTURE.md](file:///home/marcelo/projetos/smart360-v3/docs/architecture/SMART360_ARCHITECTURE.md) (relative path: `../../docs/architecture/SMART360_ARCHITECTURE.md`)
- [DEVELOPMENT_WORKFLOW.md](file:///home/marcelo/projetos/smart360-v3/docs/architecture/DEVELOPMENT_WORKFLOW.md) (relative path: `../../docs/architecture/DEVELOPMENT_WORKFLOW.md`)

Keep this rule concise.

Antigravity workspace rules have a practical size limit, so do not copy entire architecture documents into it.
