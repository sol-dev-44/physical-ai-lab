# Supabase

Postgres holds a **published copy** of the lab's event logs, plus the admin
command queue. The JSONL logs on the lab machine stay the source of truth.

| Table      | Written by            | Read by                        |
|------------|-----------------------|--------------------------------|
| `runs`     | lab-agent sync        | site (published only), admin   |
| `events`   | lab-agent sync        | site (published runs), admin   |
| `tools`    | lab-agent on startup  | admin console                  |
| `commands` | admin console         | lab-agent (`claim_next_command`) |
| `admins`   | you, once, by hand    | `is_admin()`                   |

Invariants enforced in the database, not just the app:

- `events` is append-only (update and delete raise). Fix mistakes with a new run.
- `(run_id, seq)` is unique.
- Anonymous users only see published runs and their events.
- Only admins can queue commands or publish runs; only the service role can claim commands.
- A command older than 60 seconds is marked `expired` instead of being run.
- The web may insert only `(tool, args, confirmed)` into `commands`. `requested_by`
  defaults to `auth.uid()` and the policy checks it, so **don't send it**: including it
  fails with "permission denied for table commands".
- `commands.run_id` references `runs`, so it can only be set once that run is synced.

## Setup (new project)

1. Create the project, then apply migrations: `supabase link --project-ref <ref>` and `supabase db push`
   (or paste `migrations/*.sql` into the SQL editor in order).
2. Auth > Providers: keep Email on. Auth > Settings: **turn off "Allow new users to sign up"**.
3. Auth > Users: invite yourself. Then register that user as admin:
   ```sql
   insert into public.admins (user_id, email)
   select id, email from auth.users where email = 'you@example.com';
   ```
4. Auth > URL Configuration: add `http://localhost:3000/auth/callback` and the production callback.
5. Copy the URL and anon key into `apps/web/.env.local`; the service role key goes only in
   `services/lab-agent/.env` on the lab machine. Never ship the service role key to the web app.
   New projects issue `sb_secret_...` keys (Project Settings, API Keys, Secret keys); the
   lab-agent client accepts them. The `sb_publishable_...` key is the public one.

## Tests

`tests/run.sh` applies every migration to a throwaway Postgres database with
stand-ins for Supabase's roles and `auth.uid()`, then runs `tests/rls_test.sql`.
CI runs it on every push. Add an expectation whenever you add a policy.
