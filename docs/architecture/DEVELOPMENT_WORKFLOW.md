# Smart360 v3 - Development Workflow

Este documento define o fluxo obrigatorio de desenvolvimento do Smart360 v3.

## 1. Principio

Toda alteracao deve seguir:

Understand
-> Inspect
-> Model
-> Implement
-> Validate
-> Report

O objetivo e reduzir alteracoes acidentais, retrabalho e divida arquitetural.

## 2. Inicio de qualquer tarefa

Antes de alterar codigo:

git status --short
git branch --show-current
python manage.py check

O agente deve identificar alteracoes pre-existentes.

Alteracoes pre-existentes fora do escopo devem ser preservadas.

## 3. Ler governanca

Antes de implementar:

- AGENTS.md
- .cursor/rules/smart360-architecture/RULE.md
- .cursor/skills/smart360-development/SKILL.md
- docs/architecture/SMART360_ARCHITECTURE.md
- docs/architecture/DEVELOPMENT_WORKFLOW.md

## 4. Inspecionar antes de criar

Pesquisar implementacoes existentes.

Utilizar comandos direcionados como:

find src -maxdepth 5 -type f | sort

grep -R "NomeDoConceito" -n src

Nao duplicar entidades, ports, repositories ou casos de uso existentes.

## 5. Definir escopo

Antes da implementacao identificar:

- requisito exato
- bounded context
- regras afetadas
- schema afetado
- autorizacao
- multi-tenancy
- testes necessarios

Nao ampliar escopo automaticamente.

## 6. Ordem preferencial

Quando a feature possui dominio real:

1. domain
2. application
3. infrastructure
4. interfaces

Isso nao significa criar arquivos vazios em todas as camadas.

Criar apenas o necessario.

## 7. Domain first

Comecar pelas regras de negocio quando houver regras significativas.

Domain deve permanecer independente do framework.

Nao criar Django Model primeiro e depois tentar transformar automaticamente esse model em dominio.

## 8. Use case

Toda acao relevante deve possuir responsabilidade clara.

Exemplos:

CreateServiceCategory
CreateService
RegisterProvider
CreateServiceRequest
FindProviderCandidates

Use cases devem depender de ports, nao de adapters concretos.

## 9. Persistencia

Depois de definir dominio e aplicacao, implementar adapters.

Fluxo:

Domain Entity
-> Repository Port
-> Django Repository
-> Django Model
-> PostgreSQL

Ou caminho inverso para leitura.

## 10. Alteracao de Django Model

Antes:

python manage.py check

Depois de alterar model:

python manage.py makemigrations nome_do_app

Inspecionar migration gerada.

Nao aplicar automaticamente em producao.

## 11. Migration local

Quando autorizado no ambiente local:

python manage.py migrate

Depois:

python manage.py check

## 12. Quando nao deve haver migration

Executar:

python manage.py makemigrations --check

Resultado esperado:

No changes detected

## 13. Migration existente

Nunca editar uma migration que ja foi aplicada apenas para alterar schema.

Criar nova migration.

Nunca apagar migrations para "recomecar" sem autorizacao expressa.

## 14. PostgreSQL

PostgreSQL e o banco oficial.

Nao substituir por SQLite para facilitar implementacao.

Nao recriar banco.

Nao executar flush.

Nao apagar dados existentes sem autorizacao.

## 15. Multi-tenancy

Toda feature organizacional deve responder:

Qual Organization possui este recurso?

Antes de persistir ou retornar dados verificar:

- User
- Membership
- Organization
- Role
- Ownership
- Authorization

Nao aceitar organization_id do cliente como prova de autorizacao.

## 16. Autorizacao

A verificacao deve ocorrer server-side.

Diferenciar:

Authentication
Membership
Role
Permission
Ownership

Usuario autenticado nao significa autorizado.

## 17. API e Views

Interface deve:

- receber dados
- validar formato
- resolver contexto
- chamar use case
- traduzir resposta

Interface nao deve concentrar regras centrais.

## 18. IA

Toda feature de IA deve possuir um contrato explicito.

Processo:

input
-> port
-> provider adapter
-> structured result
-> validation
-> application/domain

Nao chamar provider diretamente do domain.

Nao confiar automaticamente na resposta do LLM.

## 19. Matching

Ao trabalhar com matching separar:

- retrieval
- eligibility
- scoring
- ranking
- explanation

Cada parte deve ser testavel.

Evitar ranking inteiramente escondido dentro de prompt.

## 20. Alteracoes pequenas

Preferir incrementos pequenos e completos.

Exemplo:

ServiceCategory completo

antes de:

ServiceCategory + Service + Provider + Matching + Payment

na mesma tarefa.

## 21. Testes durante desenvolvimento

Executar primeiro testes especificos da alteracao.

Exemplo:

python manage.py test caminho.do.app.tests

ou teste unitario direcionado.

Expandir para suites maiores quando necessario.

## 22. Testes de dominio

Sempre que possivel testar domain sem inicializar Django.

Testar:

- invariantes
- comportamento
- transicoes
- validacoes
- regras negativas

## 23. Testes de use case

Testar:

- sucesso
- duplicidade
- recurso inexistente
- entradas invalidas
- autorizacao quando aplicavel

Preferir doubles/fakes para ports quando isso simplificar o teste.

## 24. Testes de repository

Validar:

- persistencia
- leitura
- conversao Model para Entity
- conversao Entity para Model
- constraints relevantes

## 25. Testes multi-tenant

