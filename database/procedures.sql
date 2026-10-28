-- ============================================================================
-- SMART RAILWAY RESERVATION SYSTEM
-- A Python Tkinter Application Using Oracle Database and PL/SQL
-- Stored Procedures Script: procedures.sql
-- ============================================================================

-- 1. PROCEDURE: REGISTER_PASSENGER
CREATE OR REPLACE PROCEDURE REGISTER_PASSENGER (
    p_full_name       IN  VARCHAR2,
    p_age             IN  NUMBER,
    p_gender          IN  VARCHAR2,
    p_phone_number    IN  VARCHAR2,
    p_email           IN  VARCHAR2,
    o_passenger_id    OUT NUMBER,
    o_status_code     OUT NUMBER, -- 0: Success, 1: Validation Error, 2: DB Error
    o_message         OUT VARCHAR2
) AS
BEGIN
    -- Input validations
    IF p_full_name IS NULL OR TRIM(p_full_name) = '' THEN
        o_status_code := 1;
        o_message := 'Passenger full name cannot be blank.';
        RETURN;
    END IF;

    IF p_age < 1 OR p_age > 120 THEN
        o_status_code := 1;
        o_message := 'Age must be between 1 and 120.';
        RETURN;
    END IF;

    IF p_gender NOT IN ('Male', 'Female', 'Other') THEN
        o_status_code := 1;
        o_message := 'Gender must be Male, Female, or Other.';
        RETURN;
    END IF;

    IF p_phone_number IS NULL OR LENGTH(TRIM(p_phone_number)) < 7 THEN
        o_status_code := 1;
        o_message := 'Please provide a valid contact phone number.';
        RETURN;
    END IF;

    INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email, registration_date)
    VALUES (TRIM(p_full_name), p_age, p_gender, TRIM(p_phone_number), LOWER(TRIM(p_email)), SYSDATE)
    RETURNING passenger_id INTO o_passenger_id;

    COMMIT;
    o_status_code := 0;
    o_message := 'Passenger registered successfully with ID: ' || o_passenger_id;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error registering passenger: ' || SQLERRM;
END REGISTER_PASSENGER;
/

-- 2. PROCEDURE: ADD_STATION
CREATE OR REPLACE PROCEDURE ADD_STATION (
    p_station_code    IN  VARCHAR2,
    p_station_name    IN  VARCHAR2,
    p_city            IN  VARCHAR2,
    p_state           IN  VARCHAR2,
    o_station_id      OUT NUMBER,
    o_status_code     OUT NUMBER,
    o_message         OUT VARCHAR2
) AS
    v_clean_code VARCHAR2(10);
BEGIN
    v_clean_code := UPPER(TRIM(p_station_code));
    IF v_clean_code IS NULL OR LENGTH(v_clean_code) < 2 THEN
        o_status_code := 1;
        o_message := 'Invalid station code. Must be at least 2 characters.';
        RETURN;
    END IF;

    INSERT INTO STATIONS (station_code, station_name, city, state)
    VALUES (v_clean_code, TRIM(p_station_name), TRIM(p_city), TRIM(p_state))
    RETURNING station_id INTO o_station_id;

    COMMIT;
    o_status_code := 0;
    o_message := 'Station ' || v_clean_code || ' created successfully with ID: ' || o_station_id;

EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        ROLLBACK;
        o_status_code := 1;
        o_message := 'A station with code ' || v_clean_code || ' already exists.';
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error adding station: ' || SQLERRM;
END ADD_STATION;
/

-- 3. PROCEDURE: ADD_TRAIN
CREATE OR REPLACE PROCEDURE ADD_TRAIN (
    p_train_number      IN  VARCHAR2,
    p_train_name        IN  VARCHAR2,
    p_train_type        IN  VARCHAR2,
    p_source_station_id IN  NUMBER,
    p_dest_station_id   IN  NUMBER,
    p_total_capacity    IN  NUMBER,
    o_train_id          OUT NUMBER,
    o_status_code       OUT NUMBER,
    o_message           OUT VARCHAR2
) AS
    v_clean_num VARCHAR2(10);
    v_src_count NUMBER;
    v_dst_count NUMBER;
