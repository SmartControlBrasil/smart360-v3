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

## Marketplace Monetization and Opportunity Distribution

### 1. PRINCIPIO CENTRAL

O Smart360 nao deve usar apenas mensalidade fixa e tambem nao deve depender exclusivamente de leilao.

O modelo planejado e hibrido:

- cadastro gratuito
- assinatura opcional
- creditos
- cobranca por oportunidade comercial
- preco variavel/dinamico da oportunidade
- leilao somente quando houver concorrencia suficiente
- futuras fontes adicionais de monetizacao

A arquitetura deve ser desenhada desde o inicio para permitir essas modalidades sem acopla-las ao Matching Engine.

### 2. SEPARACAO ENTRE MATCHING E MONETIZACAO

Regra arquitetural obrigatoria:

Matching determina adequacao.

Monetization determina acesso e distribuicao comercial dentro dos candidatos elegiveis.

Pagamento, assinatura, creditos ou lance nunca devem transformar um Provider tecnicamente inadequado em candidato adequado.

Fluxo conceitual:

ServiceRequest
    |
    v
Candidate Discovery
    |
    v
Eligible Providers
    |
    +--> Matching / Quality
    |
    +--> Monetization / Distribution
    |
    v
Opportunity Access

O dinheiro pode influenciar distribuicao/prioridade comercial somente depois da elegibilidade minima.

### 3. CADASTRO GRATUITO

O Provider deve poder entrar no ecossistema sem mensalidade obrigatoria.

Objetivos:

- reduzir barreira de entrada
- aumentar liquidez do marketplace
- formar rapidamente base de fornecedores
- permitir construcao de reputacao
- permitir descoberta organica

Nao assumir que todo Provider sera assinante.

Nao tornar subscription obrigatoria no dominio Provider.

### 4. ASSINATURA OPCIONAL

O Smart360 podera oferecer planos recorrentes.

Exemplos conceituais:

- Free
- Pro
- Business
- Premium

Os valores nao estao definidos ainda.

Planos pagos poderao futuramente incluir beneficios como:

- creditos mensais
- desconto no custo das oportunidades
- alertas antecipados
- analytics
- ferramentas comerciais
- gestao de equipe
- CRM
- automacoes
- recursos de IA
- maior capacidade operacional
- recursos premium

Importante:

Nao hardcodar precos de planos na arquitetura central.

Pricing deve ser configuravel.

### 5. CREDITOS

O Smart360 podera possuir sistema de creditos.

Creditos poderao ser:

- comprados
- incluidos em assinatura
- concedidos promocionalmente
- ganhos por campanhas/recompensas futuras
- utilizados para desbloquear oportunidades

Nao implementar wallet/payment prematuramente.

Mas nao criar decisoes arquiteturais que impecam creditos no futuro.

### 6. OPORTUNIDADE COMERCIAL

ServiceRequest e Opportunity nao devem ser tratados necessariamente como a mesma coisa.

ServiceRequest representa a demanda/necessidade do solicitante.

Opportunity representa a exposicao/distribuicao comercial dessa demanda para Providers.

Essa distincao deve ser preservada para futura modelagem.

Exemplo:

ServiceRequest:
"Minha CNC esta com erro de encoder no eixo Y."

A partir dela o sistema podera criar uma Opportunity comercial distribuida para candidatos elegiveis.

Nao implementar Opportunity automaticamente apenas por esta atualizacao documental.

### 7. PRIVACIDADE ANTES DO DESBLOQUEIO

O Provider podera futuramente visualizar informacoes suficientes para avaliar a oportunidade sem necessariamente receber imediatamente os dados completos do solicitante.

Exemplo de informacoes possivelmente visiveis antes do desbloqueio:

- categoria
- servico
- problema
- regiao aproximada
- equipamento
- fabricante
- urgencia
- faixa estimada do trabalho
- qualidade/verificacao da demanda
- quantidade de interessados

Exemplos de informacoes que poderao permanecer protegidas ate autorizacao/desbloqueio:

- nome completo
- telefone
- WhatsApp
- e-mail
- endereco exato
- outros dados pessoais/comerciais sensiveis

Essa politica devera respeitar LGPD e principios de minimizacao de dados.

Nao implementar interface ou regras definitivas ainda.

### 8. COBRANCA POR OPORTUNIDADE

O Smart360 podera cobrar pelo acesso/desbloqueio de uma oportunidade comercial qualificada.

O objeto economico nao deve ser conceitualmente tratado como simples "clique".

Uma oportunidade pode ter valor muito superior a um clique publicitario porque ja representa intencao comercial estruturada.

Nao usar CPC como conceito central da arquitetura.

Usar conceitos proprios de marketplace, como:

- Opportunity
- OpportunityAccess
- PricingPolicy
- OpportunityPrice
- CreditCost
- Bid

Os nomes definitivos serao decididos nas respectivas sprints.

### 9. PRECO DINAMICO DA OPORTUNIDADE

O custo de uma Opportunity podera variar.

Possiveis sinais futuros:

- categoria
- servico
- ticket estimado
- urgencia
- localizacao
- oferta de Providers na regiao
- quantidade de candidatos
- concorrencia
- qualidade da demanda
- verificacao do solicitante
- probabilidade de conversao
- historico de conversoes
- escassez
- horario
- complexidade
- especializacao requerida

Exemplo conceitual:

base price
+ urgency
+ estimated economic value
+ scarcity
+ demand quality
+ competition
= opportunity price

Nao congelar formula ou pesos agora.

O pricing deve futuramente ser implementado atraves de politica/servico proprio e nao espalhado pelos models.

### 10. LEILAO

Leilao nao sera obrigatorio para todas as oportunidades.

