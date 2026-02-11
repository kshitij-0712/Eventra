-- PART 5: Add CHECK constraints
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
