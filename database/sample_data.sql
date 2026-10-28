-- ============================================================================
-- SMART RAILWAY RESERVATION AND ROUTE OPTIMIZATION SYSTEM
-- Sample Data Script: sample_data.sql
-- ============================================================================

-- 1. INSERT STATIONS (12 Major Stations across India)
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('NDLS', 'New Delhi Railway Station', 'New Delhi', 'Delhi');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('MMCT', 'Mumbai Central', 'Mumbai', 'Maharashtra');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('SBC', 'KSR Bengaluru City', 'Bengaluru', 'Karnataka');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('LKO', 'Lucknow Charbagh', 'Lucknow', 'Uttar Pradesh');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'Telangana');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh');
INSERT INTO STATIONS (station_code, station_name, city, state) VALUES ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh');

COMMIT;

-- 2. INSERT PASSENGERS
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Aarav Sharma', 29, 'Male', '9876543210', 'aarav.sharma@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Priya Patel', 26, 'Female', '9812345678', 'priya.patel@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Rajesh Kumar', 45, 'Male', '9823456789', 'rajesh.k@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Ananya Iyer', 32, 'Female', '9834567890', 'ananya.iyer@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Vikram Singh', 52, 'Male', '9845678901', 'vikram.singh@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Sneha Kulkarni', 24, 'Female', '9856789012', 'sneha.k@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Mohammad Tariq', 38, 'Male', '9867890123', 'm.tariq@example.com');
INSERT INTO PASSENGERS (full_name, age, gender, phone_number, email) VALUES ('Deepika Reddy', 30, 'Female', '9878901234', 'deepika.r@example.com');

COMMIT;
/

-- 3. INSERT TRAINS (10 Trains)
-- Helper: Map station codes to IDs
DECLARE
    v_ndls NUMBER; v_mmct NUMBER; v_hwh NUMBER; v_mas NUMBER;
    v_sbc  NUMBER; v_adi  NUMBER; v_jp  NUMBER; v_lko NUMBER;
    v_hyb  NUMBER; v_pune NUMBER; v_cnb NUMBER; v_bpl NUMBER;

    v_t1 NUMBER; v_t2 NUMBER; v_t3 NUMBER; v_t4 NUMBER; v_t5 NUMBER;
    v_t6 NUMBER; v_t7 NUMBER; v_t8 NUMBER; v_t9 NUMBER; v_t10 NUMBER;
    v_t11 NUMBER; v_t12 NUMBER;

    v_sch1 NUMBER; v_sch2 NUMBER; v_sch3 NUMBER; v_sch4 NUMBER; v_sch5 NUMBER;
    v_sch6 NUMBER; v_sch7 NUMBER; v_sch8 NUMBER; v_sch9 NUMBER; v_sch10 NUMBER;
    v_sch11 NUMBER; v_sch12 NUMBER;
    v_day NUMBER;

    v_res1 NUMBER; v_res2 NUMBER;
