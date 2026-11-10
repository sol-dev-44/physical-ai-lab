-- Explicit grants for the lab-agent (service role). Projects created with
-- "automatically expose new tables" turned off don't grant these by default,
-- and the sync and command queue go through PostgREST as service_role.
grant usage on schema public to service_role;
grant all on public.admins, public.runs, public.events, public.tools, public.commands to service_role;