BEGIN
    v_clean_num := UPPER(TRIM(p_train_number));
    IF p_source_station_id = p_dest_station_id THEN
        o_status_code := 1;
        o_message := 'Source and destination stations cannot be the same.';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_src_count FROM STATIONS WHERE station_id = p_source_station_id;
    SELECT COUNT(*) INTO v_dst_count FROM STATIONS WHERE station_id = p_dest_station_id;
    IF v_src_count = 0 OR v_dst_count = 0 THEN
        o_status_code := 1;
        o_message := 'Source or destination station ID does not exist.';
        RETURN;
    END IF;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES (v_clean_num, TRIM(p_train_name), NVL(p_train_type, 'Superfast'), p_source_station_id, p_dest_station_id, NVL(p_total_capacity, 500), 'ACTIVE')
    RETURNING train_id INTO o_train_id;

    COMMIT;
    o_status_code := 0;
    o_message := 'Train ' || v_clean_num || ' registered successfully with ID: ' || o_train_id;

EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        ROLLBACK;
        o_status_code := 1;
        o_message := 'Train with number ' || v_clean_num || ' already exists.';
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error adding train: ' || SQLERRM;
END ADD_TRAIN;
/

-- 4. PROCEDURE: BOOK_TICKET (Transaction-Safe & Concurrency-Safe)
-- Uses SELECT ... FOR UPDATE to eliminate race conditions / overbooking
CREATE OR REPLACE PROCEDURE BOOK_TICKET (
    p_passenger_id      IN  NUMBER,
    p_schedule_id       IN  NUMBER,
    p_from_station_id   IN  NUMBER,
    p_to_station_id     IN  NUMBER,
    p_journey_date      IN  DATE,
    p_seat_class        IN  VARCHAR2,
    p_passenger_count   IN  NUMBER,
    p_total_fare        IN  NUMBER,
    p_payment_method    IN  VARCHAR2,
    o_reservation_id    OUT NUMBER,
    o_pnr_number        OUT VARCHAR2,
    o_status_code       OUT NUMBER, -- 0: Success, 1: Validation/Capacity error, 2: System Error
    o_message           OUT VARCHAR2
) AS
    v_avail_seats       NUMBER;
    v_booked_seats      NUMBER;
    v_total_seats       NUMBER;
    v_sched_status      VARCHAR2(20);
    v_pnr               VARCHAR2(20);
    v_tx_ref            VARCHAR2(50);
    v_res_id            NUMBER;
    v_class_clean       VARCHAR2(10);
