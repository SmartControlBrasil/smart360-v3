---
name: smart360-development
description: Implementacao controlada de funcionalidades no Smart360 v3 respeitando arquitetura hexagonal, DDD pragmatico, modular monolith, PostgreSQL e multi-tenancy.
---

# Smart360 Development Skill

Use esta skill ao criar, alterar, corrigir ou expandir funcionalidades do Smart360 v3.

## Objetivo

Implementar software preservando:

- baixo acoplamento
- dominio independente
- regras explicitas
- testabilidade
- arquitetura hexagonal
- bounded contexts claros
- seguranca
- multi-tenancy
- auditabilidade
- evolucao incremental

## 1. Inicio obrigatorio

Antes de editar qualquer arquivo:

1. ler AGENTS.md
2. ler .cursor/rules/smart360-architecture/RULE.md
3. ler docs/architecture/SMART360_ARCHITECTURE.md
4. ler docs/architecture/DEVELOPMENT_WORKFLOW.md
5. executar git status --short
6. executar git branch --show-current
7. executar python manage.py check
8. inspecionar arquivos relacionados a tarefa

Preservar qualquer alteracao pre-existente fora do escopo.

## 2. Entender a tarefa

Antes de implementar, identificar:

- objetivo funcional
- bounded context responsavel
- entidades afetadas
- regras de negocio
- dados necessarios
- dependencias externas
- impacto multi-tenant
- impacto em autorizacao
- impacto em seguranca
- impacto em schema
- migrations necessarias
- testes necessarios

Nao iniciar automaticamente por models.py.

Primeiro entender o dominio.

## 3. Escolher o bounded context

Utilizar contexto existente quando a responsabilidade ja pertencer a ele.

Contextos atuais:

- identity
- organizations
- memberships

Contextos previstos, somente quando necessarios:

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

Nao criar novo bounded context para uma responsabilidade trivial.

Nao misturar responsabilidades claramente distintas no mesmo contexto apenas por conveniencia.

## 4. Estrutura preferencial

Quando aplicavel:

context/
  domain/
  application/
  infrastructure/
  interfaces/

Criar somente diretorios e arquivos necessarios para a tarefa atual.

## 5. Domain

Quando houver regra de negocio real, modelar primeiro o dominio.

Arquivos possiveis:

- domain/entities.py
- domain/value_objects.py
- domain/enums.py
- domain/services.py
- domain/policies.py
- domain/exceptions.py

Nao criar todos automaticamente.

Domain deve ser Python puro sempre que possivel.

Domain nao pode importar:

- django
- django.db
- django.http
- django.conf
- DRF
- OpenAI SDK
- Gemini SDK
- adapters de infraestrutura

Exemplo conceitual de entidade:

from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True)
class Example:
    id: UUID
    name: str

Entidades devem possuir comportamento quando houver regra apropriada.

Evitar entidades que sejam apenas espelhos desnecessarios de tabela sem significado de dominio.

## 6. Value Objects

Criar value object quando um conceito possuir:

- validacao propria
- invariantes
- semantica propria
- igualdade por valor

Exemplos futuros possiveis:

- Money
- Location
- Score
- EmailAddress
- ServiceIntent

Nao criar value objects por estetica arquitetural.

## 7. Application

Application coordena casos de uso.

Arquivos possiveis:

- application/ports.py
- application/use_cases.py
- application/dtos.py

Application pode depender de domain.

Application nao deve depender diretamente de implementacao Django.

## 8. Ports

Criar port quando a aplicacao depender de algo externo.

Exemplos:

- repository
- LLM provider
- email sender
- storage
- geocoding
- payment provider
- external API

Preferir Protocol quando adequado.

Exemplo conceitual:

from typing import Protocol

class ExampleRepository(Protocol):
    def save(self, entity):
        ...

O use case depende do contrato.

Nao depende de DjangoExampleRepository diretamente.

## 9. Use Cases

Use cases representam acoes de negocio.

Preferir nomes explicitos:

- CreateOrganization
- AddMemberToOrganization
- CreateServiceCategory
- CreateService
- RegisterProvider
- CreateServiceRequest
- FindProviderCandidates
- RankProviderCandidates
- SubmitReview

Evitar nomes vagos:

- Manager
- Helper
- Utils
- Processor
- GenericService
- Handler sem contexto

Um use case deve possuir responsabilidade clara.

## 10. Infrastructure

Infrastructure implementa adapters concretos.

Exemplos:

- DjangoOrganizationRepository
- DjangoMembershipRepository
- OpenAIIntentClassifier
- GeminiIntentClassifier
- DjangoProviderRepository

Responsabilidades de repository:

- consultar ORM
- persistir dados
- traduzir Model para Domain Entity
- traduzir Domain Entity para persistencia
- encapsular detalhes do ORM

Nao colocar regra central do negocio em repository.

## 11. Django Models

Django Models sao modelos de persistencia.

Usar UUID em entidades principais.

