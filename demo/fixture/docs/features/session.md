# Session recovery

## User outcome

A returning authenticated user resumes their most recent saved work instead of starting over.

## Scope

Recovery covers the current user's persisted session only. It runs at application resume time and does not cover anonymous visitors, cross-device transfer, or session sharing.

## Behavior

On resume the application loads the saved record for the active user. When the record is missing or owned by a different user, a clean session is created. Valid state is copied into the in-memory session so later edits never mutate the stored record directly.

## States and failure modes

Saved state resumes as-is. Missing state starts clean. A record owned by another user is rejected and treated as missing. Storage read errors surface to the caller rather than being silently swallowed.

## Data and dependencies

Durable session state is owned by the provided store and keyed by user id. The application entry point in `src/app.py` calls recovery before rendering user work.

## Invariants

Never restore another user's state. Never infer ownership from the token alone. A failed read must not fabricate saved state.

## Change guidance

Recovery is coupled to session ownership checks, the store contract, and the resume entry point. When adding a restore source or expiry rule, update the ownership check, the clean-start fallback, and the persistence tests together so foreign-state rejection stays intact.

## Implementation

Recovery is implemented by `src/auth/session.py`, which exposes `recover_session` and `new_session`. The resume entry point lives in `src/app.py`.

## Verification

Run `python3 -m pytest tests/test_session.py` and confirm that saved state restores while foreign state is rejected.
