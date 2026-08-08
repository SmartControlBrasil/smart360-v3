---
description: Constituicao arquitetural obrigatoria do Smart360 v3
alwaysApply: true
---

# Smart360 v3 - Architecture Constitution

Estas regras sao obrigatorias para qualquer alteracao neste repositorio.

## 1. Arquitetura

O Smart360 v3 utiliza:

- Modular Monolith
- Hexagonal Architecture
- Pragmatic Domain-Driven Design
- Ports and Adapters
- PostgreSQL
- Django
- Python

Nao transformar o sistema em microservicos sem decisao arquitetural explicita.

## 2. Principio fundamental

Django e framework e adapter do Smart360.

Django nao e o dominio do Smart360.

As regras fundamentais do negocio devem existir independentemente de:

- Django ORM
- PostgreSQL
- HTTP
- REST
- frontend
- OpenAI
- Gemini
- APIs externas
- servicos de terceiros

## 3. Camadas

Cada bounded context pode possuir:

domain/
application/
infrastructure/
interfaces/

### domain

Contem:

- entities
- value objects
- enums de dominio
- regras de negocio
- policies
- domain services
- exceptions

Domain deve ser Python puro sempre que possivel.

Domain NAO pode importar Django.

Domain NAO pode conhecer ORM.

Domain NAO pode conhecer HTTP.

Domain NAO pode acessar banco diretamente.

Domain NAO pode chamar APIs externas diretamente.

### application

Contem:

- use cases
- ports
- repository protocols
- application services
- DTOs quando necessarios
- orchestration

Application pode depender de domain.

Application nao deve depender de adapters concretos.

### infrastructure

Contem adapters concretos:

- Django ORM
- PostgreSQL
- repositories
- OpenAI
- Gemini
- email
- storage
- cache
- APIs externas
- mensageria

Infrastructure pode depender de application e domain.

### interfaces

Contem:

- views
- APIs
- controllers
- Django Admin
- serializers
- forms
- CLI

Interfaces chamam use cases.

Views nao devem concentrar regras de negocio.

## 4. Dependencias permitidas

Direcao principal:

interfaces -> application -> domain

Infrastructure implementa contratos definidos pela aplicacao ou dominio.

Nunca permitir:

domain -> Django
domain -> infrastructure
domain -> HTTP
domain -> OpenAI
domain -> Gemini

## 5. Persistencia

Banco oficial:

PostgreSQL.

Nao substituir PostgreSQL.

Nao introduzir SQLite como banco principal.

Entidades principais devem utilizar UUID.

Django Models representam persistencia.

Django Models nao sao automaticamente entidades de dominio.

Quando houver entidade de dominio separada, repository/adapters convertem:

Domain Entity <-> Django Model <-> PostgreSQL

## 6. Identidade

Existe usuario customizado.

Nunca substituir AUTH_USER_MODEL.

Nunca criar relacionamento direto com django.contrib.auth.models.User.

Usar settings.AUTH_USER_MODEL ou get_user_model quando apropriado.

IDs de usuarios e entidades principais utilizam UUID.

## 7. Multi-tenancy

Regra fundamental:

User != Organization

Relacao:

User -> Membership -> Organization

Um User pode participar de varias Organizations.

Uma Organization pode possuir varios Users.

Membership representa o vinculo organizacional.

Nao adicionar organization_id diretamente ao User para substituir Membership.

Toda operacao tenant-scoped deve possuir isolamento explicito.

## 8. Contextos atuais

Existem:

- identity
- organizations
- memberships

## 9. Contextos previstos

Podem existir futuramente, conforme necessidade real:

- marketplace
- providers
- service_requests
- matching
- reputation
- ai
- learning
- rewards
- advertising
- growth

Nao criar modulos apenas porque estao previstos.

## 10. Marketplace

Marketplace representa o catalogo de capacidades/servicos.

Entidades iniciais previstas:

- ServiceCategory
- Service

Nao confundir:

User com Provider
Organization com Provider
Provider com Service
Service com ServiceRequest

## 11. Providers

Possiveis conceitos futuros:

- Provider
- ProviderService
- ProviderLocation
- ProviderCredential
- ProviderAvailability
- ProviderExperience

A modelagem detalhada deve ser decidida antes da implementacao.

Nao antecipar schema complexo.

## 12. Service Requests

ServiceRequest representa uma necessidade do cliente.

Fluxo conceitual:

Customer Need
-> ServiceRequest
-> Intent Understanding
-> Matching
-> Provider Candidates

ServiceRequest nao e Service.

## 13. Matching

Matching e um contexto estrategico.

Fluxo esperado:

ServiceRequest
-> Candidate Retrieval
-> Eligibility
-> Scoring
-> Ranking
-> Explanation

Primeira implementacao deve ser:

- deterministica
- explicavel
- mensuravel
- testavel

Possiveis sinais:

- specialty_match
- location_match
- reputation
- availability
- experience
- response_rate

Os pesos nao devem ser tratados como definitivos sem decisao explicita.

## 14. Inteligencia Artificial

O Smart360 nao precisa criar LLM proprio inicialmente.

LLMs sao providers externos.

Toda integracao deve estar atras de ports e adapters.

Exemplos conceituais:

IntentClassifier
OpenAIIntentClassifier
GeminiIntentClassifier

Domain nunca importa SDK de LLM.

