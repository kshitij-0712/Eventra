-- PART 2: Add PRIMARY KEY constraints
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
