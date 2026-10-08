-- Ski Nav group backend (Supabase / Postgres).
-- Paste this whole file into Supabase > SQL Editor > New query > Run. Safe to run again.
--
-- Security model: the tables are locked (row level security on, no policies), so the public "anon" key
-- can't read or write them directly. Everything goes through the functions below, and every function
-- needs the caller's member secret, a random token each phone gets when it joins. Only people in a trip
-- can see that trip, and only the organizer can change the plan or remove people.

create table if not exists trips (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  invite_code text not null unique,
  plan        jsonb not null default '{}'::jsonb,   -- shared plan settings, e.g. {"variant":"red"}
  starts_on   date,
  ends_on     date,
  created_at  timestamptz not null default now()
);

create table if not exists members (
  id         uuid primary key default gen_random_uuid(),
  trip_id    uuid not null references trips(id) on delete cascade,
  secret     uuid not null unique default gen_random_uuid(),
  name       text not null check (char_length(name) between 1 and 30),
  color      text not null default '#C2410C' check (color ~ '^#[0-9A-Fa-f]{6}$'),
  role       text not null default 'member' check (role in ('owner','member')),
  sharing    boolean not null default true,
  platform   text,
  joined_at  timestamptz not null default now(),
  seen_at    timestamptz
);
create index if not exists members_trip on members(trip_id);

-- latest position only (one row per member): nothing is kept as a history
create table if not exists positions (
  member_id  uuid primary key references members(id) on delete cascade,
  trip_id    uuid not null references trips(id) on delete cascade,
  lat        double precision not null check (lat between -90 and 90),
  lon        double precision not null check (lon between -180 and 180),
  acc        real,
  speed      real,
  on_lift    boolean not null default false,
  run        text,
  km         real,
  updated_at timestamptz not null default now()
);

create table if not exists meet_points (
  trip_id    uuid primary key references trips(id) on delete cascade,
  lat        double precision not null,
  lon        double precision not null,
  label      text,
  at_time    text,
  set_by     uuid references members(id) on delete set null,
  updated_at timestamptz not null default now()
);

alter table trips enable row level security;
alter table members enable row level security;
alter table positions enable row level security;
alter table meet_points enable row level security;
revoke all on trips, members, positions, meet_points from public;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'anon') then
    execute 'revoke all on trips, members, positions, meet_points from anon';
  end if;
  if exists (select 1 from pg_roles where rolname = 'authenticated') then
    execute 'revoke all on trips, members, positions, meet_points from authenticated';
  end if;
end $$;

-- who is calling (by secret)
create or replace function _me(p_secret uuid) returns members
language sql stable security definer set search_path = public as $$
  select * from members where secret = p_secret
$$;

create or replace function _code() returns text language sql volatile as $$
  select 'AVZ-' || upper(substr(md5(random()::text || clock_timestamp()::text), 1, 4))
$$;

-- organizer starts a trip; returns their secret and the invite code
create or replace function create_trip(p_name text, p_owner_name text, p_color text, p_starts date default null, p_ends date default null, p_platform text default null)
returns json language plpgsql security definer set search_path = public as $$
declare t trips; m members; c text;
begin
  loop
    c := _code();
    exit when not exists (select 1 from trips where invite_code = c);
  end loop;
  insert into trips(name, invite_code, starts_on, ends_on) values (left(p_name, 60), c, p_starts, p_ends) returning * into t;
  insert into members(trip_id, name, color, role, platform) values (t.id, left(trim(p_owner_name), 30), coalesce(p_color, '#1D5FE0'), 'owner', left(p_platform, 20)) returning * into m;
  return json_build_object('trip_id', t.id, 'member_id', m.id, 'secret', m.secret, 'invite_code', t.invite_code, 'name', t.name);
end $$;

-- what a friend sees before joining (no secret yet)
create or replace function trip_preview(p_code text) returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('name', t.name, 'starts_on', t.starts_on, 'ends_on', t.ends_on,
    'organizer', (select name from members where trip_id = t.id and role = 'owner' limit 1),
    'members', (select count(*) from members where trip_id = t.id))
  from trips t where t.invite_code = upper(trim(p_code))
$$;

create or replace function join_trip(p_code text, p_name text, p_color text, p_platform text default null)
returns json language plpgsql security definer set search_path = public as $$
declare t trips; m members;
begin
  select * into t from trips where invite_code = upper(trim(p_code));
  if t.id is null then raise exception 'invite code not found' using errcode = 'P0002'; end if;
  if (select count(*) from members where trip_id = t.id) >= 20 then raise exception 'trip is full'; end if;
  insert into members(trip_id, name, color, platform) values (t.id, left(trim(p_name), 30), coalesce(p_color, '#C2410C'), left(p_platform, 20)) returning * into m;
  return json_build_object('trip_id', t.id, 'member_id', m.id, 'secret', m.secret, 'invite_code', t.invite_code, 'name', t.name);
end $$;

