-- PART 3: Add UNIQUE constraints
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
