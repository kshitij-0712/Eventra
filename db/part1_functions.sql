-- PART 1: Normalize get_average_rating function
DROP FUNCTION IF EXISTS public.get_average_rating(integer);
DROP FUNCTION IF EXISTS public.get_average_rating(uuid);
DROP FUNCTION IF EXISTS public.get_average_rating(bigint);
DROP FUNCTION IF EXISTS public.getaveragerating(bigint);

CREATE OR REPLACE FUNCTION public.get_average_rating(p_event_id bigint)
RETURNS numeric
LANGUAGE sql
STABLE
AS $function$
  select coalesce(avg(rating), 0)
  from tbl_event_feedback
  where event_id = p_event_id;
$function$;
