-- ============================================================================
-- SMART RAILWAY RESERVATION SYSTEM
-- A Python Tkinter Application Using Oracle Database and PL/SQL
-- Database Triggers Script: triggers.sql
-- ============================================================================

-- 1. TRIGGER: TRG_RESERVATION_AUDIT
-- Audits all ticket reservations and status transitions into AUDIT_LOG
CREATE OR REPLACE TRIGGER TRG_RESERVATION_AUDIT
AFTER INSERT OR UPDATE ON RESERVATIONS
FOR EACH ROW
DECLARE
    v_op VARCHAR2(20);
    v_details VARCHAR2(1000);
BEGIN
    IF INSERTING THEN
        v_op := 'INSERT';
        v_details := 'New Reservation Created. PNR: ' || :NEW.pnr_number ||
                     ', Schedule ID: ' || :NEW.schedule_id ||
                     ', Class: ' || :NEW.seat_class ||
                     ', Passengers: ' || :NEW.passenger_count ||
                     ', Total Fare: ' || :NEW.total_fare ||
                     ', Status: ' || :NEW.booking_status;
    ELSIF UPDATING THEN
        v_op := 'UPDATE';
        v_details := 'Reservation Updated. PNR: ' || :NEW.pnr_number ||
                     ', Old Status: ' || :OLD.booking_status ||
                     ' -> New Status: ' || :NEW.booking_status;
    END IF;

    INSERT INTO AUDIT_LOG (table_name, operation, record_id, details, logged_at, logged_by)
    VALUES ('RESERVATIONS', v_op, :NEW.reservation_id, v_details, SYSTIMESTAMP, USER);
END TRG_RESERVATION_AUDIT;
/

-- 2. TRIGGER: TRG_CANCELLATION_AUDIT
-- Audits all cancellation requests and refunds into AUDIT_LOG
CREATE OR REPLACE TRIGGER TRG_CANCELLATION_AUDIT
AFTER INSERT ON CANCELLATIONS
FOR EACH ROW
DECLARE
    v_details VARCHAR2(1000);
BEGIN
    v_details := 'Ticket Cancelled. Ref: ' || :NEW.cancellation_ref ||
                 ', Reservation ID: ' || :NEW.reservation_id ||
                 ', Refund Amount: ' || :NEW.refund_amount ||
                 ', Fee: ' || :NEW.cancellation_charge ||
                 ', Reason: ' || :NEW.reason;

    INSERT INTO AUDIT_LOG (table_name, operation, record_id, details, logged_at, logged_by)
    VALUES ('CANCELLATIONS', 'INSERT', :NEW.cancellation_id, v_details, SYSTIMESTAMP, USER);
END TRG_CANCELLATION_AUDIT;
/

-- 3. TRIGGER: TRG_CHECK_SCHEDULE_DATES
-- Validates that train schedule arrival date is not before departure date
CREATE OR REPLACE TRIGGER TRG_CHECK_SCHEDULE_DATES
BEFORE INSERT OR UPDATE ON TRAIN_SCHEDULES
FOR EACH ROW
BEGIN
    IF :NEW.arrival_date < :NEW.departure_date THEN
        RAISE_APPLICATION_ERROR(-20002, 'Arrival date cannot be earlier than departure date.');
    END IF;
END TRG_CHECK_SCHEDULE_DATES;
/

-- 4. TRIGGER: TRG_TRAIN_AUDIT
-- Audits train operational status and capacity modifications into AUDIT_LOG
CREATE OR REPLACE TRIGGER TRG_TRAIN_AUDIT
AFTER INSERT OR UPDATE ON TRAINS
FOR EACH ROW
DECLARE
    v_op VARCHAR2(20);
    v_details VARCHAR2(1000);
BEGIN
    IF INSERTING THEN
        v_op := 'INSERT';
        v_details := 'New Train Registered: ' || :NEW.train_number || ' - ' || :NEW.train_name ||
                     ', Type: ' || :NEW.train_type || ', Capacity: ' || :NEW.total_capacity ||
                     ', Status: ' || :NEW.status;
    ELSIF UPDATING THEN
        v_op := 'UPDATE';
        v_details := 'Train Modified: ' || :NEW.train_number || ' - ' || :NEW.train_name ||
                     ', Old Status: ' || :OLD.status || ' -> New Status: ' || :NEW.status ||
                     ', Old Capacity: ' || :OLD.total_capacity || ' -> New Capacity: ' || :NEW.total_capacity;
    END IF;

    INSERT INTO AUDIT_LOG (table_name, operation, record_id, details, logged_at, logged_by)
    VALUES ('TRAINS', v_op, :NEW.train_id, v_details, SYSTIMESTAMP, USER);
END TRG_TRAIN_AUDIT;
/