BEGIN
    v_class_clean := UPPER(TRIM(p_seat_class));

    -- Basic input validation
    IF p_passenger_count <= 0 THEN
        o_status_code := 1;
        o_message := 'Passenger count must be at least 1.';
        RETURN;
    END IF;

    IF p_from_station_id = p_to_station_id THEN
        o_status_code := 1;
        o_message := 'From and To station cannot be the same.';
        RETURN;
    END IF;

    -- Verify schedule status
    BEGIN
        SELECT status INTO v_sched_status
        FROM TRAIN_SCHEDULES
        WHERE schedule_id = p_schedule_id;

        IF v_sched_status <> 'SCHEDULED' AND v_sched_status <> 'RUNNING' THEN
            o_status_code := 1;
            o_message := 'Train schedule is currently ' || v_sched_status || ' and not open for booking.';
            RETURN;
        END IF;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            o_status_code := 1;
            o_message := 'Specified train schedule does not exist.';
            RETURN;
    END;

    -- CRITICAL CONCURRENCY SAFEGUARD:
    -- Lock inventory row for this specific schedule & class using SELECT FOR UPDATE
    BEGIN
        SELECT available_seats, booked_seats, total_seats
        INTO v_avail_seats, v_booked_seats, v_total_seats
        FROM TRAIN_SEATS
        WHERE schedule_id = p_schedule_id
          AND seat_class = v_class_clean
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            o_status_code := 1;
            o_message := 'Seat inventory for class ' || v_class_clean || ' not configured for this schedule.';
            RETURN;
    END;

    -- Check if sufficient seats are available
    IF v_avail_seats < p_passenger_count THEN
        ROLLBACK;
        o_status_code := 1;
        o_message := 'Insufficient seats available in ' || v_class_clean || '. Requested: ' ||
                     p_passenger_count || ', Available: ' || v_avail_seats;
        RETURN;
    END IF;

    -- Generate unique PNR (10-digit format: e.g., 23A + 7 digits)
    v_pnr := 'PNR' || TO_CHAR(SYSDATE, 'YYMMDD') || LPAD(TO_CHAR(MOD(ABS(DBMS_RANDOM.RANDOM), 10000)), 4, '0');
    v_tx_ref := 'TXN-' || TO_CHAR(SYSTIMESTAMP, 'YYYYMMDDHH24MISSFF3');

    -- Insert reservation record
    INSERT INTO RESERVATIONS (
        pnr_number, passenger_id, schedule_id, from_station_id, to_station_id,
        journey_date, seat_class, passenger_count, total_fare, booking_status, booking_time
    ) VALUES (
        v_pnr, p_passenger_id, p_schedule_id, p_from_station_id, p_to_station_id,
        TRUNC(p_journey_date), v_class_clean, p_passenger_count, p_total_fare, 'CONFIRMED', SYSTIMESTAMP
    ) RETURNING reservation_id INTO v_res_id;

    -- Deduct seats atomically
    UPDATE TRAIN_SEATS
    SET booked_seats = booked_seats + p_passenger_count,
        available_seats = available_seats - p_passenger_count,
        last_updated = SYSTIMESTAMP
    WHERE schedule_id = p_schedule_id
      AND seat_class = v_class_clean;

    -- Record payment transaction
    INSERT INTO BOOKING_TRANSACTIONS (
        reservation_id, transaction_ref, amount, payment_method, payment_status, transaction_time
    ) VALUES (
        v_res_id, v_tx_ref, p_total_fare, NVL(p_payment_method, 'UPI'), 'SUCCESS', SYSTIMESTAMP
    );

    -- Commit transaction atomically
    COMMIT;

    o_reservation_id := v_res_id;
    o_pnr_number := v_pnr;
    o_status_code := 0;
    o_message := 'Booking successful! Confirmed PNR: ' || v_pnr;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Booking transaction failed: ' || SQLERRM;
END BOOK_TICKET;
/

-- 5. PROCEDURE: CANCEL_TICKET (Transaction-Safe Cancellation & Seat Inventory Restoration)
CREATE OR REPLACE PROCEDURE CANCEL_TICKET (
    p_pnr_number          IN  VARCHAR2,
    p_reason              IN  VARCHAR2,
    o_refund_amount       OUT NUMBER,
    o_cancellation_charge OUT NUMBER,
    o_status_code         OUT NUMBER,
    o_message             OUT VARCHAR2
) AS
    v_res_id            NUMBER;
    v_sched_id          NUMBER;
    v_seat_class        VARCHAR2(10);
    v_pass_count        NUMBER;
    v_total_fare        NUMBER;
    v_status            VARCHAR2(20);
    v_cancel_ref        VARCHAR2(50);
    v_charge_rate       NUMBER := 0.20; -- 20% cancellation fee
    v_charge            NUMBER;
    v_refund            NUMBER;
