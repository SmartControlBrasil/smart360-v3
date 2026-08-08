# Smart360 v3 - Arquitetura de Referencia

Status: arquitetura inicial aprovada.

## 1. Proposito

O Smart360 v3 sera um ecossistema digital capaz de conectar:

necessidade + capacidade + oportunidade

O sistema nao sera apenas um catalogo de profissionais ou empresas.

Seu nucleo devera compreender uma necessidade, estrutura-la, identificar capacidades disponiveis e conectar demanda e oferta.

Exemplo de entrada:

Minha maquina CNC esta apresentando erro de encoder no eixo Y.

O Smart360 podera identificar futuramente:

- dominio: automacao industrial
- categoria: manutencao CNC
- equipamento: CNC
- componente: encoder
- eixo: Y
- problema relatado
- fabricante, quando conhecido
- localizacao
- urgencia

Depois podera localizar profissionais ou empresas adequados.

## 2. Visao central

O produto estrategico do Smart360 e:

motor de conexao entre intencao, capacidade e oportunidade

Fluxo conceitual:

Customer Need
-> Intent Understanding
-> Marketplace
-> Providers
-> Matching
-> Opportunity
-> Outcome
-> Reputation
-> Learning
-> Rewards

Outros contextos podem operar em paralelo:

- AI
- Advertising
- Growth
- Analytics

## 3. O que constitui vantagem competitiva

O ativo principal do Smart360 nao deve ser um LLM especifico.

LLMs podem ser substituidos.

A propriedade intelectual e vantagem defensavel devem estar principalmente em:

- workflows
- taxonomias
- dados historicos
- matching
- reputacao
- regras
- conhecimento acumulado
- relacionamentos
- outcomes
- sinais comportamentais
- UX
- inteligencia sobre oferta e demanda

## 4. Modelo de negocio

Fontes de receita possiveis incluem:

- assinaturas
- comissoes
- cobranca por lead
- planos premium
- destaque de providers
- publicidade
- campanhas patrocinadas
- recursos premium de IA
- cursos
- treinamento
- certificacoes
- marketplace
- servicos digitais
- produtos
- parcerias

A arquitetura nao deve depender de uma unica fonte de receita.

## 5. Stack inicial

Stack aprovada:

- Python 3.12+
- Django 6.x
- PostgreSQL 16+
- psycopg
- python-dotenv

Tecnologias candidatas futuras, somente mediante necessidade:

- PostGIS
- pgvector
- Redis
- Celery
- object storage
- mecanismo de busca especializado

Nao instalar infraestrutura futura antecipadamente.

## 6. Estilo arquitetural

O sistema utiliza:

Modular Monolith
+
Hexagonal Architecture
+
Pragmatic Domain-Driven Design
+
Ports and Adapters

Objetivos:

- simplicidade operacional
- fronteiras claras
- baixo acoplamento
- testabilidade
- evolucao incremental
- facilidade de substituicao de adapters
- possibilidade de extracao futura de servicos
- evitar complexidade distribuida prematura

## 7. Principio Django

Regra:

Django e um framework do Smart360.

Django nao e o Smart360.

Django deve atender principalmente:

- ORM
- migrations
- autenticacao
- admin
- HTTP
- middleware
- integracoes

As regras fundamentais de negocio devem permanecer fora do acoplamento direto ao framework sempre que fizer sentido.

## 8. Estrutura de bounded contexts

Estrutura conceitual:

src/
  identity/
  organizations/
  memberships/
  marketplace/
  providers/
  service_requests/
  matching/
  reputation/
  ai/
  learning/
  rewards/
  advertising/
  growth/

Nem todos estes modulos devem ser criados imediatamente.

Eles representam fronteiras candidatas conforme o produto evolui.

## 9. Estrutura interna

Cada bounded context pode possuir:

domain/
application/
infrastructure/
interfaces/

### Domain

Responsavel por:

- entidades
- value objects
- enums
- invariantes
- politicas
- regras de negocio
- domain services
- exceptions

Domain deve ser independente de Django sempre que possivel.

### Application

Responsavel por:

- use cases
- ports
- orchestration
- application services
- DTOs quando necessarios

Application coordena o dominio.

### Infrastructure

Responsavel por adapters concretos:

- Django ORM
- PostgreSQL
- repositories
- providers de IA
- email
- storage
- cache
- APIs externas

### Interfaces

Responsavel por entradas:

- HTTP
- API
- views
- Django Admin
- forms
- serializers
- CLI

## 10. Direcao de dependencias

Direcao principal:

interfaces -> application -> domain

Infrastructure implementa contracts/ports.

Nao permitir:

domain -> Django
domain -> infrastructure
domain -> HTTP
domain -> OpenAI
domain -> Gemini

## 11. Persistencia

Banco principal:

PostgreSQL.

Entidades principais utilizam UUID.

Django Model representa persistencia.

Domain Entity representa conceito e comportamento de dominio quando essa separacao agrega valor.

Repository faz a ponte:

Domain Entity
<-> Repository Adapter
<-> Django Model
<-> PostgreSQL