Resultados de IA devem ser validados antes de serem aceitos pelo dominio.

IA pode auxiliar:

- classificacao
- extracao de entidades
- normalizacao
- busca semantica
- embeddings
- explicacao

IA nao deve inicialmente substituir todo mecanismo decisorio de matching.

## 15. Reputation

Reputation deve ser baseada em evidencias.

Possiveis sinais:

- reviews
- ratings
- servicos concluidos
- response time
- complaints
- credentials
- experience
- repeat customers
- cancellations

Evitar score inexplicavel.

## 16. Learning

O sistema podera identificar gaps de capacidade e recomendar treinamento.

Fluxo conceitual:

Provider
-> Skill Gap
-> Training
-> Improved Capability
-> Better Opportunities

Learning deve permanecer separado de Marketplace.

## 17. Rewards

Recompensas devem incentivar comportamentos desejaveis:

- qualidade
- resposta
- conclusao
- confiabilidade
- aprendizado
- colaboracao

Nao implementar reinforcement learning complexo prematuramente.

Primeiro registrar eventos e feedbacks corretamente.

## 18. Advertising

Publicidade deve ser um modulo desacoplado do core.

Possiveis conceitos:

- Advertiser
- Campaign
- Ad
- Audience
- Placement
- Impression
- Click
- Conversion
- Budget

Nao acoplar publicidade ao dominio principal do marketplace.

## 19. Eventos e dados

Eventos futuros podem incluir:

- search_performed
- service_request_created
- provider_shown
- provider_clicked
- match_generated
- lead_created
- provider_contacted
- job_started
- job_completed
- review_submitted
- course_started
- course_completed
- ad_impression
- ad_clicked
- conversion

Nao introduzir event sourcing sem necessidade concreta.

## 20. Geografia

PostGIS podera ser adotado quando matching geografico exigir.

Nao adicionar antecipadamente.

## 21. Busca semantica

pgvector podera ser adotado para:

- semantic search
- provider search
- service search
- intent similarity
- RAG
- semantic matching

Nao tornar pgvector requisito do MVP sem necessidade.

## 22. Autorizacao

Distinguir claramente:

- Authentication
- Authorization
- Membership
- Role
- Ownership

Usuario autenticado nao significa usuario autorizado.

Permissoes globais do Django nao substituem autorizacao organizacional.

## 23. Integridade

Utilizar constraints e indexes no banco quando apropriado.

Nao depender apenas de validacao no frontend.

Regras estruturais importantes devem ser protegidas tambem no PostgreSQL.

## 24. Auditoria

Operacoes importantes devem evoluir para serem auditaveis.

Exemplos:

- criacao
- atualizacao
- exclusao
- mudanca de role
- mudanca de permissao
- matching
- conversoes
- operacoes administrativas

Nao adicionar sistema complexo de auditoria fora do escopo de uma tarefa.

## 25. Seguranca

Nunca:

- salvar secrets no Git
- hardcodar API keys
- hardcodar senhas de producao
- logar tokens
- expor credenciais
- confiar em IDs de cliente sem autorizacao
- modificar .env sem instrucao explicita

## 26. Django

Usar Django principalmente como:

- ORM
- migrations
- auth
- admin
- HTTP
- middleware
- integracao

Evitar fat models.

Evitar fat views.

Preferir casos de uso explicitos.

## 27. Migrations

Nunca editar migration aplicada para corrigir schema.

Criar nova migration.

Antes de migrations:

python manage.py check

Quando gerar migration, inspecionar antes de aplicar.

Quando nenhuma migration deveria existir:

python manage.py makemigrations --check

## 28. Testes

Priorizar testes de:

1. regras de dominio
2. casos de uso
3. repositories
4. integracoes criticas
5. isolamento multi-tenant
6. autorizacao

Testes de dominio devem evitar Django sempre que possivel.

## 29. Escopo

Nao realizar:

- limpeza geral
- renomeacao generalizada
- refatoracao nao solicitada
- atualizacao de dependencias nao relacionada
- mudancas esteticas arbitrarias

Resolver a tarefa solicitada preservando o restante.

## 30. Dependencias externas

Antes de adicionar biblioteca:

1. verificar se Python ou Django ja resolve
2. justificar necessidade
3. avaliar manutencao
4. avaliar seguranca
5. evitar dependencias para problemas triviais

## 31. Git

Sem autorizacao explicita, nao executar:

- git commit
- git push
- git reset --hard
- git clean -fd

Preservar alteracoes pre-existentes.

## 32. Producao

Uma tarefa local nao autoriza:

- SSH em producao
- deploy
- restart de services
- migration em producao
- alteracao DNS
- alteracao de webserver

Producao exige instrucao explicita.

## 33. Desenvolvimento incremental

Preferir:

small coherent change -> validation -> next change

Evitar:

large rewrite -> debugging loop

## 34. Definition of Done

Uma implementacao esta concluida quando:

- requisito foi atendido
- arquitetura foi preservada
- contratos foram mantidos
- python manage.py check passa
- migrations estao coerentes
- testes relevantes passam
- nao ha alteracoes fora de escopo

## 35. Conflitos

Se uma solicitacao conflitar com esta constituicao:

1. nao contornar silenciosamente
2. identificar a regra conflitante
3. explicar impacto
4. propor alternativa compativel
5. solicitar decisao somente quando realmente necessaria