BEGIN
    IF p_pnr_number IS NULL OR TRIM(p_pnr_number) = '' THEN
        o_status_code := 1;
        o_message := 'PNR number must be provided.';
        RETURN;
    END IF;

    -- Lock reservation row
    BEGIN
        SELECT reservation_id, schedule_id, seat_class, passenger_count, total_fare, booking_status
        INTO v_res_id, v_sched_id, v_seat_class, v_pass_count, v_total_fare, v_status
        FROM RESERVATIONS
        WHERE pnr_number = UPPER(TRIM(p_pnr_number))
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            o_status_code := 1;
            o_message := 'No reservation found for PNR: ' || p_pnr_number;
            RETURN;
    END;

    IF v_status = 'CANCELLED' THEN
        o_status_code := 1;
        o_message := 'Reservation with PNR ' || p_pnr_number || ' is already cancelled.';
        RETURN;
    END IF;

    -- Calculate charges and refund (Academic rule: 20% fee, min 60.00)
    v_charge := ROUND(GREATEST(v_total_fare * v_charge_rate, 60.00), 2);
    IF v_charge > v_total_fare THEN
        v_charge := v_total_fare;
    END IF;
    v_refund := ROUND(v_total_fare - v_charge, 2);

    -- Restore inventory in TRAIN_SEATS
    UPDATE TRAIN_SEATS
    SET booked_seats = booked_seats - v_pass_count,
        available_seats = available_seats + v_pass_count,
        last_updated = SYSTIMESTAMP
    WHERE schedule_id = v_sched_id
      AND seat_class = v_seat_class;

    -- Update reservation status
    UPDATE RESERVATIONS
    SET booking_status = 'CANCELLED'
    WHERE reservation_id = v_res_id;

    -- Update transaction payment status
    UPDATE BOOKING_TRANSACTIONS
    SET payment_status = 'REFUNDED'
    WHERE reservation_id = v_res_id;

    -- Record cancellation entry
    v_cancel_ref := 'CAN-' || TO_CHAR(SYSTIMESTAMP, 'YYYYMMDDHH24MISSFF3');
    INSERT INTO CANCELLATIONS (
        reservation_id, cancellation_ref, cancellation_time, refund_amount, cancellation_charge, reason
    ) VALUES (
        v_res_id, v_cancel_ref, SYSTIMESTAMP, v_refund, v_charge, NVL(p_reason, 'Customer Request')
    );

    COMMIT;

    o_refund_amount := v_refund;
    o_cancellation_charge := v_charge;
    o_status_code := 0;
    o_message := 'Ticket cancelled successfully. Refund amount: ' || TO_CHAR(v_refund, '999990.99') ||
                 ', Cancellation fee: ' || TO_CHAR(v_charge, '999990.99');

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Cancellation error: ' || SQLERRM;
END CANCEL_TICKET;
/

-- 6. PROCEDURE: UPDATE_TRAIN_SCHEDULE
CREATE OR REPLACE PROCEDURE UPDATE_TRAIN_SCHEDULE (
    p_schedule_id   IN  NUMBER,
    p_base_fare     IN  NUMBER,
    p_status        IN  VARCHAR2,
    o_status_code   OUT NUMBER,
    o_message       OUT VARCHAR2
) AS
BEGIN
    UPDATE TRAIN_SCHEDULES
    SET base_fare = NVL(p_base_fare, base_fare),
        status = NVL(p_status, status)
    WHERE schedule_id = p_schedule_id;

    IF SQL%ROWCOUNT = 0 THEN
        o_status_code := 1;
        o_message := 'Schedule ID ' || p_schedule_id || ' not found.';
        RETURN;
    END IF;

    COMMIT;
    o_status_code := 0;
    o_message := 'Schedule updated successfully.';
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Failed to update schedule: ' || SQLERRM;
END UPDATE_TRAIN_SCHEDULE;
/