## 12. Identity

O contexto identity contem a identidade tecnica do usuario.

Ja existe User customizado baseado em AbstractUser.

Caracteristicas:

- UUID como primary key
- email unico
- timestamps
- integracao com Django Auth

AUTH_USER_MODEL deve ser preservado.

## 13. Organizations

Organization representa uma organizacao dentro do ecossistema.

Ja existem:

- Organization domain entity
- OrganizationRepository
- DjangoOrganizationRepository
- OrganizationModel
- CreateOrganization use case

Organization e independente de User.

## 14. Memberships

Membership representa a relacao entre User e Organization.

Relacao:

User
-> Membership
-> Organization

Roles iniciais:

- OWNER
- ADMIN
- MANAGER
- MEMBER

Um usuario pode pertencer a varias organizacoes.

Uma organizacao pode possuir varios usuarios.

Isso constitui a base do multi-tenancy organizacional.

## 15. Marketplace

Marketplace representa o catalogo do que pode ser ofertado ou solicitado.

Primeiras entidades planejadas:

- ServiceCategory
- Service

Exemplo conceitual:

Automacao Industrial
  - Manutencao CNC
  - Programacao de CLP
  - IHM
  - SCADA
  - Retrofit

Nao criar hierarquia excessivamente sofisticada no primeiro incremento.

## 16. Distincoes importantes

User != Organization

Organization != Provider

Provider != Service

Service != ServiceRequest

Membership != Permission

Authentication != Authorization

Estas distincoes devem permanecer claras durante a modelagem.

## 17. Providers

Provider representa capacidade de atender demanda.

Conceitos candidatos:

- Provider
- ProviderService
- ProviderLocation
- ProviderCredential
- ProviderAvailability
- ProviderExperience

Uma decisao estrutural ainda devera definir com precisao como profissional individual e empresa serao representados.

Essa decisao nao deve ser tomada silenciosamente durante uma implementacao incidental.

## 18. Service Requests

ServiceRequest representa a necessidade do cliente.

Exemplo:

Preciso consertar uma IHM Mitsubishi em Guarulhos.

Dados estruturados futuros podem conter:

- customer
- description
- category
- service
- manufacturer
- equipment
- problem
- urgency
- location
- structured_intent
- status

A descricao original deve ser preservavel.

Dados extraidos por IA nao devem substituir cegamente a entrada original.

## 19. Intent Understanding

A IA podera transformar linguagem natural em estrutura.

Exemplo conceitual de resultado:

intent = technical_service
category = industrial_automation
service = cnc_maintenance
manufacturer = mitsubishi
equipment = cnc
problem = servo_alarm
urgency = high

O output deve ser validado.

O dominio nao deve conhecer diretamente o provider de LLM.

## 20. Matching

Matching e parte estrategica da plataforma.

Pipeline previsto:

ServiceRequest
-> Candidate Retrieval
-> Eligibility
-> Scoring
-> Ranking
-> Explanation

Primeira versao deve ser explicavel e deterministica.

Sinais candidatos:

- specialty_match
- location_match
- reputation
- availability
- experience
- response_rate

Exemplo inicial de distribuicao conceitual:

- specialty: 30%
- location: 20%
- reputation: 20%
- availability: 10%
- experience: 10%
- response rate: 10%

Esses pesos nao sao definitivos.

Nao implementar como regra imutavel sem aprovacao.

## 21. Matching geografico

No futuro, localizacao sera relevante para:

- raio de atendimento
- distancia
- areas de cobertura
- proximidade
- ordenacao geografica

PostGIS e a tecnologia preferencial quando a necessidade surgir.

PostGIS nao deve ser habilitado apenas por antecipacao.

## 22. Matching semantico

pgvector podera futuramente apoiar:

- semantic search
- service similarity
- provider similarity
- intent similarity
- knowledge retrieval
- RAG
- semantic candidate retrieval

Nao deve ser dependencia obrigatoria do primeiro MVP.

## 23. Inteligencia Artificial

O Smart360 utilizara LLMs existentes.

Nao existe requisito inicial para construir LLM proprietario.

Providers poderao incluir:

- OpenAI
- Gemini
- outros providers futuros

Port conceitual:

IntentClassifier

Adapters possiveis:

- OpenAIIntentClassifier
- GeminiIntentClassifier

A aplicacao deve conhecer o contrato, nao necessariamente o fornecedor.

## 24. Papel da IA

IA pode auxiliar:

- entendimento de intencao
- classificacao
- extracao
- normalizacao
- embeddings
- busca
- explicacao
- suporte
- recomendacao

IA nao deve automaticamente assumir:

- autorizacao
- decisao financeira
- score opaco
- controle total do ranking
- validacao de seguranca

## 25. Reputation

Reputation deve refletir evidencias reais do ecossistema.

Sinais candidatos:

- rating
- reviews
- servicos concluidos
- taxa de resposta
- tempo de resposta
- reclamacoes
- credenciais
- experiencia
- clientes recorrentes
- cancelamentos

Evitar score sem explicacao.