Para recursos tenant-scoped testar:

1. membro autorizado acessa recurso da propria Organization
2. membro de outra Organization nao acessa
3. usuario sem Membership nao acessa
4. role insuficiente nao executa operacao protegida

## 26. Validacao final minima

Antes de declarar uma tarefa concluida:

python manage.py check
python manage.py makemigrations --check
git diff --check

Executar testes relevantes.

Se a tarefa criou intencionalmente migration ainda nao aplicada, adaptar a verificacao de makemigrations conforme necessario e explicar no relatorio.

## 27. Git status final

Executar:

git status --short

Comparar com o status inicial.

Garantir que somente arquivos esperados foram alterados.

## 28. Git diff

Inspecionar:

git diff

Verificar:

- arquivos inesperados
- secrets
- debugging temporario
- prints
- codigo morto
- mudancas fora de escopo

## 29. Secrets

Antes de concluir verificar que nao entraram:

- senhas
- API keys
- tokens
- credenciais
- conteudo de .env
- dados privados desnecessarios

## 30. Dependencias

Se uma biblioteca foi adicionada, justificar no relatorio.

Nao adicionar biblioteca sem necessidade.

## 31. Debug temporario

Remover antes da conclusao:

- print de debugging
- breakpoint
- logs temporarios
- codigo comentado sem utilidade
- arquivos temporarios

## 32. Escopo proibido automaticamente

Uma tarefa local nao autoriza:

- deploy
- producao
- DNS
- webserver
- restart de services
- SSH
- commit
- push

## 33. Git proibido sem autorizacao

Nao executar:

git commit
git push
git reset --hard
git clean -fd

## 34. Producao

Producao exige solicitacao explicita.

Mesmo que o codigo esteja pronto, nao fazer deploy automaticamente.

## 35. Refatoracao

Se for necessario refatorar codigo diretamente relacionado:

- manter escopo pequeno
- justificar
- preservar comportamento
- testar

Nao aproveitar feature pequena para reescrever modulo inteiro.

## 36. Erro durante implementacao

Quando um teste falhar:

1. ler erro
2. identificar causa
3. corrigir causa
4. executar teste direcionado novamente

Nao iniciar alteracoes aleatorias.

## 37. Loop de testes

Evitar:

test everything
-> alterar
-> test everything
-> alterar
-> test everything

Preferir:

teste direcionado
-> correcao
-> teste direcionado
-> validacao final

## 38. Conflito arquitetural

Se requisito conflitar com governanca:

- nao ignorar regra
- nao criar workaround escondido
- explicar conflito
- propor alternativa

## 39. Decisao reversivel

Se a decisao for:

- local
- pequena
- reversivel
- coerente com arquitetura

o agente pode decidir e implementar.

Registrar decisao quando relevante.

## 40. Decisao estrutural

Se afetar:

- modelo de dominio
- tenancy
- auth
- provider abstraction
- banco
- arquitetura
- fronteiras de contexto

e houver alternativas relevantes, apresentar opcoes antes de congelar uma escolha nao definida.

## 41. Documentacao

Atualizar documentacao somente quando:

- comportamento mudou
- arquitetura mudou
- nova regra permanente surgiu
- nova decisao estrutural foi aprovada

Nao inflar documentacao para cada mudanca trivial.

## 42. Comentarios de codigo

Comentarios devem explicar:

- motivo
- restricao
- regra nao obvia

Nao comentar codigo obvio apenas repetindo sua sintaxe.

## 43. Naming

Usar nomes orientados ao dominio.

Preferir:

CreateService
ProviderRepository
ServiceRequest
MatchingScore

Evitar:

Thing
DataManager
CommonUtils
Misc
Helper2

## 44. Imports

Respeitar fronteiras.

Se domain precisar importar infrastructure, existe forte indicio de violacao arquitetural.

Corrigir dependencia em vez de contornar.

## 45. Integridade do banco

Quando apropriado usar:

- unique constraints
- foreign keys
- check constraints
- indexes

Nao confiar somente em validacao Python para invariantes estruturais que o banco pode garantir.

## 46. Performance

Nao otimizar prematuramente.

Mas evitar problemas evidentes como:

- N+1 em consultas criticas
- queries globais sem tenant
- loops fazendo queries repetidas
- carregamento integral desnecessario

Otimizar baseado em necessidade e medicao.

## 47. Observabilidade futura

Quando a feature for critica, considerar pontos futuros de:

- logging
- audit
- metrics
- events

Nao instalar stack de observabilidade sem necessidade.

## 48. Feature pronta

Uma feature esta pronta quando:

- requisito funciona
- dominio esta coerente
- multi-tenancy esta protegido
- autorizacao esta correta
- banco esta consistente
- migration esta correta
- testes relevantes passam
- checks passam
- escopo foi respeitado

## 49. Formato do relatorio final

A resposta final do agente deve usar:

A. Implementado

B. Arquivos alterados

C. Arquitetura

D. Banco e migrations

E. Testes e validacoes

F. Riscos ou pendencias

G. Nao alterado

## 50. Regra de economia

Nao medir produtividade por quantidade de codigo.

Menos codigo correto e bem posicionado e preferivel a grande implementacao acoplada.

## 51. Regra final

O Smart360 deve evoluir por incrementos controlados.

Cada incremento deve fortalecer pelo menos um destes pilares:

- intencao
- capacidade
- oportunidade
- confianca
- inteligencia
- aprendizado
- monetizacao
- operacao

sem comprometer as fronteiras arquiteturais.
