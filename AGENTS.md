# Smart360 v3 - Agent Instructions

Este repositorio implementa o Smart360 v3.

## Leitura obrigatoria

Antes de alterar codigo, o agente DEVE ler:

1. .cursor/rules/smart360-architecture/RULE.md
2. docs/architecture/SMART360_ARCHITECTURE.md
3. docs/architecture/DEVELOPMENT_WORKFLOW.md

Para implementacao de funcionalidades, consultar tambem:

.cursor/skills/smart360-development/SKILL.md

## Regra fundamental

O Smart360 v3 utiliza:

- Python 3.12+
- Django 6.x
- PostgreSQL
- Arquitetura Hexagonal
- Modular Monolith
- Pragmatic Domain-Driven Design
- Ports and Adapters
- UUID para entidades principais
- Multi-tenancy baseado em Organization + Membership

Django e framework e adapter de infraestrutura.

Django NAO e o dominio do Smart360.

## Estrutura arquitetural

Cada bounded context pode possuir:

- domain/
- application/
- infrastructure/
- interfaces/

### Domain

Contem:

- entidades
- value objects
- enums
- regras de negocio
- politicas
- servicos de dominio
- excecoes de dominio

Domain nao pode depender de:

- Django
- ORM
- PostgreSQL
- HTTP
- APIs externas
- SDKs de LLM

### Application

Contem:

- use cases
- ports
- repository protocols
- application services
- orchestration

Application pode depender de domain.

Application nao deve depender de implementacoes concretas de infraestrutura.

### Infrastructure

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

Infrastructure pode depender de application e domain.

Domain nunca depende de infrastructure.

### Interfaces

Contem pontos de entrada:

- HTTP
- API
- views
- Django Admin
- forms
- serializers
- CLI

Interfaces devem chamar casos de uso.

Views nao devem concentrar regras de negocio.

## Direcao das dependencias

Fluxo principal:

interfaces -> application -> domain

Infrastructure implementa ports definidos pela aplicacao ou dominio.

Nunca permitir:

domain -> Django
domain -> infrastructure
domain -> HTTP
domain -> OpenAI
domain -> Gemini

## Banco de dados

Banco oficial:

PostgreSQL.

Nao introduzir SQLite como banco principal da aplicacao.

Entidades principais usam UUID.

Django Models representam persistencia.

Django Models nao devem automaticamente representar entidades do dominio.

Repositories realizam a traducao entre persistencia e dominio quando necessario.

## Identidade

O projeto possui usuario customizado.

Nunca substituir AUTH_USER_MODEL.

Nunca criar ForeignKey diretamente para django.contrib.auth.models.User.

Quando necessario utilizar:

settings.AUTH_USER_MODEL

ou:

get_user_model()

## Multi-tenancy

A relacao fundamental e:

User -> Membership -> Organization

User nao e Organization.

Um User pode participar de multiplas Organizations.

Uma Organization pode possuir multiplos Users.

Membership representa o vinculo e pode carregar:

- role
- status
- permissoes organizacionais futuras

Nunca adicionar organization_id diretamente ao User como substituto de Membership.

## Contextos existentes

Atualmente existem:

- identity
- organizations
- memberships

Contextos previstos:

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

Nao criar contextos futuros sem necessidade concreta.

## Marketplace

Marketplace representa o catalogo daquilo que pode ser ofertado ou solicitado.

Entidades iniciais previstas:

- ServiceCategory
- Service

User nao e automaticamente Provider.

Organization nao e automaticamente Provider.

Provider nao e Service.

ServiceRequest nao e Service.

## Matching

Matching e um bounded context estrategico.

A primeira versao deve ser:

- deterministica
- explicavel
- testavel
- mensuravel

Conceitos previstos:

- candidate retrieval
- eligibility
- scoring
- ranking
- explanation

IA pode auxiliar classificacao e enriquecimento.

IA nao deve substituir silenciosamente todas as regras de matching.

## Inteligencia Artificial

O Smart360 nao precisa criar seu proprio LLM.

LLMs sao providers externos.

Toda integracao com LLM deve ficar atras de ports e adapters.

O dominio nunca deve importar SDK da OpenAI, Gemini ou equivalente.

Resultados gerados por IA devem ser validados antes de entrar no dominio.

## Antes de implementar

O agente deve:

1. Ler estas instrucoes.
2. Ler a documentacao arquitetural.
3. Inspecionar o codigo existente.
4. Executar git status --short.
5. Identificar o bounded context correto.
6. Identificar regras de negocio.
7. Verificar impacto multi-tenant.
8. Verificar impacto de autorizacao e seguranca.
9. Verificar impacto de schema.
10. Fazer a menor alteracao coerente possivel.

Nao iniciar automaticamente pela criacao de models.

Primeiro entender o dominio.

## Validacao

Apos uma implementacao executar, quando aplicavel:

python manage.py check

Quando nenhuma migration deveria existir:

python manage.py makemigrations --check

Executar testes relacionados a alteracao.

Se houver alteracao de schema:

1. gerar migration
2. inspecionar migration
3. relatar migration
4. aplicar somente quando apropriado ao ambiente

## Alteracoes existentes

Preservar alteracoes pre-existentes fora do escopo da tarefa.

Nunca sobrescrever trabalho existente silenciosamente.

## Proibicoes

Sem autorizacao explicita, NAO:

- transformar o sistema em microservicos
- substituir PostgreSQL
- substituir Django
- remover o usuario customizado
- alterar AUTH_USER_MODEL
- colocar regras centrais de negocio em Django Models
- colocar regras centrais de negocio em views
- importar Django dentro de domain
- chamar LLM diretamente de domain
- adicionar dependencias desnecessarias
- editar migration ja aplicada
- apagar codigo apenas por parecer desnecessario
- executar refatoracao generalizada
- modificar .env
- expor secrets
- fazer deploy
- acessar producao
- executar commit
- executar push
- executar git reset --hard
- executar git clean -fd

## Seguranca

Nunca:

- salvar secrets no Git
- hardcodar API keys
- hardcodar senha de producao
- imprimir tokens
- expor credenciais em logs
- confiar em IDs enviados pelo cliente sem validar autorizacao

## Desenvolvimento incremental

Preferir:

small coherent change -> validation -> next coherent change

Evitar:

rewrite everything -> hope it works

## Critério de conclusao

Uma tarefa somente esta concluida quando:

- requisito foi atendido
- arquitetura foi preservada
- python manage.py check passa
- migrations estao coerentes
- testes relevantes passam
- nenhuma alteracao fora de escopo foi introduzida

## Relatorio obrigatorio

Ao concluir uma implementacao informar:

### Implementado

Resumo objetivo.

### Arquivos alterados

Lista dos arquivos alterados.

### Arquitetura

Explicar como domain, application, infrastructure e interfaces foram preservados.

### Banco

Informar migrations criadas ou ausencia de alteracao de schema.

### Validacao

Informar comandos executados e resultados.

### Pendencias

Somente pendencias reais.

### Nao alterado

Informar componentes sensiveis preservados quando relevante.

## Conflitos arquiteturais

Se uma solicitacao exigir violar estas regras, nao contornar silenciosamente.

Relatar:

1. regra conflitante
2. impacto tecnico
3. alternativa compativel
4. decisao necessaria
