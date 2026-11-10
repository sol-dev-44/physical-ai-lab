-- Lab schema v0.
--
-- The event log on the lab machine is the source of truth. This database is a
-- published copy: the lab-agent sync (service role) inserts runs and events;
-- the website reads them. Events are append-only, enforced by trigger.
--
-- Security model:
--   anon           reads published runs and their events, nothing else
--   authenticated  admins only (public.is_admin()); can toggle run.published,
--                  read tools/commands, queue commands
--   service_role   the lab-agent; bypasses RLS

-- ---------------------------------------------------------------- admins
create table public.admins (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  email      text not null,
  created_at timestamptz not null default now()
);

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;

-- ---------------------------------------------------------------- runs
create table public.runs (
  run_id        text primary key check (run_id ~ '^[a-z0-9][a-z0-9-]{2,79}$'),
  experiment_id text not null check (experiment_id ~ '^exp[0-9]{3}(-[a-z0-9]+)*$'),
  status        text not null default 'open' check (status in ('open', 'completed', 'aborted', 'failed')),
  null_test     boolean not null default false,
  forked_from   text references public.runs (run_id),
  git_sha       text,
  started_at    timestamptz,
  ended_at      timestamptz,
  event_count   integer not null default 0,
  published     boolean not null default false,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index runs_experiment_idx on public.runs (experiment_id, started_at desc);

-- ---------------------------------------------------------------- events
create table public.events (
  event_id    text primary key check (event_id ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
  run_id      text not null references public.runs (run_id) on delete restrict,
  seq         integer not null check (seq >= 0),
  ts          timestamptz not null,
  type        text not null,
  actor       text not null,
  tool        text,
  device      text,
  parent_id   text,
  -- The exact event as written to the log. Readers validate this against
  -- the contract; the columns above exist only for querying.
  raw         jsonb not null,
  ingested_at timestamptz not null default now(),
  unique (run_id, seq)
);
create index events_run_idx on public.events (run_id, seq);
create index events_tool_idx on public.events (tool) where tool is not null;

create or replace function public.events_append_only()
returns trigger
language plpgsql
as $$
begin
  raise exception 'events are append-only (% blocked). Write a new run instead.', tg_op;
end;
$$;

create trigger events_no_update before update on public.events
  for each row execute function public.events_append_only();
create trigger events_no_delete before delete on public.events
  for each row execute function public.events_append_only();

-- ---------------------------------------------------------------- tools
-- Registered by the lab-agent on startup so the admin UI knows what exists.
create table public.tools (
  name                  text primary key check (name ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$'),
  description           text not null default '',
  requires_confirmation boolean not null default false,
  args_schema           jsonb not null default '{}'::jsonb,
  agent_id              text not null,
  registered_at         timestamptz not null default now()
);

-- ---------------------------------------------------------------- commands
-- A queue, not a control channel. The web inserts; the agent at home claims,
-- runs the safety gate, executes, and logs. Stale commands are never run.
create table public.commands (
  id           uuid primary key default gen_random_uuid(),
  tool         text not null references public.tools (name) on delete cascade,
  args         jsonb not null default '{}'::jsonb check (jsonb_typeof(args) = 'object'),
  confirmed    boolean not null default false,
  status       text not null default 'pending'
               check (status in ('pending', 'claimed', 'done', 'rejected', 'failed', 'expired')),
  requested_by uuid references auth.users (id) default auth.uid(),
  created_at   timestamptz not null default now(),
  claimed_at   timestamptz,
  claimed_by   text,
  finished_at  timestamptz,
  run_id       text references public.runs (run_id),
  result       text
);
create index commands_pending_idx on public.commands (created_at) where status = 'pending';

-- Claim the oldest pending command younger than max_age. Older pending
-- commands are marked expired first: a command queued while the agent was
-- offline must not fire hours later.
create or replace function public.claim_next_command(agent text, max_age interval default interval '60 seconds')
returns setof public.commands
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.commands
     set status = 'expired', finished_at = now(), result = 'expired before claim'
   where status = 'pending' and created_at < now() - max_age;

  return query
  update public.commands c
     set status = 'claimed', claimed_at = now(), claimed_by = agent
   where c.id = (
     select id from public.commands
      where status = 'pending'
      order by created_at
      for update skip locked
      limit 1
   )
  returning c.*;
end;
$$;

revoke all on function public.claim_next_command(text, interval) from public, anon, authenticated;
grant execute on function public.claim_next_command(text, interval) to service_role;

-- ---------------------------------------------------------------- updated_at
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;
create trigger runs_touch before update on public.runs
  for each row execute function public.touch_updated_at();

-- ---------------------------------------------------------------- RLS
alter table public.admins   enable row level security;
alter table public.runs     enable row level security;
alter table public.events   enable row level security;
alter table public.tools    enable row level security;
alter table public.commands enable row level security;

-- Start from nothing for the client roles, then grant exactly what's needed.
revoke all on public.admins, public.runs, public.events, public.tools, public.commands from anon, authenticated;

grant select on public.runs, public.events to anon, authenticated;
grant select on public.admins, public.tools, public.commands to authenticated;
grant update (published) on public.runs to authenticated;
grant insert (tool, args, confirmed) on public.commands to authenticated;

create policy admins_self on public.admins
  for select to authenticated using (user_id = auth.uid());

create policy runs_read on public.runs
  for select to anon, authenticated using (published or public.is_admin());
create policy runs_publish on public.runs
  for update to authenticated using (public.is_admin()) with check (public.is_admin());

create policy events_read on public.events
  for select to anon, authenticated using (
    public.is_admin()
    or exists (select 1 from public.runs r where r.run_id = events.run_id and r.published)
  );

create policy tools_read on public.tools
  for select to authenticated using (public.is_admin());

create policy commands_read on public.commands
  for select to authenticated using (public.is_admin());
create policy commands_queue on public.commands
  for insert to authenticated with check (public.is_admin() and status = 'pending' and requested_by = auth.uid());
