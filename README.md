# Smart Railway Reservation and Route Optimization System

> **A Desktop Application Combining Oracle PL/SQL (Advanced DBMS) and Design & Analysis of Algorithms (DAA)**  
> Built with **Python 3.11**, **Tkinter & ttk**, **Oracle Database (23c / 23ai / 19c)**, and **Matplotlib**.

---

## 📌 Project Highlights

- **PL/SQL Transaction Safety & Concurrency Control:**
  - Stored Procedures: `BOOK_TICKET`, `CANCEL_TICKET`, `REGISTER_PASSENGER`, `ADD_TRAIN`, `ADD_STATION`, `GENERATE_BOOKING_REPORT`, `GET_RESERVATION_DETAILS`.
  - Exclusively prevents overbooking and race conditions via **Row-Level Locking (`SELECT ... FOR UPDATE`)** inside atomic transaction boundaries.
  - User-defined PL/SQL Functions: `CALCULATE_FARE`, `GET_AVAILABLE_SEATS`, `GET_JOURNEY_DURATION`, `GET_RESERVATION_STATUS`.
  - Automated Triggers: `TRG_RESERVATION_AUDIT`, `TRG_CANCELLATION_AUDIT`, `TRG_CHECK_SCHEDULE_DATES`.
  - Comprehensive Relational Schema: 12 normalized tables with identity columns, check constraints, foreign keys, and indexes.

- **Design & Analysis of Algorithms (DAA):**
  - **Dijkstra's Shortest Path Algorithm:** Implemented with binary min-priority queues (`heapq`) with time complexity $O((V+E)\log V)$ to optimize routes across the railway graph.
  - **Multi-Criteria Optimization:** Solves for both *Shortest Distance* (km) and *Fastest Travel Time* (minutes). Demonstrates cases where shortest distance $\ne$ fastest travel time (e.g. New Delhi to Mumbai via Jaipur vs Bhopal).
  - **Binary Search:** Fast in-memory $O(\log n)$ train lookup by train number on sorted train arrays with full step-by-step diagnostic tracing.
  - **Merge Sort & Quick Sort:** Empirically sorts search results and timetable schedules by departure time, fare, or journey duration with stability and complexity benchmarks.
  - **DAA Algorithm Laboratory:** Interactive benchmarking panel measuring live execution times using `time.perf_counter()` and rendering scaling curves via embedded Matplotlib figures.

- **Modern Desktop GUI (Tkinter & ttk):**
  - Modern Railway Enterprise Theme (Railway Navy `#1A2B4C`, Golden Amber `#D97706`, Slate Card elevation).
  - Sidebar navigation with 11 functional modules.
  - Top application status bar with live Oracle DB health indicator.
  - Responsive tables (`ttk.Treeview`) with custom headings and alternating row highlights.

---

## 🛠 Technology Stack

- **Programming Language:** Python 3.11+
- **GUI Framework:** Tkinter & ttk
- **Database:** Oracle Database (23c / 23ai Free / 19c / 21c / XE)
- **Database Programming:** Oracle PL/SQL
- **Python Driver:** `oracledb` 26.0+ (Thin & Thick modes supported)
- **Data Visualization:** Matplotlib 3.11+
- **Environment Management:** `python-dotenv`

---

## 📁 Project Directory Structure

