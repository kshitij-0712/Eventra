-- ============================================================
-- EVENTRA SCHEMA UPDATES
-- Run this entire script in Supabase SQL Editor
-- ============================================================

-- ============================================================
-- PART 1: Normalize get_average_rating function
-- ============================================================
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

-- ============================================================
-- PART 2: Add PRIMARY KEY constraints
-- (uses standard syntax; PG will reuse existing unique index)
-- ============================================================
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_events_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_events ADD CONSTRAINT tbl_events_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_students_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_students ADD CONSTRAINT tbl_students_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_hosts_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_hosts ADD CONSTRAINT tbl_hosts_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_venues_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_venues ADD CONSTRAINT tbl_venues_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_tickets_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_tickets ADD CONSTRAINT tbl_tickets_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_orders_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_orders ADD CONSTRAINT tbl_orders_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resources_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resources ADD CONSTRAINT tbl_resources_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants ADD CONSTRAINT tbl_event_participants_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback ADD CONSTRAINT tbl_event_feedback_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources ADD CONSTRAINT tbl_event_resources_pkey PRIMARY KEY (id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resource_maintenance_pkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resource_maintenance ADD CONSTRAINT tbl_resource_maintenance_pkey PRIMARY KEY (id);
  END IF;
END$$;

-- ============================================================
-- PART 3: Add UNIQUE constraints
-- ============================================================
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_students_srn_unique' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_students ADD CONSTRAINT tbl_students_srn_unique UNIQUE (srn);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_hosts_email_unique' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_hosts ADD CONSTRAINT tbl_hosts_email_unique UNIQUE (email);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_hosts_phone_unique' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_hosts ADD CONSTRAINT tbl_hosts_phone_unique UNIQUE (phone);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_event_user_unique' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback ADD CONSTRAINT tbl_event_feedback_event_user_unique UNIQUE (event_id, user_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_event_user_unique' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants ADD CONSTRAINT tbl_event_participants_event_user_unique UNIQUE (event_id, user_id);
  END IF;
END$$;

-- ============================================================
-- PART 4: Add FOREIGN KEY constraints
-- ============================================================
DO $$
BEGIN
  -- tbl_events.organizer_id -> tbl_hosts.id (RESTRICT)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_events_organizer_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_events
      ADD CONSTRAINT tbl_events_organizer_id_fkey
      FOREIGN KEY (organizer_id) REFERENCES public.tbl_hosts(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;

  -- tbl_events.location_id -> tbl_venues.id (SET NULL)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_events_location_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_events
      ADD CONSTRAINT tbl_events_location_id_fkey
      FOREIGN KEY (location_id) REFERENCES public.tbl_venues(id)
      ON DELETE SET NULL NOT VALID;
  END IF;

  -- tbl_tickets.event_id -> tbl_events.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_tickets_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_tickets
      ADD CONSTRAINT tbl_tickets_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_participants.event_id -> tbl_events.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants
      ADD CONSTRAINT tbl_event_participants_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_participants.user_id -> tbl_students.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants
      ADD CONSTRAINT tbl_event_participants_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_feedback.event_id -> tbl_events.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback
      ADD CONSTRAINT tbl_event_feedback_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_feedback.user_id -> tbl_students.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback
      ADD CONSTRAINT tbl_event_feedback_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_orders.ticket_id -> tbl_tickets.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_orders_ticket_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_orders
      ADD CONSTRAINT tbl_orders_ticket_id_fkey
      FOREIGN KEY (ticket_id) REFERENCES public.tbl_tickets(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_orders.user_id -> tbl_students.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_orders_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_orders
      ADD CONSTRAINT tbl_orders_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_resources.event_id -> tbl_events.id (CASCADE)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  -- tbl_event_resources.resource_id -> tbl_resources.id (RESTRICT)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_resource_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_resource_id_fkey
      FOREIGN KEY (resource_id) REFERENCES public.tbl_resources(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;

  -- tbl_resource_maintenance.resource_id -> tbl_resources.id (RESTRICT)
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resource_maintenance_resource_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resource_maintenance
      ADD CONSTRAINT tbl_resource_maintenance_resource_id_fkey
      FOREIGN KEY (resource_id) REFERENCES public.tbl_resources(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;
END$$;

-- ============================================================
-- PART 5: Add CHECK constraints
-- ============================================================
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_rating_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback
      ADD CONSTRAINT tbl_event_feedback_rating_check CHECK (rating BETWEEN 1 AND 5) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_tickets_quantity_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_tickets
      ADD CONSTRAINT tbl_tickets_quantity_check CHECK (quantity >= 0) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_tickets_price_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_tickets
      ADD CONSTRAINT tbl_tickets_price_check CHECK (price >= 0) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resources_quantity_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resources
      ADD CONSTRAINT tbl_resources_quantity_check CHECK (quantity >= 0) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_quantity_booked_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_quantity_booked_check CHECK (quantity_booked > 0) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_booking_window_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_booking_window_check CHECK (booking_end > booking_start) NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resource_maintenance_window_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resource_maintenance
      ADD CONSTRAINT tbl_resource_maintenance_window_check CHECK (maintenance_end IS NULL OR maintenance_end > maintenance_start) NOT VALID;
  END IF;
END$$;

-- ============================================================
-- PART 6: Add performance indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS tbl_event_participants_user_id_idx
  ON public.tbl_event_participants(user_id);
CREATE INDEX IF NOT EXISTS tbl_tickets_event_id_idx
  ON public.tbl_tickets(event_id);
CREATE INDEX IF NOT EXISTS tbl_orders_user_id_idx
  ON public.tbl_orders(user_id);
CREATE INDEX IF NOT EXISTS tbl_orders_ticket_id_idx
  ON public.tbl_orders(ticket_id);
CREATE INDEX IF NOT EXISTS tbl_event_feedback_event_id_idx
  ON public.tbl_event_feedback(event_id);
CREATE INDEX IF NOT EXISTS tbl_event_resources_event_id_idx
  ON public.tbl_event_resources(event_id);
