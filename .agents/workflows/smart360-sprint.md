# Smart360 Sprint Workflow

This workflow guides the step-by-step process for executing development sprints in the Smart360 v3 codebase.

## 1. Read Governance & Inspect State
- Read the project architecture rules in [smart360-architecture.md](file:///home/marcelo/projetos/smart360-v3/.agents/rules/smart360-architecture.md).
- Inspect the current working tree by running:
  ```bash
  git status --short
  git branch --show-current
  ```
- If the working tree is not clean, stop and report immediately to the user.

## 2. Code Inspection & Scope Restatement
- Locate and inspect existing code related to the task within `src/` to prevent duplication.
- Restate internally the exact functional and architectural scope of the task. Do not plan or implement speculative requirements.

## 3. Implement Domain First
- Begin implementation at the domain layer when business rules are involved.
- Coordinate actions through the application layer (use cases and ports).
- Implement concrete infrastructure adapters and UI interfaces last.

## 4. Local Validation
- Run targeted tests for the modified bounded context:
  ```bash
  .venv/bin/python manage.py test src.<bounded_context>.tests -v 2
  ```
- Run Django framework and system checks:
  ```bash
  .venv/bin/python manage.py check
  ```
- Run the migration checker to ensure schema coherence:
  ```bash
  .venv/bin/python manage.py makemigrations --check
  ```

## 5. Review Diff
- Inspect the file changes to ensure no secrets, debugging code, or unrelated edits are present:
  ```bash
  git diff --check
  git diff
  ```

## 6. Report & Await Approval
- Prepare a final report answering the standard reporting structure (Implemented, Files changed, Architecture, Database, Tests, Risks, Not changed).
- **DO NOT** execute any git commit, git push, or deployment commands.