Adicionar timestamps quando relevantes.

Usar constraints para integridade importante.

Usar indexes para consultas relevantes.

Para relacionamento com usuario:

settings.AUTH_USER_MODEL

Nao importar User diretamente de django.contrib.auth.models.

Nao substituir o custom User existente.

## 12. Interfaces

Interfaces representam entrada no sistema.

Podem incluir:

- views
- APIs
- controllers
- forms
- serializers
- Django Admin
- CLI

Fluxo desejado:

HTTP
-> interface
-> use case
-> port
-> adapter
-> PostgreSQL

Evitar:

HTTP
-> view com regra de negocio extensa
-> ORM diretamente

Consultas simples de leitura podem ser tratadas pragmaticamente quando nao houver regra de dominio relevante, desde que nao prejudiquem isolamento, seguranca ou arquitetura.

## 13. Multi-tenancy

Para toda nova feature perguntar:

Esta informacao pertence a uma Organization?

Se sim:

- modelar ownership explicitamente
- filtrar pelo tenant correto
- validar Membership
- validar autorizacao
- impedir acesso cross-tenant

Nunca depender apenas de organization_id enviado pelo frontend.

Nunca considerar usuario autenticado automaticamente autorizado.

## 14. Membership e Role

Distinguir:

- autenticacao
- membership
- role
- autorizacao
- ownership

Roles atuais:

- OWNER
- ADMIN
- MANAGER
- MEMBER

Nao inventar novos roles sem necessidade concreta.

Nao transformar roles em dezenas de constantes prematuramente.

Permissoes granulares poderao evoluir separadamente.

## 15. Marketplace

Quando implementar Marketplace:

Separar claramente:

ServiceCategory

representa classificacao de servicos.

Service

representa algo que pode ser ofertado/solicitado.

Provider

representa capacidade de fornecer servico.

ServiceRequest

representa demanda.

Nao misturar estes conceitos.

## 16. Providers

Antes de implementar Provider, determinar explicitamente se o provider representa:

- profissional individual
- Organization
- perfil operacional independente associado a um ou ambos

Nao decidir isso silenciosamente.

Se a tarefa exigir essa decisao e ela ainda nao existir, relatar alternativas antes de congelar schema estrutural.

## 17. Service Requests

ServiceRequest deve representar a necessidade do cliente.

A descricao natural pode coexistir com dados estruturados.

Exemplo conceitual:

descricao:
Preciso consertar uma IHM Mitsubishi em Guarulhos.

Dados estruturados futuros:

- intent
- category
- service
- manufacturer
- equipment
- problem
- urgency
- location

Dados estruturados gerados por IA devem ser validados.

## 18. Matching

Separar matching em responsabilidades:

1. candidate retrieval
2. eligibility
3. scoring
4. ranking
5. explanation

Nao colocar tudo dentro de um unico prompt de LLM.

Primeira implementacao deve ser deterministicamente testavel.

Scores devem ter motivo explicavel.

Exemplo conceitual de sinais:

- specialty_match
- location_match
- reputation
- availability
- experience
- response_rate

Nao congelar pesos sem requisito explicito.

## 19. IA

Para implementar funcionalidade de IA:

1. definir contrato
2. definir input
3. definir output estruturado
4. implementar adapter
5. validar resposta
6. lidar com erro do provider
7. evitar acoplamento ao fornecedor
8. registrar evidencias relevantes quando necessario

Nunca importar SDK de LLM em domain.

Nunca assumir que output de LLM e confiavel.

Preferir respostas estruturadas a texto livre para integracao de sistema.

## 20. Provider de LLM

O sistema deve permitir substituicao futura de provider.

Exemplo conceitual:

IntentClassifier
  -> OpenAIIntentClassifier
  -> GeminiIntentClassifier

Application conhece IntentClassifier.

Nao conhece necessariamente OpenAI.

## 21. PostGIS

Nao adicionar PostGIS antecipadamente.

Adicionar quando houver requisito real de:

- distancia
- raio
- proximidade
- areas geograficas
- matching espacial

Quando adotado, manter detalhes PostGIS em infrastructure.

## 22. pgvector

Nao adicionar pgvector antecipadamente.

Usar quando houver necessidade real de:

- semantic search
- embedding similarity
- semantic matching
- RAG
- knowledge retrieval

Domain nao deve depender do tipo VectorField.

## 23. Redis e Celery

Nao adicionar por padrao.

Considerar somente quando houver necessidade de:

- processamento assincrono
- fila
- retry
- tarefas demoradas
- scheduling
- cache distribuido

Nao adicionar infraestrutura para tarefas simples.

## 24. Reputation

Ao modelar reputation:

Preferir evidencias e eventos concretos.

Possiveis fontes:

- reviews
- jobs completed
- response time
- complaints
- credentials
- cancellations
- repeat customers

Evitar um unico campo score sem explicacao de origem.

## 25. Learning e Rewards

