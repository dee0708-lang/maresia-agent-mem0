# maresia-agent-mem0
Mem0 user-profile memory connector scaffold. Code and documentation only; live synchronization disabled by default.

## Public-repository boundary and Mem0 adapter

This public repository contains original code, documentation, and synthetic tests only. Never commit profile memory, contact information, account credentials, exports, or real user fixtures.

`Mem0Profiles(execute, user_id, enabled=False, allow_writes=False)` binds one instance to one authenticated, authorized, preferably pseudonymous user ID. The runtime must derive and authorize that ID from the authenticated principal, not from untrusted model output. There is deliberately no global/default user ID in `.env.example`.

`search(...)` maps to `MEM0_PERFORM_SEMANTIC_SEARCH_ON_MEMORIES` with strict user scoping. `remember(..., consent_confirmed=True)` maps to `MEM0_ADD_NEW_MEMORY_RECORDS` with `infer=False` for verbatim storage and asynchronous processing. Preserve any returned event ID; the runtime must poll the provider event and perform a scoped read-back before claiming persistence. No automatic profiling, update, deletion, or migration is implemented.

## Starter status and runtime contract

This is an offline-tested Python 3.11+ scaffold, not a deployed integration.
No HTTP client, scheduler, webhook, automatic cross-service transfer, or background job is configured.
Only the Python standard library is needed for the tests.

`connector.py` expects an injected `execute(tool_slug, arguments)` callable. A future authorized runtime must bind that callable to the explicitly selected Composio connected account, enforce tenant/user authorization, propagate provider errors, and redact logs. The callable's response is returned unchanged: a queued response is not proof of persistence. Connecting an app in chat does not install its credentials into GitHub.

All constructors default to disabled. `from_env(...)` enables access only when `MARESIA_ENABLE_LIVE_SYNC=true`; memory writes additionally require `MARESIA_ALLOW_WRITES=true` and explicit consent for each write. `.env.example` is a variable-name template and is not loaded automatically. The HubSpot adapter has no write methods.

## Offline tests

```sh
python -m unittest discover -s tests -v
```

Tests use recording executors and synthetic fixtures only. They make no provider calls and do not validate live authentication, production permissions, or data synchronization.

## Before any live use

1. Approve the data scope, transfer direction, runtime, retention policy, and schedule separately.
2. Configure least-privilege credentials in a deployment secret manager; never commit `.env` files, keys, exports, customer content, snippets, or profiles, even to private repositories.
3. Implement and review the account-bound executor and application authorization. Feature flags are safety gates, not an authentication boundary.
4. Add redacted operational logging, rate-limit handling, a durable checkpoint/idempotency strategy, and a consent/deletion policy before scheduling transfers. No automatic retries are included.
5. Verify provider results with a scoped read-back before reporting successful persistence. No live integration test has been performed.

`.gitignore` is a convenience, not a security guarantee. Inspect every commit. No repository license was selected automatically.