Ele podera ser ativado somente quando fizer sentido economico, por exemplo:

- multiplos Providers elegiveis
- demanda concorrida
- oferta limitada de vagas
- oportunidade de maior valor

O Provider podera futuramente definir um bid maximo.

Mas o maior lance nao deve necessariamente vencer.

O Smart360 deve combinar adequacao/qualidade com elementos comerciais.

### 11. QUALITY BEFORE BID

Regra forte:

BID nao substitui QUALITY.

Um Provider incompativel tecnicamente nao entra no matching apenas porque paga mais.

Primeiro:

Eligibility.

Depois:

Matching Quality.

Depois:

Commercial Distribution.

Exemplo conceitual futuro:

- Technical Match
- Location
- Reputation
- Availability
- Experience
- Response Rate
- Commercial Bid

podem participar de uma decisao de distribuicao/ranking.

Os pesos nao estao definidos e nao devem ser hardcoded agora.

### 12. LIMITACAO DE ACESSOS A MESMA OPORTUNIDADE

O Smart360 nao deve vender indiscriminadamente a mesma oportunidade para dezenas de Providers.

Isso destroi:

- confianca
- taxa de conversao
- percepcao de valor
- reputacao do marketplace

Deve existir futuramente um limite configuravel de acessos/compradores por Opportunity.

Valor inicial conceitual para experimentacao:

3 Providers

Importante:

Esse numero nao e uma regra fixa de dominio neste momento.

Deve permanecer configuravel.

### 13. ESCASSEZ E DISTRIBUICAO

Uma Opportunity podera futuramente possuir:

- numero maximo de acessos
- quantidade de vagas restantes
- janela de disponibilidade
- preco atual
- preco minimo
- estado de distribuicao
- inicio/fim do leilao
- quantidade de interessados

Esses conceitos deverao ser modelados apenas quando chegarmos a sprint especifica.

Nao adicionar campos prematuros em ServiceRequest ou ProviderService.

### 14. MRR + REVENUE VARIABLE

O modelo hibrido busca combinar:

Receita recorrente:

- subscriptions / plans

com:

Receita variavel:

- credits
- opportunity unlock
- dynamic pricing
- auction/bid
- sponsored placement
- outros servicos

Isso evita depender exclusivamente de uma unica fonte de receita.

### 15. FUTURAS FONTES DE RECEITA

A arquitetura deve permanecer aberta para:

- assinaturas
- creditos
- oportunidade paga
- leilao
- comissao sobre contratacao
- anuncios patrocinados
- destaque de perfil
- premium AI
- cursos
- treinamentos
- certificacoes
- marketplace de produtos
- parceiros
- servicos financeiros
- seguros
- afiliados
- midia e videos patrocinados

Esses itens nao fazem parte do MVP atual.

Nao implementa-los antecipadamente.

### 16. IA E PRICING FUTURO

IA podera futuramente ajudar a estimar:

- qualidade da demanda
- ticket potencial
- intencao real de contratacao
- probabilidade de conversao
- complexidade
- urgencia
- fraude/spam
- valor esperado da oportunidade

Mas:

- IA nao deve controlar dinheiro sem politicas deterministicas/auditaveis
- precos e decisoes financeiras precisam ser explicaveis e auditaveis
- regras de fallback devem existir
- provider deve poder entender por que determinada cobranca ocorreu

Nao implementar IA de pricing agora.

### 17. TELEMETRIA ECONOMICA

Quando o modulo de monetizacao for construido, a arquitetura deve permitir registrar eventos como:

- opportunity_created
- opportunity_shown
- opportunity_unlocked
- opportunity_skipped
- bid_placed
- bid_won
- bid_lost
- credits_spent
- opportunity_contacted
- proposal_created
- conversion
- service_completed
- refund
- dispute

Isso permitira futuramente medir:

- conversion rate
- cost per opportunity
- cost per acquisition
- provider ROI
- marketplace take rate
- LTV
- CAC
- fill rate
- opportunity liquidity
- revenue per request

Nao implementar telemetria agora.

### 18. REGRAS PARA FUTURAS SPRINTS

Antes de implementar Candidate Discovery, Matching, Ranking ou Opportunity Distribution, verificar sempre:

1. A funcionalidade pertence a elegibilidade tecnica ou monetizacao?
2. Estamos misturando bid com capacidade tecnica?
3. Estamos introduzindo preco em entidade errada?
4. Estamos tornando subscription obrigatoria acidentalmente?
5. Estamos expondo dados privados antes do necessario?
6. Estamos permitindo compradores ilimitados para uma mesma demanda?
7. Estamos hardcodando precos ou pesos que deveriam ser politicas configuraveis?
8. Estamos criando dependencia de um gateway de pagamento no dominio?

Se qualquer resposta indicar acoplamento indevido, parar e revisar a arquitetura.

### 19. PRINCIPIO FINAL

Registrar em destaque:

"Matching determines suitability.
Monetization determines commercial access and distribution among eligible candidates."

Em portugues:

"Matching determina adequacao.
Monetizacao determina acesso e distribuicao comercial entre candidatos elegiveis."

E tambem:

"Complexidade economica nao deve contaminar o nucleo de elegibilidade tecnica."

### Atualizacao da sequencia de desenvolvimento

Apos ServiceRequest, a sequencia planejada passa conceitualmente a considerar:

- 01E - ServiceRequest - concluida
- 01F - Monetization Foundations / Opportunity Concepts
- 01G - Candidate Discovery
- 01H - Matching Score v1
- 01I - Opportunity Distribution / Auction

Essa sequencia ainda pode ser refinada conforme o dominio evoluir.

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
