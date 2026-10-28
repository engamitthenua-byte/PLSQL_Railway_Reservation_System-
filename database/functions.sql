-- ============================================================================
-- SMART RAILWAY RESERVATION SYSTEM
-- A Python Tkinter Application Using Oracle Database and PL/SQL
-- Database Functions Script: functions.sql
-- ============================================================================

-- 1. FUNCTION: CALCULATE_FARE
-- Computes the fare based on distance, train type, travel class, and passenger count
CREATE OR REPLACE FUNCTION CALCULATE_FARE (
    p_distance_km     IN NUMBER,
    p_train_type      IN VARCHAR2,
    p_seat_class      IN VARCHAR2,
    p_passenger_count IN NUMBER
) RETURN NUMBER IS
    v_base_rate_per_km  NUMBER;
    v_class_multiplier  NUMBER;
    v_reservation_fee   NUMBER := 40.00;
    v_superfast_charge  NUMBER := 45.00;
    v_calculated_fare   NUMBER;
BEGIN
    IF p_distance_km IS NULL OR p_distance_km <= 0 OR p_passenger_count IS NULL OR p_passenger_count <= 0 THEN
        RETURN 0.00;
    END IF;

    -- Train type base rate per kilometer
    CASE UPPER(NVL(p_train_type, 'EXPRESS'))
        WHEN 'RAJDHANI' THEN
            v_base_rate_per_km := 1.25;
            v_superfast_charge := 75.00;
        WHEN 'SHATABDI' THEN
            v_base_rate_per_km := 1.20;
            v_superfast_charge := 60.00;
        WHEN 'SUPERFAST' THEN
            v_base_rate_per_km := 0.85;
            v_superfast_charge := 45.00;
        WHEN 'DURONTO' THEN
            v_base_rate_per_km := 1.15;
            v_superfast_charge := 65.00;
        ELSE
            v_base_rate_per_km := 0.65;
            v_superfast_charge := 25.00;
    END CASE;

    -- Seat class multiplier
    CASE UPPER(TRIM(p_seat_class))
        WHEN '1A' THEN v_class_multiplier := 3.20;
        WHEN '2A' THEN v_class_multiplier := 2.20;
        WHEN '3A' THEN v_class_multiplier := 1.55;
        WHEN 'SL' THEN v_class_multiplier := 1.00;
        ELSE v_class_multiplier := 1.00;
    END CASE;

    -- Formula: ((Distance * BaseRate * Multiplier) + Fees) * PassengerCount
    v_calculated_fare := ((p_distance_km * v_base_rate_per_km * v_class_multiplier) +
                          v_reservation_fee + v_superfast_charge) * p_passenger_count;

    -- Round to nearest 5 for realistic railway ticket pricing
    RETURN ROUND(v_calculated_fare, 2);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0.00;
END CALCULATE_FARE;
/

-- 2. FUNCTION: GET_AVAILABLE_SEATS
-- Retrieves currently available unreserved seats for a schedule and class
CREATE OR REPLACE FUNCTION GET_AVAILABLE_SEATS (
    p_schedule_id IN NUMBER,
    p_seat_class  IN VARCHAR2
) RETURN NUMBER IS
    v_available NUMBER := 0;
BEGIN
    SELECT NVL(available_seats, 0)
    INTO v_available
    FROM TRAIN_SEATS
    WHERE schedule_id = p_schedule_id
      AND seat_class = UPPER(TRIM(p_seat_class));

    RETURN v_available;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        RETURN 0;
END GET_AVAILABLE_SEATS;
/

-- 3. FUNCTION: GET_JOURNEY_DURATION
-- Calculates duration in minutes between two station stops of a train
CREATE OR REPLACE FUNCTION GET_JOURNEY_DURATION (
    p_train_id         IN NUMBER,
    p_from_station_id  IN NUMBER,
    p_to_station_id    IN NUMBER
) RETURN NUMBER IS
    v_from_dep_time    VARCHAR2(10);
    v_to_arr_time      VARCHAR2(10);
    v_from_day         NUMBER;
    v_to_day           NUMBER;
    v_from_minutes     NUMBER;
    v_to_minutes       NUMBER;
    v_duration         NUMBER;
BEGIN
    -- Get departure info of origin stop
    SELECT departure_time, day_offset
    INTO v_from_dep_time, v_from_day
    FROM TRAIN_STOPS
    WHERE train_id = p_train_id AND station_id = p_from_station_id;

    -- Get arrival info of destination stop
    SELECT arrival_time, day_offset
    INTO v_to_arr_time, v_to_day
    FROM TRAIN_STOPS
    WHERE train_id = p_train_id AND station_id = p_to_station_id;

    -- Convert HH24:MI to minutes from start of day
    v_from_minutes := (TO_NUMBER(SUBSTR(v_from_dep_time, 1, 2)) * 60) +
                       TO_NUMBER(SUBSTR(v_from_dep_time, 4, 2)) + (v_from_day * 1440);

    v_to_minutes := (TO_NUMBER(SUBSTR(v_to_arr_time, 1, 2)) * 60) +
                     TO_NUMBER(SUBSTR(v_to_arr_time, 4, 2)) + (v_to_day * 1440);

    v_duration := v_to_minutes - v_from_minutes;
    IF v_duration < 0 THEN
        v_duration := v_duration + 1440;
    END IF;

    RETURN v_duration;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN -1; -- Indicates no direct stop connection on this train
    WHEN OTHERS THEN
        RETURN -1;
END GET_JOURNEY_DURATION;
/

-- 4. FUNCTION: GET_RESERVATION_STATUS
-- Quick lookup for current status of a PNR
CREATE OR REPLACE FUNCTION GET_RESERVATION_STATUS (
    p_pnr_number IN VARCHAR2
) RETURN VARCHAR2 IS
    v_status VARCHAR2(20);
BEGIN
    SELECT booking_status
    INTO v_status
    FROM RESERVATIONS
    WHERE pnr_number = UPPER(TRIM(p_pnr_number));

    RETURN v_status;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 'NOT_FOUND';
    WHEN OTHERS THEN
        RETURN 'ERROR';
END GET_RESERVATION_STATUS;
/