-- 7. PROCEDURE: GET_RESERVATION_DETAILS (Returns SYS_REFCURSOR for rich cursor processing)
CREATE OR REPLACE PROCEDURE GET_RESERVATION_DETAILS (
    p_pnr_number      IN  VARCHAR2,
    o_res_cursor      OUT SYS_REFCURSOR,
    o_pass_cursor     OUT SYS_REFCURSOR,
    o_status_code     OUT NUMBER,
    o_message         OUT VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM RESERVATIONS
    WHERE pnr_number = UPPER(TRIM(p_pnr_number));

    IF v_count = 0 THEN
        o_status_code := 1;
        o_message := 'Reservation not found for PNR: ' || p_pnr_number;
        RETURN;
    END IF;

    -- Open cursor for main reservation details
    OPEN o_res_cursor FOR
        SELECT r.reservation_id, r.pnr_number, r.journey_date, r.seat_class,
               r.passenger_count, r.total_fare, r.booking_status, r.booking_time,
               p.passenger_id, p.full_name AS primary_passenger, p.phone_number, p.email,
               t.train_number, t.train_name, t.train_type,
               s_from.station_code AS from_code, s_from.station_name AS from_name,
               s_to.station_code AS to_code, s_to.station_name AS to_name,
               c.refund_amount, c.cancellation_charge, c.cancellation_time
        FROM RESERVATIONS r
        JOIN PASSENGERS p ON r.passenger_id = p.passenger_id
        JOIN TRAIN_SCHEDULES sch ON r.schedule_id = sch.schedule_id
        JOIN TRAINS t ON sch.train_id = t.train_id
        JOIN STATIONS s_from ON r.from_station_id = s_from.station_id
        JOIN STATIONS s_to ON r.to_station_id = s_to.station_id
        LEFT JOIN CANCELLATIONS c ON r.reservation_id = c.reservation_id
        WHERE r.pnr_number = UPPER(TRIM(p_pnr_number));

    -- Open cursor for passengers in reservation
    OPEN o_pass_cursor FOR
        SELECT rp.res_passenger_id, rp.passenger_name, rp.age, rp.gender, rp.seat_number
        FROM RESERVATION_PASSENGERS rp
        JOIN RESERVATIONS r ON rp.reservation_id = r.reservation_id
        WHERE r.pnr_number = UPPER(TRIM(p_pnr_number))
        ORDER BY rp.res_passenger_id;

    o_status_code := 0;
    o_message := 'Details retrieved successfully.';
EXCEPTION
    WHEN OTHERS THEN
        o_status_code := 2;
        o_message := 'Error retrieving reservation details: ' || SQLERRM;
END GET_RESERVATION_DETAILS;
/

-- 8. PROCEDURE: GENERATE_BOOKING_REPORT
CREATE OR REPLACE PROCEDURE GENERATE_BOOKING_REPORT (
    p_from_date       IN  DATE,
    p_to_date         IN  DATE,
    o_report_cursor   OUT SYS_REFCURSOR
) AS
BEGIN
    OPEN o_report_cursor FOR
        SELECT t.train_number,
               t.train_name,
               COUNT(r.reservation_id) AS total_reservations,
               SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.passenger_count ELSE 0 END) AS confirmed_passengers,
               SUM(CASE WHEN r.booking_status = 'CANCELLED' THEN r.passenger_count ELSE 0 END) AS cancelled_passengers,
               NVL(SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.total_fare ELSE 0 END), 0) AS gross_revenue,
               NVL(SUM(c.cancellation_charge), 0) AS cancellation_fees_retained,
               NVL(SUM(CASE WHEN r.booking_status = 'CONFIRMED' THEN r.total_fare ELSE 0 END), 0) +
               NVL(SUM(c.cancellation_charge), 0) AS net_revenue
        FROM TRAINS t
        LEFT JOIN TRAIN_SCHEDULES sch ON t.train_id = sch.train_id
        LEFT JOIN RESERVATIONS r ON sch.schedule_id = r.schedule_id
             AND (p_from_date IS NULL OR r.journey_date >= TRUNC(p_from_date))
             AND (p_to_date IS NULL OR r.journey_date <= TRUNC(p_to_date))
        LEFT JOIN CANCELLATIONS c ON r.reservation_id = c.reservation_id
        GROUP BY t.train_number, t.train_name
        ORDER BY net_revenue DESC;
END GENERATE_BOOKING_REPORT;
/