Reputation deve ser auditavel e evolutiva.

## 26. Learning

Smart360 podera detectar gaps de capacidade.

Fluxo:

market demand
-> provider capability
-> skill gap
-> training recommendation
-> course
-> assessment
-> improved capability
-> more opportunities

Podera haver:

- cursos proprios
- parceiros
- integracoes com plataformas educacionais

Learning permanece um contexto separado.

## 27. Rewards

Rewards e gamificacao poderao incentivar:

- qualidade
- confiabilidade
- resposta rapida
- conclusao
- aprendizado
- colaboracao
- boas avaliacoes legitimas

Reinforcement Learning podera ser estudado para partes adequadas do ecossistema.

Antes disso o sistema precisa registrar:

- estados
- eventos
- acoes
- resultados
- recompensas
- feedback

Nao usar RL apenas como recurso de marketing.

## 28. Advertising

Advertising sera uma vertical de monetizacao.

Conceitos candidatos:

- Advertiser
- Campaign
- Ad
- Audience
- Placement
- Impression
- Click
- Conversion
- Budget

Publicidade deve permanecer desacoplada do ranking organico.

Conteudo patrocinado deve ser identificavel.

## 29. Growth

Growth podera coordenar:

- acquisition
- activation
- retention
- referral
- revenue
- campaigns
- experiments

Nao misturar Growth com regras centrais do Marketplace.

## 30. Eventos

Eventos serao importantes para inteligencia futura.

Exemplos:

- search_performed
- service_request_created
- intent_classified
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

Isso nao implica adotar Event Sourcing.

Podemos iniciar com modelo convencional de eventos e auditoria.

## 31. Multi-tenancy

Todo dado organizational deve responder:

A qual Organization este dado pertence?

Isolamento nao deve depender somente do frontend.

Operacoes devem verificar:

- usuario
- membership
- organization
- role
- ownership
- permissao

Dados de uma organization nao podem vazar para outra.

## 32. Autorizacao

Authentication responde:

Quem e voce?

Authorization responde:

Voce pode realizar esta acao?

Membership responde:

Qual e sua relacao com esta Organization?

Ownership responde:

Este recurso pertence a quem?

Nao confundir estes conceitos.

## 33. Seguranca

Principios:

- secrets fora do Git
- .env fora do versionamento
- API keys nunca hardcoded
- autorizacao sempre server-side
- validar IDs
- evitar IDOR
- evitar cross-tenant access
- validar input
- minimizar dados retornados
- logs sem secrets

## 34. Auditoria

O sistema deve evoluir para registrar operacoes relevantes.

Exemplos:

- create
- update
- delete
- role changes
- permission changes
- administrative actions
- matching decisions
- conversions
- important AI decisions

Auditoria deve ser proporcional ao risco.

## 35. API

API e interface.

API nao e dominio.

Fluxo esperado:

request
-> validation
-> interface
-> use case
-> domain
-> repository
-> response

## 36. Frontend

O frontend deve poder evoluir sem redefinir regras centrais.

Dominio nao deve depender de:

- HTML
- templates
- CSS
- JavaScript framework
- componentes de UI

## 37. Processamento assincrono

Redis e Celery nao sao requisitos imediatos.

Poderao ser introduzidos quando existirem:

- tarefas demoradas
- retries
- jobs
- scheduling
- processamento em background
- filas

Nao introduzir infraestrutura sem problema real.

## 38. Evolucao para microservicos

Microservicos nao sao proibidos para sempre.

Uma parte podera ser extraida quando houver motivo concreto:

- escala independente
- isolamento de falha
- ownership separado
- requisitos operacionais distintos
- tecnologia especializada
- deployment independente justificavel

A distribuicao deve surgir da necessidade, nao da estetica.

## 39. MVP inicial

O primeiro loop de valor deve provar:

usuario descreve necessidade
-> sistema estrutura demanda
-> encontra candidates
-> classifica/rankeia
-> apresenta providers
-> gera contato ou lead
-> acompanha resultado
-> coleta reputacao

Antes de expandir agressivamente monetizacao, devemos validar esse loop.

## 40. Nao priorizar inicialmente

Nao construir prematuramente:

- wallet
- pagamentos complexos
- ad platform completa
- afiliados complexos
- reinforcement learning sofisticado
- agentes autonomos amplos
- mobile app nativo
- microservicos
- infraestrutura distribuida desnecessaria

## 41. Decisao de produto

Toda nova feature deve responder pelo menos uma destas perguntas:

- melhora conexao entre demanda e capacidade?
- aumenta confianca?
- aumenta inteligencia?
- melhora operacao?
- cria monetizacao sustentavel?
- melhora experiencia?
- reduz friccao?
- gera dados estrategicos?

Se nao, avaliar prioridade.

## 42. Principio final

O Smart360 v3 nao deve ser construido como uma colecao aleatoria de features.

Ele deve evoluir como um ecossistema coerente em torno de:

intencao
+
capacidade
+
oportunidade
+
confianca
+
aprendizado
+
monetizacao