-- everything a phone needs to draw the group: trip, me, members with their latest position, meet point
create or replace function trip_state(p_secret uuid) returns json
language plpgsql security definer set search_path = public as $$
declare me members; t trips;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  update members set seen_at = now() where id = me.id;
  select * into t from trips where id = me.trip_id;
  -- privacy: positions older than 12 hours, or after the trip, are deleted
  delete from positions where trip_id = t.id and (updated_at < now() - interval '12 hours' or (t.ends_on is not null and current_date > t.ends_on + 1));
  return json_build_object(
    'trip', json_build_object('id', t.id, 'name', t.name, 'invite_code', t.invite_code, 'plan', t.plan, 'starts_on', t.starts_on, 'ends_on', t.ends_on),
    'me', me.id,
    'role', me.role,
    'members', coalesce((select json_agg(json_build_object(
        'id', m.id, 'name', m.name, 'color', m.color, 'role', m.role, 'sharing', m.sharing, 'platform', m.platform,
        'pos', case when p.member_id is null or not m.sharing then null else json_build_object(
          'lat', p.lat, 'lon', p.lon, 'acc', p.acc, 'speed', p.speed, 'on_lift', p.on_lift, 'run', p.run, 'km', p.km,
          'age_s', extract(epoch from now() - p.updated_at)::int) end)
        order by m.joined_at)
      from members m left join positions p on p.member_id = m.id where m.trip_id = t.id), '[]'::json),
    'meet', (select json_build_object('lat', lat, 'lon', lon, 'label', label, 'at_time', at_time,
              'by', (select name from members where id = set_by), 'age_s', extract(epoch from now() - updated_at)::int)
             from meet_points where trip_id = t.id));
end $$;

create or replace function post_position(p_secret uuid, p_lat double precision, p_lon double precision, p_acc real default null,
  p_speed real default null, p_on_lift boolean default false, p_run text default null, p_km real default null)
returns boolean language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  if not me.sharing then return false; end if;
  insert into positions(member_id, trip_id, lat, lon, acc, speed, on_lift, run, km, updated_at)
  values (me.id, me.trip_id, p_lat, p_lon, p_acc, p_speed, coalesce(p_on_lift, false), left(p_run, 60), p_km, now())
  on conflict (member_id) do update set lat = excluded.lat, lon = excluded.lon, acc = excluded.acc, speed = excluded.speed,
    on_lift = excluded.on_lift, run = excluded.run, km = excluded.km, updated_at = now();
  return true;
end $$;

create or replace function set_sharing(p_secret uuid, p_on boolean) returns boolean
language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  update members set sharing = p_on where id = me.id;
  if not p_on then delete from positions where member_id = me.id; end if;
  return p_on;
end $$;

create or replace function update_me(p_secret uuid, p_name text, p_color text) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  update members set name = left(trim(coalesce(p_name, name)), 30), color = coalesce(p_color, color) where secret = p_secret;
  return found;
end $$;

create or replace function set_meet(p_secret uuid, p_lat double precision, p_lon double precision, p_label text, p_at text)
returns boolean language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  if p_lat is null then delete from meet_points where trip_id = me.trip_id; return true; end if;
  insert into meet_points(trip_id, lat, lon, label, at_time, set_by, updated_at) values (me.trip_id, p_lat, p_lon, left(p_label, 60), left(p_at, 10), me.id, now())
  on conflict (trip_id) do update set lat = excluded.lat, lon = excluded.lon, label = excluded.label, at_time = excluded.at_time, set_by = excluded.set_by, updated_at = now();
  return true;
end $$;

-- organizer only
create or replace function set_plan(p_secret uuid, p_plan jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null or me.role <> 'owner' then raise exception 'only the organizer can change the plan' using errcode = '42501'; end if;
  update trips set plan = coalesce(p_plan, '{}'::jsonb) where id = me.trip_id;
  return true;
end $$;

create or replace function remove_member(p_secret uuid, p_member uuid) returns boolean
language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  if p_member = me.id then  -- leaving
    if me.role = 'owner' then raise exception 'the organizer can''t leave their own trip'; end if;
    delete from members where id = me.id; return true;
  end if;
  if me.role <> 'owner' then raise exception 'only the organizer can remove people' using errcode = '42501'; end if;
  delete from members where id = p_member and trip_id = me.trip_id;
  return found;
end $$;

-- the app can call these with the public anon key; nothing else is reachable
do $$
declare f text;
begin
  foreach f in array array['create_trip(text,text,text,date,date,text)','trip_preview(text)','join_trip(text,text,text,text)','trip_state(uuid)',
    'post_position(uuid,double precision,double precision,real,real,boolean,text,real)','set_sharing(uuid,boolean)','update_me(uuid,text,text)',
    'set_meet(uuid,double precision,double precision,text,text)','set_plan(uuid,jsonb)','remove_member(uuid,uuid)'] loop
    execute 'revoke all on function ' || f || ' from public';
    if exists (select 1 from pg_roles where rolname = 'anon') then execute 'grant execute on function ' || f || ' to anon'; end if;
    if exists (select 1 from pg_roles where rolname = 'authenticated') then execute 'grant execute on function ' || f || ' to authenticated'; end if;
  end loop;
  execute 'revoke all on function _me(uuid) from public';
  execute 'revoke all on function _code() from public';
end $$;