-- 9. PROCEDURE: UPDATE_PASSENGER
CREATE OR REPLACE PROCEDURE UPDATE_PASSENGER (
    p_passenger_id    IN  NUMBER,
    p_full_name       IN  VARCHAR2,
    p_age             IN  NUMBER,
    p_gender          IN  VARCHAR2,
    p_phone_number    IN  VARCHAR2,
    p_email           IN  VARCHAR2,
    o_status_code     OUT NUMBER, -- 0: Success, 1: Validation Error, 2: DB Error
    o_message         OUT VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    IF p_passenger_id IS NULL THEN
        o_status_code := 1;
        o_message := 'Passenger ID must be provided.';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM PASSENGERS WHERE passenger_id = p_passenger_id;
    IF v_count = 0 THEN
        o_status_code := 1;
        o_message := 'Passenger with ID ' || p_passenger_id || ' does not exist.';
        RETURN;
    END IF;

    IF p_full_name IS NULL OR TRIM(p_full_name) = '' THEN
        o_status_code := 1;
        o_message := 'Passenger full name cannot be blank.';
        RETURN;
    END IF;

    IF p_age < 1 OR p_age > 120 THEN
        o_status_code := 1;
        o_message := 'Age must be between 1 and 120.';
        RETURN;
    END IF;

    IF p_gender NOT IN ('Male', 'Female', 'Other') THEN
        o_status_code := 1;
        o_message := 'Gender must be Male, Female, or Other.';
        RETURN;
    END IF;

    IF p_phone_number IS NULL OR LENGTH(TRIM(p_phone_number)) < 7 THEN
        o_status_code := 1;
        o_message := 'Please provide a valid contact phone number.';
        RETURN;
    END IF;

    UPDATE PASSENGERS
    SET full_name = TRIM(p_full_name),
        age = p_age,
        gender = p_gender,
        phone_number = TRIM(p_phone_number),
        email = LOWER(TRIM(p_email))
    WHERE passenger_id = p_passenger_id;

    COMMIT;
    o_status_code := 0;
    o_message := 'Passenger ID ' || p_passenger_id || ' updated successfully.';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error updating passenger: ' || SQLERRM;
END UPDATE_PASSENGER;
/

-- 10. PROCEDURE: DELETE_PASSENGER
-- Prevents deletion of passengers who have active or historical reservations
CREATE OR REPLACE PROCEDURE DELETE_PASSENGER (
    p_passenger_id    IN  NUMBER,
    o_status_code     OUT NUMBER, -- 0: Success, 1: Constraint/Business rule violation, 2: DB Error
    o_message         OUT VARCHAR2
) AS
    v_count NUMBER;
    v_res_count NUMBER;
BEGIN
    IF p_passenger_id IS NULL THEN
        o_status_code := 1;
        o_message := 'Passenger ID must be provided.';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM PASSENGERS WHERE passenger_id = p_passenger_id;
    IF v_count = 0 THEN
        o_status_code := 1;
        o_message := 'Passenger with ID ' || p_passenger_id || ' does not exist.';
        RETURN;
    END IF;

    -- Referential integrity business rule:
    -- Prevent deletion of passengers who have reservations that must be retained for historical records
    SELECT COUNT(*) INTO v_res_count FROM RESERVATIONS WHERE passenger_id = p_passenger_id;
    IF v_res_count > 0 THEN
        o_status_code := 1;
        o_message := 'Cannot delete passenger: ' || v_res_count || ' historical or active reservation(s) exist for this passenger.';
        RETURN;
    END IF;

    DELETE FROM PASSENGERS WHERE passenger_id = p_passenger_id;
    COMMIT;
    o_status_code := 0;
    o_message := 'Passenger ID ' || p_passenger_id || ' deleted successfully.';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error deleting passenger: ' || SQLERRM;
END DELETE_PASSENGER;
/

-- 11. PROCEDURE: UPDATE_TRAIN
CREATE OR REPLACE PROCEDURE UPDATE_TRAIN (
    p_train_id        IN  NUMBER,
    p_train_name      IN  VARCHAR2,
    p_train_type      IN  VARCHAR2,
    p_total_capacity  IN  NUMBER,
    p_status          IN  VARCHAR2,
    o_status_code     OUT NUMBER,
    o_message         OUT VARCHAR2
) AS
    v_count NUMBER;
    v_clean_status VARCHAR2(20);
BEGIN
    IF p_train_id IS NULL THEN
        o_status_code := 1;
        o_message := 'Train ID must be provided.';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM TRAINS WHERE train_id = p_train_id;
    IF v_count = 0 THEN
        o_status_code := 1;
        o_message := 'Train with ID ' || p_train_id || ' does not exist.';
        RETURN;
    END IF;

    IF p_train_name IS NULL OR TRIM(p_train_name) = '' THEN
        o_status_code := 1;
        o_message := 'Train name cannot be blank.';
        RETURN;
    END IF;

    IF p_total_capacity IS NOT NULL AND p_total_capacity <= 0 THEN
        o_status_code := 1;
        o_message := 'Total capacity must be a positive integer.';
        RETURN;
    END IF;

    v_clean_status := UPPER(TRIM(NVL(p_status, 'ACTIVE')));
    IF v_clean_status NOT IN ('ACTIVE', 'MAINTENANCE', 'CANCELLED') THEN
        o_status_code := 1;
        o_message := 'Train status must be ACTIVE, MAINTENANCE, or CANCELLED.';
        RETURN;
    END IF;

    UPDATE TRAINS
    SET train_name = TRIM(p_train_name),
        train_type = NVL(p_train_type, train_type),
        total_capacity = NVL(p_total_capacity, total_capacity),
        status = v_clean_status
    WHERE train_id = p_train_id;

    COMMIT;
    o_status_code := 0;
    o_message := 'Train ID ' || p_train_id || ' updated successfully.';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        o_status_code := 2;
        o_message := 'Database error updating train: ' || SQLERRM;
END UPDATE_TRAIN;
/