Nao antecipar sistemas complexos.

Primeiro modelar:

- eventos
- feedback
- comportamento
- resultados

Depois evoluir regras de recompensa.

Reinforcement learning nao deve ser aplicado apenas porque o projeto utiliza IA.

Deve existir problema mensuravel, estado, acao, recompensa e estrategia de avaliacao.

## 26. Advertising

Advertising deve permanecer desacoplado do core.

Possiveis conceitos futuros:

- Campaign
- Ad
- Placement
- Impression
- Click
- Conversion

Nao misturar ranking organico com publicidade sem regra explicita e transparencia.

## 27. Migrations

Antes de alterar schema:

python manage.py check

Depois de modificar models:

python manage.py makemigrations app_name

Inspecionar a migration gerada.

Nao editar migration aplicada.

Se nenhuma migration deveria existir:

python manage.py makemigrations --check

## 28. Dados existentes

Nao:

- deletar dados
- recriar database
- flush database
- apagar migrations
- resetar schema

sem autorizacao explicita.

## 29. Testes

Prioridade:

1. domain rules
2. use cases
3. repository adapters
4. authorization
5. multi-tenant isolation
6. integrations
7. HTTP interfaces

Testes de domain devem ser independentes de Django sempre que possivel.

Testar casos negativos, nao apenas happy path.

## 30. Testes multi-tenant

Para dados tenant-scoped, testar pelo menos:

- usuario autorizado na Organization correta
- usuario de outra Organization sem acesso
- usuario sem Membership sem acesso

Quando a feature possuir diferentes roles, testar roles relevantes.

## 31. Seguranca

Verificar:

- authorization
- mass assignment
- IDOR
- cross-tenant access
- secrets
- input validation
- output exposure
- logs

Nao retornar dados sensiveis desnecessarios em APIs.

## 32. Erros de dominio

Quando apropriado, preferir excecoes especificas.

Exemplos conceituais:

- OrganizationAlreadyExists
- MembershipAlreadyExists
- UnauthorizedOrganizationAccess
- InvalidServiceRequest

Nao criar hierarquia enorme de exceptions sem necessidade.

## 33. Novas dependencias

Antes de instalar uma dependencia:

1. verificar se biblioteca padrao resolve
2. verificar se Django resolve
3. justificar necessidade
4. verificar manutencao
5. verificar seguranca
6. verificar impacto operacional

Nao modificar requirements ou pyproject sem necessidade.

## 34. Refatoracao

Nao fazer refatoracao ampla enquanto implementa feature pequena.

Refatorar somente:

- codigo diretamente relacionado
- quando necessario para concluir corretamente
- mantendo escopo controlado

Relatar qualquer refatoracao relevante.

## 35. Git

Antes da alteracao:

git status --short

Depois da alteracao:

git diff --check
git status --short

Nao executar sem autorizacao:

- git commit
- git push
- git reset --hard
- git clean -fd

## 36. Producao

Nao:

- acessar VPS
- alterar service
- reiniciar Gunicorn
- alterar CyberPanel
- alterar OpenLiteSpeed
- alterar DNS
- executar migration de producao
- fazer deploy

sem solicitacao explicita.

## 37. Economia de execucao

Evitar loops desnecessarios.

Preferir:

diagnostico
-> alteracao direcionada
-> teste direcionado
-> validacao final

Nao rodar repetidamente uma suite completa se um teste especifico resolve durante desenvolvimento.

## 38. Escopo

Se a tarefa for:

implementar ServiceCategory

nao implementar automaticamente:

- Provider
- ServiceRequest
- Matching
- Reputation
- Advertising
- Payments
- Learning
- Rewards

Implementar apenas o incremento aprovado.

## 39. Decisoes arquiteturais

Se houver decisao estrutural duradoura com duas alternativas plausiveis, relatar:

Opcao A
- beneficios
- custos

Opcao B
- beneficios
- custos

Recomendacao
- motivo

Se a decisao for local, reversivel e claramente compatível com a arquitetura, implementar diretamente.

## 40. Validacao final

Ao concluir uma tarefa executar, quando aplicavel:

python manage.py check

Se nenhuma migration deve existir:

python manage.py makemigrations --check

Tambem executar:

git diff --check

Executar testes relacionados.

## 41. Relatorio final

Responder usando:

## Implementado

Resumo objetivo da alteracao.

## Arquivos alterados

Lista objetiva.

## Arquitetura

Explicar como a implementacao respeita:

- domain
- application
- infrastructure
- interfaces

## Banco

Informar:

- migration criada
ou
- sem alteracao de schema

## Validacao

Informar comandos executados e resultados.

## Pendencias

Somente pendencias reais.

## Nao alterado

Informar componentes sensiveis preservados, quando relevante.

## 42. Regra final

O objetivo nao e gerar a maior quantidade possivel de codigo.

O objetivo e produzir o menor incremento correto que fortalece o Smart360 sem comprometer sua arquitetura.