```
Smart Railway Reservation and Route Optimization System/
│
├── main.py                     # Master application entry point & CLI controller
├── config.py                   # Central configuration & theme definitions
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and documentation overview
├── .env.example                # Oracle credentials configuration template
├── .env                        # Active environment credentials
│
├── database/                   # Oracle SQL and PL/SQL Scripts
│   ├── __init__.py
│   ├── schema.sql              # 12 Relational tables & integrity constraints
│   ├── procedures.sql          # Stored procedures (booking, cancellation, etc.)
│   ├── functions.sql           # Functions (fare calculator, seat lookup)
│   ├── triggers.sql            # Audit & schedule date validation triggers
│   ├── sample_data.sql         # 12 Stations, 10 Trains, Stops, Schedules & Connections
│   ├── db_connection.py        # Connection pooling & PL/SQL execution wrappers
│   └── setup_database.py       # Automated database deployment runner
│
├── algorithms/                 # DAA Algorithm Implementations
│   ├── __init__.py
│   ├── dijkstra.py             # Dijkstra shortest path with min-heap
│   ├── binary_search.py        # Iterative binary search & linear search
│   ├── merge_sort.py           # Stable divide-and-conquer merge sort
│   ├── quick_sort.py           # Median-of-three in-place quick sort
│   └── algorithm_analysis.py   # Empirical benchmarking engine
│
├── services/                   # Application Business Logic Layer
│   ├── __init__.py
│   ├── passenger_service.py    # Passenger registration & history
│   ├── train_service.py        # Timetable search, binary lookup & stops
│   ├── reservation_service.py  # PL/SQL booking & atomic cancellation
│   ├── route_service.py        # Graph construction & multi-criteria optimization
│   └── report_service.py       # Aggregated KPIs & revenue yields
│
├── gui/                        # Modern Tkinter Desktop Interface
│   ├── __init__.py
│   ├── theme.py                # Color palette, card containers & TTK styles
│   ├── main_window.py          # Master window with sidebar navigation
│   ├── dashboard_page.py       # Operations dashboard with live summary cards
│   ├── search_page.py          # Train search, DAA sorting & binary lookup
│   ├── route_page.py           # Dijkstra route optimizer & visual pill path
│   ├── booking_page.py         # Transaction-safe ticket reservation form
│   ├── cancellation_page.py    # PNR lookup, refund calculator & cancellation
│   ├── reservations_page.py    # Master booking inquiry & modal inspector
│   ├── train_page.py           # Train fleet manager & stops inspector
│   ├── station_page.py         # Station directory & safe deletion
│   ├── passenger_page.py       # Passenger directory & travel histories
│   ├── reports_page.py         # Revenue reports & embedded Matplotlib charts
│   └── algorithm_page.py       # DAA algorithm benchmark lab & scaling curves
│
├── tests/                      # Automated Test Suite (32 Tests)
│   ├── __init__.py
│   ├── test_dijkstra.py        # Graph tests (alternate paths, unreachable, weights)
│   ├── test_binary_search.py   # Search tests (edges, empty, comparisons)
│   ├── test_sorting.py         # Merge & Quick sort tests (stability, duplicates)
│   ├── test_reservations.py    # PL/SQL workflow tests (concurrency, rollback, refund)
│   └── run_all_tests.py        # Master test suite runner
│
└── docs/
    └── PROJECT_DOCUMENTATION.md # Full College Technical Report & Viva Q&A
```

---

## 🚀 Step-by-Step Setup Instructions

### 1. Prerequisites
Ensure you have installed:
- **Python 3.10+** (Python 3.11 recommended)
- **Oracle Database** (Oracle 23ai / 23c Free, 19c, 21c, or XE)

### 2. Install Required Python Packages
Open terminal / command prompt in the project root:
```bash
pip install -r requirements.txt
```

### 3. Configure Database Credentials
A `.env` file is included configured for local Oracle Database:
```env
DB_USER=railway_admin
DB_PASSWORD=admin123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=FREEPDB1
```
*(If your Oracle installation uses a different service name like `ORCLPDB` or `XE`, simply update `DB_SERVICE` and credentials in `.env`)*

### 4. Initialize Database Schema & Sample Data
Run the automated database deployment script:
```bash
python main.py --setup-db
```
This automatically compiles:
- `schema.sql`: 12 relational tables, constraints, indexes
- `procedures.sql`: All 8 stored procedures
- `functions.sql`: All 4 user-defined functions
- `triggers.sql`: All audit & validation triggers
- `sample_data.sql`: 12 Indian Railway stations, 10 express trains, 35 stops, 48 seat inventories, route track connections, and initial bookings.

### 5. Run the Automated Test Suite
Verify that all 32 unit and integration tests pass:
```bash
python main.py --run-tests
```

### 6. Launch the Desktop Application
Start the graphical desktop application:
```bash
python main.py
```

---

## 📊 Summary of Implemented DAA Algorithms

| Algorithm | Paradigm | Time Complexity | Space Complexity | Role in System |
|---|---|---|---|---|
| **Dijkstra's Algorithm** | Greedy (Min-Heap) | $O((V+E)\log V)$ | $O(V+E)$ | Solves shortest distance (km) and fastest travel time (min) across station graph. |
| **Binary Search** | Divide-and-Conquer | $O(\log n)$ | $O(1)$ | Fast in-memory lookup of trains by train number in sorted train arrays. |
| **Merge Sort** | Divide-and-Conquer | $O(n\log n)$ strictly | $O(n)$ | Stable sorting of train search results by fare, departure time, or journey duration. |
| **Quick Sort** | Divide-and-Conquer | $O(n\log n)$ avg | $O(\log n)$ | Fast in-place sorting using median-of-three pivot selection. |

---

## 📖 College Project Documentation & Viva Voce Q&A
A complete 30-page equivalent technical report including **System Architecture**, **Entity-Relationship Diagram**, **Data Flow Diagrams (Level 0, 1, 2)**, **Flowcharts**, and **20+ Detailed Viva Voce Questions & Answers** is available in:
👉 [docs/PROJECT_DOCUMENTATION.md](file:///e:/Smart%20Railway%20Reservation%20and%20Route%20Optimization%20System/docs/PROJECT_DOCUMENTATION.md)
