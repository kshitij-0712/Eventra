-- PART 4: Add FOREIGN KEY constraints
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_events_organizer_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_events
      ADD CONSTRAINT tbl_events_organizer_id_fkey
      FOREIGN KEY (organizer_id) REFERENCES public.tbl_hosts(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_events_location_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_events
      ADD CONSTRAINT tbl_events_location_id_fkey
      FOREIGN KEY (location_id) REFERENCES public.tbl_venues(id)
      ON DELETE SET NULL NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_tickets_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_tickets
      ADD CONSTRAINT tbl_tickets_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants
      ADD CONSTRAINT tbl_event_participants_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_participants_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_participants
      ADD CONSTRAINT tbl_event_participants_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback
      ADD CONSTRAINT tbl_event_feedback_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_feedback_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_feedback
      ADD CONSTRAINT tbl_event_feedback_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_orders_ticket_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_orders
      ADD CONSTRAINT tbl_orders_ticket_id_fkey
      FOREIGN KEY (ticket_id) REFERENCES public.tbl_tickets(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_orders_user_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_orders
      ADD CONSTRAINT tbl_orders_user_id_fkey
      FOREIGN KEY (user_id) REFERENCES public.tbl_students(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_event_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_event_id_fkey
      FOREIGN KEY (event_id) REFERENCES public.tbl_events(id)
      ON DELETE CASCADE NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_event_resources_resource_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_event_resources
      ADD CONSTRAINT tbl_event_resources_resource_id_fkey
      FOREIGN KEY (resource_id) REFERENCES public.tbl_resources(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tbl_resource_maintenance_resource_id_fkey' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.tbl_resource_maintenance
      ADD CONSTRAINT tbl_resource_maintenance_resource_id_fkey
      FOREIGN KEY (resource_id) REFERENCES public.tbl_resources(id)
      ON DELETE RESTRICT NOT VALID;
  END IF;
END$$;
