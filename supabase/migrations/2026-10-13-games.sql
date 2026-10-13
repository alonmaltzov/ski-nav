-- Games (STOPPP, passport check, Speed King): run once in the Supabase SQL editor.
alter table members add column if not exists games jsonb not null default '{}'::jsonb;

create or replace function set_games(p_secret uuid, p_games jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare me members;
begin
  me := _me(p_secret);
  if me.id is null then raise exception 'not a member' using errcode = '42501'; end if;
  if p_games is null or jsonb_typeof(p_games) <> 'object' or length(p_games::text) > 2000 then return false; end if;
  update members set games = games || p_games where id = me.id and length((games || p_games)::text) < 20000;
  return true;
end $$;
revoke all on function set_games(uuid,jsonb) from public;
grant execute on function set_games(uuid,jsonb) to anon, authenticated;

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
        'id', m.id, 'name', m.name, 'color', m.color, 'role', m.role, 'sharing', m.sharing, 'platform', m.platform, 'games', m.games,
        'pos', case when p.member_id is null or not m.sharing then null else json_build_object(
          'lat', p.lat, 'lon', p.lon, 'acc', p.acc, 'speed', p.speed, 'on_lift', p.on_lift, 'run', p.run, 'km', p.km,
          'age_s', extract(epoch from now() - p.updated_at)::int) end)
        order by m.joined_at)
      from members m left join positions p on p.member_id = m.id where m.trip_id = t.id), '[]'::json),
    'meet', (select json_build_object('lat', lat, 'lon', lon, 'label', label, 'at_time', at_time,
              'by', (select name from members where id = set_by), 'age_s', extract(epoch from now() - updated_at)::int)
             from meet_points where trip_id = t.id));
end $$;