BEGIN
    SELECT station_id INTO v_ndls FROM STATIONS WHERE station_code = 'NDLS';
    SELECT station_id INTO v_mmct FROM STATIONS WHERE station_code = 'MMCT';
    SELECT station_id INTO v_hwh  FROM STATIONS WHERE station_code = 'HWH';
    SELECT station_id INTO v_mas  FROM STATIONS WHERE station_code = 'MAS';
    SELECT station_id INTO v_sbc  FROM STATIONS WHERE station_code = 'SBC';
    SELECT station_id INTO v_adi  FROM STATIONS WHERE station_code = 'ADI';
    SELECT station_id INTO v_jp   FROM STATIONS WHERE station_code = 'JP';
    SELECT station_id INTO v_lko  FROM STATIONS WHERE station_code = 'LKO';
    SELECT station_id INTO v_hyb  FROM STATIONS WHERE station_code = 'HYB';
    SELECT station_id INTO v_pune FROM STATIONS WHERE station_code = 'PUNE';
    SELECT station_id INTO v_cnb  FROM STATIONS WHERE station_code = 'CNB';
    SELECT station_id INTO v_bpl  FROM STATIONS WHERE station_code = 'BPL';

    -- Insert Trains
    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12951', 'Mumbai Rajdhani Express', 'Rajdhani', v_mmct, v_ndls, 720, 'ACTIVE') RETURNING train_id INTO v_t1;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12952', 'New Delhi Rajdhani Express', 'Rajdhani', v_ndls, v_mmct, 720, 'ACTIVE') RETURNING train_id INTO v_t2;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12301', 'Howrah Rajdhani Express', 'Rajdhani', v_hwh, v_ndls, 680, 'ACTIVE') RETURNING train_id INTO v_t3;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12621', 'Tamil Nadu Express', 'Superfast', v_mas, v_ndls, 840, 'ACTIVE') RETURNING train_id INTO v_t4;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12004', 'Lucknow Swarna Shatabdi', 'Shatabdi', v_ndls, v_lko, 550, 'ACTIVE') RETURNING train_id INTO v_t5;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('22691', 'Bengaluru Rajdhani Express', 'Rajdhani', v_sbc, v_ndls, 700, 'ACTIVE') RETURNING train_id INTO v_t6;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12953', 'August Kranti Tejas Rajdhani', 'Rajdhani', v_mmct, v_ndls, 720, 'ACTIVE') RETURNING train_id INTO v_t7;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12009', 'Mumbai Ahmedabad Shatabdi', 'Shatabdi', v_mmct, v_adi, 520, 'ACTIVE') RETURNING train_id INTO v_t8;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12723', 'Telangana Express', 'Superfast', v_hyb, v_ndls, 800, 'ACTIVE') RETURNING train_id INTO v_t9;

    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12137', 'Punjab Mail', 'Express', v_mmct, v_ndls, 900, 'ACTIVE') RETURNING train_id INTO v_t10;

    -- New Train 11: Ahmedabad - Lucknow Sarvodaya Express (ADI -> JP -> CNB -> LKO)
    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12961', 'Ahmedabad Lucknow Sarvodaya Exp', 'Superfast', v_adi, v_lko, 760, 'ACTIVE') RETURNING train_id INTO v_t11;

    -- New Train 12: New Delhi - Howrah Duronto Express (NDLS -> CNB -> HWH)
    INSERT INTO TRAINS (train_number, train_name, train_type, source_station_id, dest_station_id, total_capacity, status)
    VALUES ('12273', 'Delhi Howrah Duronto Express', 'Rajdhani', v_ndls, v_hwh, 680, 'ACTIVE') RETURNING train_id INTO v_t12;

    -- 4. INSERT INTERMEDIATE STOPS FOR TRAINS
    -- 12951 Mumbai Rajdhani (MMCT -> BPL -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t1, v_mmct, 1, '17:00', '17:00', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t1, v_bpl, 2, '02:15', '02:25', 820, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t1, v_ndls, 3, '08:35', '08:35', 1384, 1);

    -- 12952 New Delhi Rajdhani (NDLS -> BPL -> MMCT)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t2, v_ndls, 1, '16:55', '16:55', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t2, v_bpl, 2, '23:00', '23:10', 564, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t2, v_mmct, 3, '08:35', '08:35', 1384, 1);

    -- 12953 August Kranti (MMCT -> ADI -> JP -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t7, v_mmct, 1, '17:40', '17:40', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t7, v_adi, 2, '23:35', '23:45', 492, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t7, v_jp, 3, '06:10', '06:20', 982, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t7, v_ndls, 4, '10:55', '10:55', 1288, 1);

    -- 12301 Howrah Rajdhani (HWH -> CNB -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t3, v_hwh, 1, '16:50', '16:50', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t3, v_cnb, 2, '04:40', '04:45', 1005, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t3, v_ndls, 3, '10:05', '10:05', 1445, 1);

    -- 12004 Lucknow Shatabdi (NDLS -> CNB -> LKO)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t5, v_ndls, 1, '06:10', '06:10', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t5, v_cnb, 2, '11:20', '11:25', 440, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t5, v_lko, 3, '12:40', '12:40', 512, 0);

    -- 12621 Tamil Nadu Express (MAS -> HYB -> BPL -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t4, v_mas, 1, '22:00', '22:00', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t4, v_hyb, 2, '08:45', '08:55', 715, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t4, v_bpl, 3, '21:10', '21:20', 1450, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t4, v_ndls, 4, '06:30', '06:30', 2182, 2);

    -- 22691 Bengaluru Rajdhani (SBC -> HYB -> BPL -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t6, v_sbc, 1, '20:00', '20:00', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t6, v_hyb, 2, '06:40', '06:50', 620, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t6, v_bpl, 3, '19:15', '19:25', 1410, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t6, v_ndls, 4, '05:30', '05:30', 2115, 2);

    -- 12009 Mumbai Ahmedabad Shatabdi (MMCT -> PUNE -> ADI)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t8, v_mmct, 1, '06:20', '06:20', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t8, v_pune, 2, '09:20', '09:25', 192, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t8, v_adi, 3, '13:10', '13:10', 492, 0);

    -- 12723 Telangana Express (HYB -> BPL -> CNB -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t9, v_hyb, 1, '06:00', '06:00', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t9, v_bpl, 2, '18:40', '18:50', 850, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t9, v_cnb, 3, '02:30', '02:40', 1320, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t9, v_ndls, 4, '09:05', '09:05', 1675, 1);

    -- 12137 Punjab Mail (MMCT -> PUNE -> BPL -> NDLS)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t10, v_mmct, 1, '19:35', '19:35', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t10, v_pune, 2, '23:05', '23:10', 192, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t10, v_bpl, 3, '11:45', '11:55', 860, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t10, v_ndls, 4, '21:30', '21:30', 1540, 1);

    -- 12961 Ahmedabad Lucknow Sarvodaya Express (ADI -> JP -> CNB -> LKO)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t11, v_adi, 1, '08:00', '08:00', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t11, v_jp, 2, '14:30', '14:40', 670, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t11, v_cnb, 3, '22:15', '22:25', 1110, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t11, v_lko, 4, '23:55', '23:55', 1182, 0);

    -- 12273 Delhi Howrah Duronto Express (NDLS -> CNB -> HWH)
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t12, v_ndls, 1, '22:30', '22:30', 0, 0);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t12, v_cnb, 2, '04:15', '04:20', 440, 1);
    INSERT INTO TRAIN_STOPS (train_id, station_id, stop_sequence, arrival_time, departure_time, distance_from_source_km, day_offset)
    VALUES (v_t12, v_hwh, 3, '17:45', '17:45', 1445, 1);

    -- 5. INSERT SCHEDULES: All 12 trains, 21 days from today (SYSDATE to SYSDATE+20)
    --    This ensures the date filter in the search always finds matching results.
    FOR v_day IN 0..20 LOOP
        -- t1: Mumbai Rajdhani (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t1, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 450.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch1;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch1, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch1, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch1, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch1, 'SL', 370, 0, 370, 1.00);

        -- t2: New Delhi Rajdhani (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t2, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 450.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch2;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch2, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch2, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch2, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch2, 'SL', 370, 0, 370, 1.00);

        -- t3: Howrah Rajdhani (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t3, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 480.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch3;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch3, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch3, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch3, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch3, 'SL', 370, 0, 370, 1.00);

        -- t4: Tamil Nadu Express (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t4, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 2, 520.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch4;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch4, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch4, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch4, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch4, 'SL', 370, 0, 370, 1.00);

        -- t5: Lucknow Shatabdi (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t5, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day, 220.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch5;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch5, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch5, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch5, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch5, 'SL', 370, 0, 370, 1.00);

        -- t6: Bengaluru Rajdhani (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t6, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 2, 550.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch6;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch6, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch6, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch6, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch6, 'SL', 370, 0, 370, 1.00);

        -- t7: August Kranti Rajdhani (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t7, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 460.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch7;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch7, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch7, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch7, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch7, 'SL', 370, 0, 370, 1.00);

        -- t8: Mumbai Ahmedabad Shatabdi (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t8, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day, 250.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch8;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch8, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch8, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch8, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch8, 'SL', 370, 0, 370, 1.00);

        -- t9: Telangana Express (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t9, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 410.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch9;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch9, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch9, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch9, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch9, 'SL', 370, 0, 370, 1.00);

        -- t10: Punjab Mail (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t10, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 380.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch10;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch10, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch10, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch10, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch10, 'SL', 370, 0, 370, 1.00);

        -- t11: Ahmedabad Lucknow Sarvodaya (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t11, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day, 310.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch11;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch11, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch11, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch11, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch11, 'SL', 370, 0, 370, 1.00);

        -- t12: Delhi Howrah Duronto (daily)
        INSERT INTO TRAIN_SCHEDULES (train_id, departure_date, arrival_date, base_fare, status)
        VALUES (v_t12, TRUNC(SYSDATE) + v_day, TRUNC(SYSDATE) + v_day + 1, 490.00, 'SCHEDULED') RETURNING schedule_id INTO v_sch12;
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch12, '1A', 30, 0, 30, 3.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch12, '2A', 80, 0, 80, 2.20);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch12, '3A', 240, 0, 240, 1.55);
        INSERT INTO TRAIN_SEATS (schedule_id, seat_class, total_seats, booked_seats, available_seats, fare_multiplier) VALUES (v_sch12, 'SL', 370, 0, 370, 1.00);
    END LOOP;


    -- 7. INSERT ROUTE CONNECTIONS (For Dijkstra Shortest-Path Algorithm)
    -- Intentionally engineered so Shortest Distance != Fastest Travel Time
    -- Example between NDLS (Delhi) and MMCT (Mumbai):
    -- Path A (Western Corridor via Jaipur): NDLS -> JP (310 km, 300 min) + JP -> ADI (670 km, 620 min) + ADI -> MMCT (492 km, 410 min)
    --   Total Dist = 310 + 670 + 492 = 1472 km | Total Time = 300 + 620 + 410 = 1330 min (22.1 hrs)
    -- Path B (Central High-Speed Corridor via Bhopal): NDLS -> BPL (700 km, 450 min) + BPL -> MMCT (820 km, 540 min)
    --   Total Dist = 700 + 820 = 1520 km | Total Time = 450 + 540 = 990 min (16.5 hrs - 5.6 hours FASTER!)
    -- Between NDLS and JP / CNB / BPL / etc.
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_ndls, v_jp, 310.0, 300.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_jp, v_ndls, 310.0, 300.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_jp, v_adi, 670.0, 620.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_adi, v_jp, 670.0, 620.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_adi, v_mmct, 492.0, 410.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_mmct, v_adi, 492.0, 410.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_ndls, v_bpl, 700.0, 450.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_bpl, v_ndls, 700.0, 450.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_bpl, v_mmct, 820.0, 540.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_mmct, v_bpl, 820.0, 540.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_mmct, v_pune, 192.0, 180.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_pune, v_mmct, 192.0, 180.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_ndls, v_cnb, 440.0, 275.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_cnb, v_ndls, 440.0, 275.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_cnb, v_lko, 72.0, 75.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_lko, v_cnb, 72.0, 75.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_cnb, v_hwh, 1005.0, 680.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_hwh, v_cnb, 1005.0, 680.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_bpl, v_hyb, 850.0, 620.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_hyb, v_bpl, 850.0, 620.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_hyb, v_sbc, 620.0, 540.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_sbc, v_hyb, 620.0, 540.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_hyb, v_mas, 715.0, 640.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_mas, v_hyb, 715.0, 640.0, 1);

    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_sbc, v_mas, 350.0, 310.0, 1);
    INSERT INTO ROUTE_CONNECTIONS (from_station_id, to_station_id, distance_km, travel_time_min, is_active)
    VALUES (v_mas, v_sbc, 350.0, 310.0, 1);

    -- 8. INITIAL SAMPLE RESERVATIONS
    -- Reservation 1: Confirmed booking
    INSERT INTO RESERVATIONS (
        pnr_number, passenger_id, schedule_id, from_station_id, to_station_id,
        journey_date, seat_class, passenger_count, total_fare, booking_status, booking_time
    ) VALUES (
        'PNR26102501', 1, v_sch1, v_mmct, v_ndls, TRUNC(SYSDATE), '2A', 2, 6240.00, 'CONFIRMED', SYSTIMESTAMP - INTERVAL '2' HOUR
    ) RETURNING reservation_id INTO v_res1;

    INSERT INTO RESERVATION_PASSENGERS (reservation_id, passenger_name, age, gender, seat_number)
    VALUES (v_res1, 'Aarav Sharma', 29, 'Male', 'A1-21');
    INSERT INTO RESERVATION_PASSENGERS (reservation_id, passenger_name, age, gender, seat_number)
    VALUES (v_res1, 'Priya Patel', 26, 'Female', 'A1-22');

    INSERT INTO BOOKING_TRANSACTIONS (reservation_id, transaction_ref, amount, payment_method, payment_status, transaction_time)
    VALUES (v_res1, 'TXN-2026102501', 6240.00, 'UPI', 'SUCCESS', SYSTIMESTAMP - INTERVAL '2' HOUR);

    UPDATE TRAIN_SEATS
    SET booked_seats = booked_seats + 2, available_seats = available_seats - 2
    WHERE schedule_id = v_sch1 AND seat_class = '2A';

    -- Reservation 2: Cancelled booking
    INSERT INTO RESERVATIONS (
        pnr_number, passenger_id, schedule_id, from_station_id, to_station_id,
        journey_date, seat_class, passenger_count, total_fare, booking_status, booking_time
    ) VALUES (
        'PNR26102502', 3, v_sch6, v_ndls, v_lko, TRUNC(SYSDATE), '3A', 1, 1280.00, 'CANCELLED', SYSTIMESTAMP - INTERVAL '5' HOUR
    ) RETURNING reservation_id INTO v_res2;

    INSERT INTO RESERVATION_PASSENGERS (reservation_id, passenger_name, age, gender, seat_number)
    VALUES (v_res2, 'Rajesh Kumar', 45, 'Male', 'B2-15');

    INSERT INTO BOOKING_TRANSACTIONS (reservation_id, transaction_ref, amount, payment_method, payment_status, transaction_time)
    VALUES (v_res2, 'TXN-2026102502', 1280.00, 'Credit Card', 'REFUNDED', SYSTIMESTAMP - INTERVAL '5' HOUR);

    INSERT INTO CANCELLATIONS (reservation_id, cancellation_ref, cancellation_time, refund_amount, cancellation_charge, reason)
    VALUES (v_res2, 'CAN-2026102501', SYSTIMESTAMP - INTERVAL '1' HOUR, 1024.00, 256.00, 'Personal urgency');

    COMMIT;
END;
/
