-- RLS and invariants test. Run on plain Postgres after 00_supabase_stub.sql and
-- the migrations (see run.sh). Any failed expectation aborts with an error.
\set ON_ERROR_STOP 1
\o /dev/null

create function pg_temp.expect_count(q text, n int) returns void language plpgsql as $$
declare got int;
begin
  execute format('select count(*) from (%s) t', q) into got;
  if got <> n then raise exception 'expected % rows from [%], got %', n, q, got; end if;
end $$;

create function pg_temp.expect_error(q text) returns void language plpgsql as $$
begin
  execute q;
  raise exception 'expected an error from [%]', q;
exception when others then
  if sqlerrm like 'expected an error%' then raise; end if;
end $$;

grant all on all tables in schema public to service_role;
grant execute on all functions in schema pg_temp to anon, authenticated, service_role;
insert into auth.users values
  ('00000000-0000-0000-0000-000000000001', 'admin@example.com'),
  ('00000000-0000-0000-0000-000000000002', 'visitor@example.com');
insert into public.admins values ('00000000-0000-0000-0000-000000000001', 'admin@example.com');

-- agent (service role) writes
set role service_role;
insert into public.runs (run_id, experiment_id, published) values
  ('exp000-t-r1', 'exp000-ir-bridge', true),
  ('exp000-t-r2', 'exp000-ir-bridge', false);
insert into public.events (event_id, run_id, seq, ts, type, actor, raw) values
  ('01JC9X7Q000000000000000001', 'exp000-t-r1', 0, now(), 'run.started', 'cli', '{}'),
  ('01JC9X7Q000000000000000002', 'exp000-t-r2', 0, now(), 'run.started', 'cli', '{}');
insert into public.tools (name, agent_id, requires_confirmation) values ('fan.power', 'test', false);
select pg_temp.expect_error($q$update public.events set seq = 9$q$);
select pg_temp.expect_error($q$delete from public.events$q$);
select pg_temp.expect_error($q$insert into public.events (event_id, run_id, seq, ts, type, actor, raw)
  values ('01JC9X7Q000000000000000003', 'exp000-t-r1', 0, now(), 'note', 'cli', '{}')$q$); -- dup seq
reset role;

-- anonymous visitor
set role anon;
select pg_temp.expect_count('select * from public.runs', 1);
select pg_temp.expect_count('select * from public.events', 1);
select pg_temp.expect_error('select * from public.tools');
select pg_temp.expect_error('select * from public.commands');
select pg_temp.expect_error($q$update public.runs set published = true$q$);
select pg_temp.expect_error($q$insert into public.events (event_id, run_id, seq, ts, type, actor, raw)
  values ('01JC9X7Q000000000000000009', 'exp000-t-r1', 1, now(), 'note', 'cli', '{}')$q$);
reset role;

-- signed in, not an admin
set request.jwt.uid = '00000000-0000-0000-0000-000000000002';
set role authenticated;
select pg_temp.expect_count('select * from public.runs', 1);
select pg_temp.expect_count('select * from public.tools', 0);
select pg_temp.expect_error($q$insert into public.commands (tool) values ('fan.power')$q$);
update public.runs set published = true where run_id = 'exp000-t-r2'; -- silently matches 0 rows
reset role;
select pg_temp.expect_count($q$select * from public.runs where run_id = 'exp000-t-r2' and published$q$, 0);

-- admin
set request.jwt.uid = '00000000-0000-0000-0000-000000000001';
set role authenticated;
select pg_temp.expect_count('select * from public.runs', 2);
select pg_temp.expect_count('select * from public.events', 2);
select pg_temp.expect_count('select * from public.tools', 1);
insert into public.commands (tool, args) values ('fan.power', '{}');
select pg_temp.expect_error($q$insert into public.commands (tool, status) values ('fan.power', 'claimed')$q$);
select pg_temp.expect_error($q$update public.runs set status = 'completed'$q$);
select pg_temp.expect_error($q$select * from public.claim_next_command('admin')$q$);
update public.runs set published = true where run_id = 'exp000-t-r2';
reset role;
select pg_temp.expect_count($q$select * from public.runs where run_id = 'exp000-t-r2' and published$q$, 1);

-- command queue: stale commands expire instead of running
insert into public.commands (tool, created_at) values ('fan.power', now() - interval '10 minutes');
set role service_role;
select pg_temp.expect_count($q$select * from public.claim_next_command('agent') where status = 'claimed'$q$, 1);
select pg_temp.expect_count($q$select * from public.commands where status = 'expired'$q$, 1);
select pg_temp.expect_count($q$select * from public.claim_next_command('agent')$q$, 0);
reset role;

\echo 'rls_test: all expectations passed'
