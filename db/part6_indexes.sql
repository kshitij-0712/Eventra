-- PART 6: Add performance indexes
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
