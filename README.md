
## Complete Technical Documentation
### For Engineers, Developers, and Non-Technical Stakeholders

---

**Author:** XXXXXXXXX  
**Student ID:** XXXXXXXX  
**Institution:** XXXXXXXXXXXXXXXXXX  
**Date:** November 2025  
**Version:** 2.0 - Complete Reference Guide

---

## Document Purpose

This documentation explains every aspect of the B777-300ER Visual Loading System in plain language. Whether you're a software developer wanting to understand the code, an aviation engineer interested in the calculations, or a project manager who needs to understand what the system does, this guide is for you.

**What You'll Learn:**
- Why this system exists and what problem it solves
- How aircraft weight and balance works (explained simply)
- How the program is organized and why
- What each piece of code does and why it's written that way
- How to use, modify, or expand the system

---

## Table of Contents

1. [Executive Summary - The Big Picture](#1-executive-summary)
2. [Understanding Aircraft Weight & Balance](#2-understanding-weight-balance)
3. [The Problem This System Solves](#3-the-problem)
4. [System Architecture Overview](#4-system-architecture)
5. [Configuration System (config.py)](#5-configuration-system)
6. [Calculation Engine (calculations.py)](#6-calculation-engine)
7. [Utility Functions (app_utils.py)](#7-utility-functions)
8. [Passenger Loading Module](#8-passenger-loading-module)
9. [Cargo Loading Module](#9-cargo-loading-module)
10. [Fuel Loading Module](#10-fuel-loading-module)
11. [Live Visualization System](#11-live-visualization-system)
12. [Main Application Integration](#12-main-application)
13. [Data Files - The Aircraft Database](#13-data-files)
14. [How Everything Works Together](#14-integration-flow)
15. [Installation & Setup Guide](#15-installation-setup)
16. [User Guide - How to Use the System](#16-user-guide)
17. [Developer Guide - How to Modify](#17-developer-guide)
18. [Testing & Validation](#18-testing-validation)
19. [Troubleshooting Common Issues](#19-troubleshooting)
20. [Future Enhancements](#20-future-enhancements)

---

## 1. Executive Summary - The Big Picture {#1-executive-summary}

### What Is This System?

Imagine you're planning to load a Boeing 777-300ER aircraft. You need to put 425 passengers, their luggage, cargo, and fuel on board. But you can't just throw everything in randomly—the airplane has to be **balanced**.

**Why Balance Matters:**
- If the plane is too nose-heavy, it won't rotate on takeoff (crash)
- If it's too tail-heavy, it becomes unstable in flight (crash)
- If it's overweight, it can't take off safely (crash or runway overrun)

**The Old Way:**
Load planners would:
1. Look up weights in tables
2. Calculate moments with a calculator
3. Plot points on a paper chart
4. Check if everything is within limits

This takes time and is prone to human error.

**The New Way (This System):**
1. Click seats to select passengers
2. Click cargo positions to load freight
3. Enter fuel amounts
4. **Instantly see** if the load is safe with a visual graph

The system does all the math automatically and shows you a live plot of where the airplane's center of gravity is. If something's wrong, you see it immediately.

---

### Key Features

**What Makes This System Special:**

1. **Visual & Interactive**
   - You see a seat map, not a spreadsheet
   - Click seats to add passengers
   - Watch the CG move in real-time on a graph

2. **Modular Design**
   - Passengers, cargo, and fuel are separate modules
   - Easy to add new aircraft types
   - Each module can be tested independently

3. **Accurate & Validated**
   - Uses official Boeing data
   - Follows EASA regulations
   - Calculations match industry standards

4. **Real-Time Feedback**
   - No "calculate" button needed
   - Every change updates the graph instantly
   - Warnings appear automatically if limits are exceeded

5. **Future-Proof**
   - All aircraft data in JSON files (easy to edit)
   - Python code is well-documented
   - Can be expanded with new features

---

### Who Should Use This Documentation?

**Aviation Engineers:**
- Sections 2, 6, 13 explain the physics and data sources
- Validation information in Section 18

**Software Developers:**
- Sections 4-12 explain code architecture
- Section 17 has modification guidelines
- All functions are documented with examples

**Project Managers / Stakeholders:**
- Section 1 (this section) explains what it does
- Section 3 explains the business case
- Section 20 discusses future potential

**Students / Learners:**
- Section 2 teaches W&B fundamentals
- Every code section has "Why?" explanations
- Real-world examples throughout

---

### Technology Overview

**What's Under the Hood:**

```
Programming Language:    Python 3.x
User Interface:          tkinter (built into Python)
Graphing:               matplotlib
Data Storage:           JSON files
Mathematics:            Standard Python + NumPy
```

**Why These Choices?**

- **Python**: Easy to read, widely used in engineering
- **tkinter**: Works on Windows, Mac, Linux without installation
- **matplotlib**: Industry-standard for scientific plotting
- **JSON**: Human-readable, easy to edit and validate

---

## 2. Understanding Aircraft Weight & Balance {#2-understanding-weight-balance}

Before we dive into the code, you need to understand the physics. This section explains weight and balance as simply as possible.

---

### The Seesaw Analogy

Think of an airplane as a giant seesaw (teeter-totter). 

```
        [Light Kid]              [Heavy Adult]
             |                        |
    ----============================----
                    ⬆ (Pivot Point)
```

- If the heavy adult sits close to the pivot, it balances
- If the heavy adult sits far from the pivot, their side goes down
- The distance from the pivot matters as much as the weight

**In an airplane:**
- The **pivot point** = Center of Gravity (CG)
- The **weight** = passengers, cargo, fuel, etc.
- The **distance** = how far fore or aft they are loaded

---

### The Three Key Concepts

#### 1. Weight
Simply: how heavy is each item in kilograms.

```
Example:
- 1 passenger = 88.5 kg (EASA standard with hand luggage)
- 1 cargo container = up to 1,587 kg
- Fuel = varies (0.75 to 0.85 kg per liter)
```

---

#### 2. Arm
The distance from the airplane's reference point (the nose) to where the item is located, measured in inches.

```
Example B777-300ER:
          [Nose]  ---1000 in---  [Wing]  ---500 in---  [Tail]
             0"                  1174.5"              2000"
                                   ↑
                            (LEMAC - reference)
```

- Passenger in Row 1: arm ≈ 600 inches
- Passenger in Row 40: arm ≈ 1,500 inches
- Fuel in center tank: arm ≈ 1,350 inches (but changes as it fills!)

**Why inches?** Boeing uses imperial units. We convert to %MAC for display.

---

#### 3. Moment
The "rotating force" an item creates. 

**Formula:**
```
Moment = Weight × Arm
```

**Example:**
```
100 kg passenger sitting at arm 1,200 inches
Moment = 100 kg × 1,200 in = 120,000 kg-in
```

**Why it matters:**
- A heavy item near the CG has less moment (less rotation)
- A light item far from the CG has more moment (more rotation)

---

### Calculating the Center of Gravity

The Center of Gravity (CG) is where all the moments balance out to zero.

**Formula:**
```
CG (in inches) = (Sum of all Moments) / (Sum of all Weights)
```

**Real Example:**

| Item | Weight (kg) | Arm (in) | Moment (kg-in) |
|------|------------|----------|----------------|
| Empty Aircraft | 170,000 | 1,252 | 212,840,000 |
| 100 Passengers | 8,850 | 1,100 | 9,735,000 |
| Cargo | 10,000 | 1,450 | 14,500,000 |
| Fuel | 80,000 | 1,280 | 102,400,000 |
| **TOTAL** | **268,850** | - | **339,475,000** |

```
CG = 339,475,000 / 268,850 = 1,262.6 inches
```

---

### Converting to %MAC (Percent Mean Aerodynamic Chord)

Airlines don't use inches—they use **%MAC** because it's standardized.

**What is MAC?**
- MAC = Mean Aerodynamic Chord (average wing width)
- For B777-300ER: MAC = 278.5 inches
- LEMAC (leading edge) = 1,174.5 inches from the nose

**Conversion Formula:**
```
%MAC = ((CG in inches - 1,174.5) / 278.5) × 100
```

**Example:**
```
CG = 1,262.6 inches

%MAC = ((1,262.6 - 1,174.5) / 278.5) × 100
     = (88.1 / 278.5) × 100
     = 31.6% MAC
```

**What does 31.6% MAC mean?**
- The CG is 31.6% of the way along the wing chord
- Typical safe range: 7% to 35% MAC
- Forward CG (7-15%): stable, uses more fuel
- Aft CG (25-35%): efficient, less stable

---

### The CG Envelope - The Safe Zone

The "CG Envelope" is a graph showing the safe operating limits.

```
Weight (kg)
  ↑
350,000 |         _______________
        |        /               \
300,000 |       /  SAFE ZONE     \
        |      /    (Certified    \
250,000 |     /      Envelope)     \
        |    /                      \
200,000 |   /________________________\
        |
150,000 +--------------------------------→ CG (%MAC)
            10%   20%   30%   40%
```

**Key Points:**
- If your calculated point is **inside** the envelope: ✅ Safe to fly
- If your calculated point is **outside** the envelope: ❌ Cannot fly

**Our system plots the aircraft's CG at different weights:**
1. DOW (Dry Operating Weight - empty plane)
2. DOW + Passengers
3. ZFW (Zero Fuel Weight - all loaded except fuel)
4. TOW (Takeoff Weight - fully loaded with fuel)

---

### The Loading Sequence

Aircraft MUST be loaded in a specific order:

```
Step 1: Start with DOW (Empty Aircraft)
   ↓
Step 2: Add Passengers
   ↓
Step 3: Add Cargo → This gives you ZFW
   ↓
Step 4: Add Fuel → This gives you TOW
```

**Why this order?**
- You check ZFW first (structural limit without fuel)
- Then you check TOW (max weight for takeoff)
- Fuel is added last because it shifts the CG

**Critical Checks:**
- ✅ ZFW must be ≤ MZFW (Max Zero Fuel Weight = 237,682 kg)
- ✅ TOW must be ≤ MTOW (Max Takeoff Weight = 351,534 kg)
- ✅ Both ZFW and TOW CG must be within the envelope

---

## 3. The Problem This System Solves {#3-the-problem}

### The Traditional Load Planning Process

**How it used to work (and still works at many airlines):**

1. **Dispatcher receives booking data**
   - 380 passengers booked
   - 15 tons of cargo manifested

2. **Manual lookup in tables**
   - Find passenger seating distribution
   - Look up cargo bay arm values
   - Check fuel density for temperature

3. **Calculator time**
   - Multiply each weight by its arm
   - Sum all moments
   - Divide by total weight
   - Convert to %MAC

4. **Plot on paper chart**
   - Find the point on the CG envelope graph
   - Check if it's inside the lines
   - Do this for ZFW and TOW

5. **Double-check everything**
   - One mistake = safety hazard
   - Process takes 15-30 minutes
   - Prone to data entry errors

---

### The Problems with Manual Calculation

**1. Time-Consuming**
- Average load plan: 20 minutes
- Tight turnaround: need faster planning

**2. Error-Prone**
- Typo in one number = wrong result
- Misreading a chart = safety risk
- No immediate validation

**3. Not Visual**
- Hard to "see" if load is balanced
- Can't easily experiment with changes
- Final check requires plotting

**4. Inflexible**
- New aircraft config = new tables
- Can't easily optimize loads
- Hard to train new staff

---

### What This System Does Differently

**The Solution:**

```
Traditional Way:              New Way (This System):
--------------               ---------------------
1. Receive data              1. Open program
2. Look up tables            2. Click seat map
3. Calculate moments         3. Click cargo bays
4. Sum everything            4. Enter fuel
5. Check envelope            5. See instant result
   ↓                            ↓
20 minutes                   2 minutes
Error-prone                  Automated
No visualization             Live graph
```

---

### Business Value

**For Airlines:**
- ⏱️ **Faster turnaround**: 10x faster load planning
- ✅ **Fewer errors**: Automated calculations eliminate math mistakes
- 💰 **Better optimization**: Can quickly test different load scenarios
- 📊 **Training**: New dispatchers learn faster with visual tools

**For Safety:**
- 🚨 **Instant validation**: Violations flagged immediately
- 📈 **Traceability**: Every load is documented
- 🔍 **Transparency**: Engineers can see the full loading sequence

**For Engineering:**
- 🔧 **Flexibility**: Easy to add new aircraft types
- 🧪 **Testing**: Can validate new loading procedures
- 📚 **Documentation**: System self-documents with data files

---

## 4. System Architecture Overview {#4-system-architecture}

### The Big Picture - How It All Fits Together

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE (tkinter)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Passenger   │  │    Cargo     │  │     Fuel     │          │
│  │  Seat Map    │  │   Bay Map    │  │   Tanks      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┴──────────────────┘                   │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│                    MAIN APPLICATION (main_app.py)                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  • Coordinates all modules                                  │ │
│  │  • Collects weights/moments from each module                │ │
│  │  • Performs sequential calculation (DOW→+Pax→ZFW→TOW)      │ │
│  │  • Updates live plot                                        │ │
│  │  • Checks limits                                            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│              CALCULATION ENGINE (calculations.py)                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Functions:                                                  │ │
│  │  • interpolate_arm() - Find fuel tank CG                   │ │
│  │  • calculate_mac_percent() - Convert inches to %MAC        │ │
│  │  • klm_index_base() - Calculate DOW index                  │ │
│  │  • klm_index_component() - Calculate load deltas           │ │
│  │  • check_limits() - Validate against MZFW/MTOW            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│           VISUALIZATION (live_cg_plot.py + app_utils.py)         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  • Draw CG envelope                                         │ │
│  │  • Plot loading sequence (DOW→Pax→ZFW→TOW)                │ │
│  │  • Update in real-time                                      │ │
│  │  • Show certified/restricted areas                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                            ↑
┌───────────────────────────────────────────────────────────────────┐
│                    DATA LAYER (JSON Files)                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  seat_map.json      - Every seat's arm position            │ │
│  │  cargo_positions.json - Cargo bay arms and limits          │ │
│  │  fuel_tanks.json    - Tank capacities and arm tables       │ │
│  │  aircraft_reference.json - DOW, DOI, registration          │ │
│  │  limits.json        - MZFW, MTOW, envelope coordinates     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

---

### Design Philosophy - Why It's Built This Way

#### Principle 1: Separation of Concerns

**What it means:** Each module does ONE job and does it well.

**Example:**
- `passengers_module.py` ONLY handles seat selection
- It doesn't know about cargo or fuel
- It doesn't know how to draw graphs
- It just returns: "These seats are selected, here's the total weight and moment"

**Why this matters:**
- If you need to fix passenger loading, you only touch one file
- You can test the passenger module without running the whole app
- You can reuse the passenger module in a different project

---

#### Principle 2: Data-Driven Design

**What it means:** All aircraft-specific information lives in JSON files, NOT in the code.

**Bad way (hardcoded):**
```python
# DON'T DO THIS
seat_1A_arm = 570.0
seat_1C_arm = 570.0
# ... 400 more seats
```

**Good way (data-driven):**
```python
# Load from file
seat_data = load_json("seat_map.json")
# File contains all seats with their arms
```

**Why this matters:**
- To add a new aircraft, just create new JSON files
- No code changes needed
- Non-programmers can edit the data
- Easy to validate against Boeing manuals

---

#### Principle 3: Callback Architecture

**What it means:** Modules don't talk to each other directly. They notify the main app when something changes.

**How it works:**
```python
# When user clicks a seat:
SeatModule: "Hey Main App, something changed!"
Main App: "Thanks! Let me recalculate everything and update the graph"
```

**Why this matters:**
- Modules stay independent
- Main app controls the coordination
- Easy to add new modules later

---

#### Principle 4: Real-Time Feedback

**What it means:** No "Calculate" button. Everything updates instantly.

**Traditional approach:**
1. User makes changes
2. User clicks "Calculate"
3. User waits
4. Result appears

**Our approach:**
1. User makes change → Graph updates (0.15 seconds later)

**Why this matters:**
- Feels responsive and modern
- User sees impact of every decision
- Encourages experimentation

---

### File Structure Explained

```
project_root/
│
├── main_app.py                 ← START HERE (the orchestrator)
│
├── src/                        ← Core logic (aircraft-agnostic)
│   ├── config.py              ← All constants (one place to change them)
│   ├── calculations.py        ← Pure math (no UI)
│   ├── app_utils.py           ← Shared utilities
│   └── live_cg_plot.py        ← Live matplotlib window
│
├── modules/                    ← UI components (user interaction)
│   ├── passengers_module.py   ← Seat selection interface
│   ├── cargo_module.py        ← Cargo loading interface
│   └── fuel_load_module.py    ← Fuel tank interface
│
└── data/                       ← Aircraft database (edit these)
    ├── seat_map_new.json
    ├── cargo_positions.json
    ├── fuel_tanks.json
    ├── aircraft_reference.json
    └── limits.json
```

**How to navigate:**
- **Want to understand calculations?** → `src/calculations.py`
- **Want to modify the UI?** → `modules/`
- **Want to add a new aircraft?** → `data/`
- **Want to see how it all connects?** → `main_app.py`

---

## 5. Configuration System (config.py) {#5-configuration-system}

### Purpose: The Single Source of Truth

This file contains EVERY magic number, constant, and file path in the entire system. 

**Why?**
- Change a value once, it updates everywhere
- Easy to audit against Boeing manuals
- No hunting through code for hardcoded values

---

### File Paths Section

```python
# --- File Paths ---
SEAT_MAP_FILEPATH = "data/seat_map_new.json"
FUEL_TANKS_FILEPATH = "data/fuel_tanks.json"
CARGO_POSITIONS_FILEPATH = "data/cargo_positions.json"
AIRCRAFT_REFERENCE_FILEPATH = "data/aircraft_reference.json"
LIMITS_FILEPATH = "data/limits.json"
```

**What this does:**
- Defines where all data files are located
- If you move files, change paths here only

**Example use in code:**
```python
# Instead of writing the path 10 times:
seat_data = load_json(config.SEAT_MAP_FILEPATH)
```

---

### Passenger Configuration

```python
# --- Passenger Constants ---
BUSINESS_SEATPLAN = ["A", "C", None, "D", "F", None, "G", "J"]
ECONOMY_SEATPLAN = ["A", "B", None, "D", "E", "F", "G", "H", None, "J", "K"]
DEFAULT_PASSENGER_WEIGHT_KG = 88.5
```

**What these mean:**

**BUSINESS_SEATPLAN:**
```
Row Layout:
[A] [C] [aisle] [D] [F] [aisle] [G] [J]
 ↑   ↑   ↑       ↑   ↑    ↑       ↑   ↑
Seat Seat Gap   Seat Seat Gap   Seat Seat
```
- `None` = aisle gap (no seat there)
- Used to draw the seat map correctly

**DEFAULT_PASSENGER_WEIGHT_KG = 88.5:**
- EASA standard: 84 kg passenger + 3 kg hand luggage + 1.5 kg personal item
- Can be changed in the Config tab at runtime

---

### Fuel Configuration

```python
# --- Fuel Constants ---
MAX_TOTAL_FUEL_KG = 33171 * 2 + 87887  # = 154,229 kg
DEFAULT_FUEL_DENSITY_KG_L = 0.8507
```

**MAX_TOTAL_FUEL_KG:**
```
Calculation breakdown:
Main Tank 1:   33,171 kg
Main Tank 2:   33,171 kg
Center Tank:   87,887 kg
--------------------------
TOTAL:        154,229 kg
```

**DEFAULT_FUEL_DENSITY_KG_L = 0.8507:**
- Jet-A1 fuel at 15°C
- Range: 0.7309 (hot/light) to 0.8507 kg/L (cold/heavy)
- System warns if you exceed capacity

---

### Aircraft Geometry Constants

```python
# --- Aircraft Physics & Index Constants ---
LE_MAC_IN = 1174.5
MAC_LENGTH_IN = 278.5
KLM_REFERENCE_ARM_IN = 1258
KLM_SCALE = 200000
KLM_OFFSET = 50
```

**LE_MAC_IN = 1174.5:**
- Leading Edge of Mean Aerodynamic Chord
- The "zero point" for %MAC calculations
- From Boeing WBCLM Section 1-02

**MAC_LENGTH_IN = 278.5:**
- Length of the Mean Aerodynamic Chord
- Used to convert inches to %MAC
- Formula: %MAC = ((arm - 1174.5) / 278.5) × 100

**KLM Index System (KLM_REFERENCE_ARM_IN, KLM_SCALE, KLM_OFFSET):**
- Alternative way to represent moments
- Used by KLM Royal Dutch Airlines (and others)
- Formula: Index = (weight × (arm - 1258)) / 200000 + 50
- Makes quick mental math easier for dispatchers

---

### CG Envelope Data

```python
# --- CG Envelope Plotting Constants ---
CG_ENVELOPE_LOWER_POINTS = [
    (138573, 7.5), (204116, 7.5),
    (237682, 10.5), (251290, 11.5),
    (325996, 15.4), (345455, 17.8),
    (352441, 22.0), (352441, 27.4)
]
```

**What this is:**
- Each tuple = (weight in kg, CG in %MAC)
- These are the "inflection points" from Boeing's certified envelope
- They define the lower boundary of safe CG positions

**Example breakdown:**
```
At 138,573 kg: CG must be ≥ 7.5% MAC  (forward limit)
At 237,682 kg: CG must be ≥ 10.5% MAC
At 352,441 kg: CG must be ≥ 27.4% MAC (aft limit at max weight)
```

**Source:** Boeing B777-300ER WBCLM, Chapter 1, Section 1-02

**UPPER_POINTS:**
- Same format, defines upper boundary
- Together they create the "envelope" shape

**RESTRICTED_AREA_POINTS:**
- Area where operations are allowed but not recommended
- Typically aft CG at high weights
- Shown darker on the graph

---

### How Config is Used Throughout the System

**Example 1: In calculations.py**
```python
def calculate_mac_percent(arm_in, 
                         le_mac_in=config.LE_MAC_IN,
                         mac_length_in=config.MAC_LENGTH_IN):
    return ((arm_in - le_mac_in) * 100 / mac_length_in)
```
- Function defaults to config values
- Can be overridden if needed (for testing)

**Example 2: In main_app.py**
```python
seat_map_data = load_json(config.SEAT_MAP_FILEPATH)
```
- No hardcoded path
- Easy to change file location

**Example 3: In passengers_module.py**
```python
seat_plan = (config.BUSINESS_SEATPLAN if row_class == "F" 
             else config.ECONOMY_SEATPLAN)
```
- UI layout comes from config
- Change config → UI updates automatically

---

## 6. Calculation Engine (calculations.py) {#6-calculation-engine}

### Purpose: Pure Mathematics, No UI

This file contains all the weight and balance calculations. It has NO user interface code, NO file loading, NO graphics. Just math.

**Why separate it?**
- Easy to test (no need to open windows)
- Easy to validate (compare to hand calculations)
- Can be reused in other projects

---

### Function 1: interpolate_arm()

**What it does:** Finds the fuel tank's center of gravity based on how full it is.

**Why it's needed:**
Fuel tanks aren't rectangular. As fuel fills up, the CG moves because the tank shape is complex.

```
Empty Tank (0L):        Half Full (50,000L):    Full (100,000L):
    ___                      ___                      ___
   /   \                    /   \                    /###\
  /     \                  /#####\                  /#####\
 /_______\                /#######\                /#######\
                          
CG at 1200"              CG at 1220"              CG at 1250"
```

The WBCLM provides a table of (liters, arm) pairs. We interpolate between them.

**Function signature:**
```python
def interpolate_arm(arm_table, fill_l):
    """
    Linearly interpolates arm from a lookup table.
    
    Args:
        arm_table: List of [liters, arm] pairs, sorted by liters
                   Example: [[0, 1200], [50000, 1220], [100000, 1250]]
        fill_l: Current fill level in liters
    
    Returns:
        float: The interpolated arm in inches
    """
```

**Example:**
```python
# Center tank arm table from Boeing manual
center_tank_table = [
    [0, 1342.1],
    [10000, 1345.2],
    [20000, 1348.8],
    [30000, 1352.1],
    # ... more points
]

# User loads 15,000 liters
arm = interpolate_arm(center_tank_table, 15000)

# Result: 1347.0 inches (interpolated between 10k and 20k)
```

**How it works (step by step):**

```python
def interpolate_arm(arm_table, fill_l):
    # Step 1: Handle edge case - below minimum
    if fill_l <= arm_table[0][0]:
        return arm_table[0][1]  # Return first arm
    
    # Step 2: Handle edge case - above maximum
    if fill_l >= arm_table[-1][0]:
        return arm_table[-1][1]  # Return last arm
    
    # Step 3: Find the two points to interpolate between
    for i in range(1, len(arm_table)):
        if fill_l < arm_table[i][0]:
            # Found it! fill_l is between point i-1 and point i
            l1, a1 = arm_table[i - 1]  # Lower point
            l2, a2 = arm_table[i]      # Upper point
            
            # Step 4: Linear interpolation
            # How far between the two points? (0.0 to 1.0)
            percentage = (fill_l - l1) / (l2 - l1)
            
            # Interpolate the arm
            return a1 + (a2 - a1) * percentage
    
    # Fallback (shouldn't reach here)
    return arm_table[-1][1]
```

**Worked Example:**
```
Tank table: [[10000, 1220], [20000, 1250]]
User input: 15000 liters

Step 1: 15000 > 10000 (not below minimum)
Step 2: 15000 < 20000 (not above maximum)
Step 3: Found bounding points:
        Lower: (10000, 1220)
        Upper: (20000, 1250)
Step 4: Calculate percentage:
        (15000 - 10000) / (20000 - 10000) = 5000/10000 = 0.5
        
        Interpolate arm:
        1220 + 0.5 × (1250 - 1220) = 1220 + 15 = 1235 inches
```

**Why linear interpolation?**
- Simple and fast
- Accurate enough for our purposes
- Boeing's tables are dense enough (points every 5,000-10,000 liters)

---

### Function 2: klm_index_base()

**What it does:** Calculates the KLM-style index for the base aircraft (DOW).

**What is the KLM Index?**
The KLM Index is an alternative way to represent the aircraft's moment. Instead of dealing with huge numbers like "339,475,000 kg-in", you get a simpler number like "45.3".

**Formula:**
```
Index = (Weight × (Arm - Reference_Arm)) / Scale + Offset

Where:
- Reference_Arm = 1258 inches (chosen reference point)
- Scale = 200,000 (makes numbers manageable)
- Offset = 50 (shifts range to positive numbers)
```

**Function signature:**
```python
def klm_index_base(weight_kg, arm_in, 
                   reference_arm_in=1258,
                   scale=200000, 
                   offset=50):
    """
    Calculates KLM index for the BASE aircraft (DOW).
    Includes the +50 offset.
    
    Args:
        weight_kg: Weight in kilograms
        arm_in: Arm position in inches
        reference_arm_in: Reference point (default 1258)
        scale: Scaling factor (default 200000)
        offset: Offset value (default 50)
    
    Returns:
        float: The index value
    """
    if weight_kg == 0:
        return 0
    return (weight_kg * (arm_in - reference_arm_in)) / scale + offset
```

**Example:**
```python
# Aircraft PH-BVA empty
DOW = 170,200 kg
DOW_arm = 1,252.48 inches

index = klm_index_base(170200, 1252.48, 1258, 200000, 50)

# Calculation:
# = (170200 × (1252.48 - 1258)) / 200000 + 50
# = (170200 × -5.52) / 200000 + 50
# = -939,504 / 200000 + 50
# = -4.7 + 50
# = 45.3

Result: 45.3 (matches Boeing's certified DOI!)
```

**Why it's useful:**
- Easier to work with (45.3 vs 212,840,000)
- Can be added/subtracted like moments
- Industry standard at many airlines

---

### Function 3: klm_index_component()

**What it does:** Calculates the KLM index for a COMPONENT (passengers, cargo, fuel).

**⚠️ CRITICAL DIFFERENCE from klm_index_base():**
This function does NOT include the +50 offset. Here's why:

**The Math:**
```
Total Index = DOW Index + Passenger Δ + Cargo Δ + Fuel Δ

If we added +50 to each:
Wrong: 45.3 + (4.6+50) + (7.1+50) + (21.3+50) = 228.3 ❌

Correct: 45.3 + 4.6 + 7.1 + 21.3 = 78.3 ✅
```

**Only the DOW gets the +50 offset. Components are deltas (changes).**

**Function signature:**
```python
def klm_index_component(weight_kg, arm_in,
                        reference_arm_in=1258,
                        scale=200000):
    """
    Calculates KLM index for a COMPONENT (pax, cargo, fuel).
    Does NOT include the +50 offset (it's a delta).
    
    Args:
        weight_kg: Component weight in kilograms
        arm_in: Component CG in inches
        reference_arm_in: Reference point (default 1258)
        scale: Scaling factor (default 200000)
    
    Returns:
        float: The index delta (change)
    """
    if weight_kg == 0:
        return 0
    return (weight_kg * (arm_in - reference_arm_in)) / scale
    # Note: NO + offset here!
```

**Example:**
```python
# 100 passengers loaded
pax_weight = 8,850 kg
pax_cg = 1,100 inches

delta = klm_index_component(8850, 1100, 1258, 200000)

# Calculation:
# = (8850 × (1100 - 1258)) / 200000
# = (8850 × -158) / 200000
# = -1,398,300 / 200000
# = -6.99

Result: -6.99 (negative because passengers are forward of reference)
```

**How to use both functions together:**
```python
# Calculate indices
dow_index = klm_index_base(dow_weight, dow_arm)       # = 45.3
pax_index = klm_index_component(pax_weight, pax_cg)   # = -6.99
cargo_index = klm_index_component(cargo_weight, cargo_cg)  # = 7.1
fuel_index = klm_index_component(fuel_weight, fuel_cg)     # = 21.3

# Total indices
zfw_index = dow_index + pax_index + cargo_index  # = 45.41
tow_index = zfw_index + fuel_index               # = 66.71
```

---

### Function 4: calculate_arm_from_doi()

**What it does:** Reverse-calculates the arm from a known index.

**Why it's needed:**
Boeing certifies each aircraft with a DOW and DOI (Dry Operating Index). But to plot the starting point on our graph, we need the DOW **arm** (in inches).

This function solves the index formula backwards.

**The algebra:**
```
Given:  Index = (Weight × (Arm - Ref)) / Scale + Offset
Solve for Arm:

Step 1: Index - Offset = (Weight × (Arm - Ref)) / Scale
Step 2: (Index - Offset) × Scale = Weight × (Arm - Ref)
Step 3: ((Index - Offset) × Scale) / Weight = Arm - Ref
Step 4: Arm = ((Index - Offset) × Scale / Weight) + Ref
```

**Function signature:**
```python
def calculate_arm_from_doi(doi, weight_kg,
                           reference_arm_in=1258,
                           scale=200000,
                           offset=50):
    """
    Reverse-calculates arm from DOI (Dry Operating Index).
    
    Args:
        doi: The Dry Operating Index
        weight_kg: The Dry Operating Weight
        reference_arm_in: Reference point (default 1258)
        scale: Scaling factor (default 200000)
        offset: Offset value (default 50)
    
    Returns:
        float: The calculated arm in inches
    """
    if weight_kg == 0:
        return 0
    return ((doi - offset) * scale / weight_kg) + reference_arm_in
```

**Example:**
```python
# Aircraft PH-BVA from Boeing certificate
DOW = 170,200 kg
DOI = 45.3

arm = calculate_arm_from_doi(45.3, 170200, 1258, 200000, 50)

# Calculation:
# = ((45.3 - 50) × 200000 / 170200) + 1258
# = (-4.7 × 200000 / 170200) + 1258
# = (-940000 / 170200) + 1258
# = -5.52 + 1258
# = 1252.48 inches

Result: 1252.48 inches
```

**Verification:**
```python
# Check: Calculate index from this arm
check = klm_index_base(170200, 1252.48)
# Result: 45.3 ✅ (matches the original DOI!)
```

---

### Function 5: calculate_mac_percent()

**What it does:** Converts an arm position (inches) to %MAC for display.

**Why it's needed:**
- All internal calculations use inches (Boeing uses imperial)
- All displays show %MAC (industry standard)
- The CG envelope is graphed in %MAC

**Formula from Boeing manual:**
```
%MAC = ((Arm - LEMAC) / MAC_length) × 100

Where:
- Arm = CG position in inches
- LEMAC = 1174.5 inches (Leading Edge of MAC)
- MAC_length = 278.5 inches
```

**Function signature:**
```python
def calculate_mac_percent(arm_in,
                          le_mac_in=1174.5,
                          mac_length_in=278.5):
    """
    Converts arm (inches) to %MAC.
    
    Args:
        arm_in: Arm position in inches
        le_mac_in: Leading edge of MAC (default 1174.5)
        mac_length_in: MAC length (default 278.5)
    
    Returns:
        float: CG position in %MAC
    """
    if mac_length_in == 0:
        return 0  # Avoid division by zero
    return ((arm_in - le_mac_in) * 100 / mac_length_in)
```

**Example:**
```python
# ZFW calculation result
zfw_arm = 1242.28 inches

mac = calculate_mac_percent(1242.28, 1174.5, 278.5)

# Calculation:
# = ((1242.28 - 1174.5) × 100) / 278.5
# = (67.78 × 100) / 278.5
# = 6778 / 278.5
# = 24.34% MAC

Result: 24.34% MAC
```

**Interpretation:**
```
24.34% MAC means:
- CG is 24.34% of the way along the wing chord
- This is mid-range (safe zone is typically 7-35%)
- Slightly forward of neutral (good for stability)
```

**Reverse calculation (if needed):**
```python
# If you have %MAC and need inches:
def mac_to_arm(mac_percent, le_mac_in=1174.5, mac_length_in=278.5):
    return (mac_percent * mac_length_in / 100) + le_mac_in

# Example:
arm = mac_to_arm(24.34)  # Returns 1242.28 inches
```

---

### Function 6: check_limits()

**What it does:** Validates calculated weights against certified limits.

**What limits are checked:**
1. **MZFW** (Maximum Zero Fuel Weight) - Structural limit
2. **MTOW** (Maximum Takeoff Weight) - Performance limit
3. **MTW** (Maximum Taxi Weight) - Ground operations limit
4. **MFW** (Minimum Flight Weight) - Usually empty weight

**Why it matters:**
- Exceeding MZFW can damage the wing structure
- Exceeding MTOW means you can't take off safely
- System must catch these violations automatically

**Function signature:**
```python
def check_limits(zfw_weight, tow_weight, limits):
    """
    Checks weights against certified limits.
    
    Args:
        zfw_weight: Calculated Zero Fuel Weight (kg)
        tow_weight: Calculated Takeoff Weight (kg)
        limits: Dictionary with limit values:
                {"MZFW_kg": 237682,
                 "MTOW_kg": 351534,
                 "MTW_kg": 352441,
                 "MFW_kg": 167829}
    
    Returns:
        list: List of warning strings (empty if all OK)
    """
```

**How it works:**
```python
def check_limits(zfw_weight, tow_weight, limits):
    messages = []
    
    # Check 1: Zero Fuel Weight
    if zfw_weight > limits["MZFW_kg"]:
        over = zfw_weight - limits["MZFW_kg"]
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) "
            f"exceeds Maximum ZFW ({limits['MZFW_kg']} kg) "
            f"by {over:.1f} kg.")
    
    # Check 2: Takeoff Weight
    if tow_weight > limits["MTOW_kg"]:
        over = tow_weight - limits["MTOW_kg"]
        messages.append(
            f"Takeoff Weight ({tow_weight:.1f} kg) "
            f"exceeds Maximum TOW ({limits['MTOW_kg']} kg) "
            f"by {over:.1f} kg.")
    
    # Check 3: Taxi Weight
    if tow_weight > limits["MTW_kg"]:
        over = tow_weight - limits["MTW_kg"]
        messages.append(
            f"Takeoff Weight ({tow_weight:.1f} kg) "
            f"exceeds Maximum Taxi Weight ({limits['MTW_kg']} kg) "
            f"by {over:.1f} kg.")
    
    # Check 4: Minimum Weight
    if zfw_weight < limits["MFW_kg"]:
        under = limits["MFW_kg"] - zfw_weight
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) "
            f"is below Minimum Flight Weight ({limits['MFW_kg']} kg) "
            f"by {under:.1f} kg.")
    
    return messages  # Empty list = all checks passed
```

**Example usage:**
```python
# Load limits from file
limits = {
    "MZFW_kg": 237682,
    "MTOW_kg": 351534,
    "MTW_kg": 352441,
    "MFW_kg": 167829
}

# Check a load
zfw = 247274.5  # Too heavy!
tow = 313610.4

warnings = check_limits(zfw, tow, limits)

# Result:
# ["Zero Fuel Weight (247274.5 kg) exceeds Maximum ZFW (237682 kg) by 9592.5 kg."]
```

**Display in UI:**
```python
if warnings:
    print("⚠️ LIMITS VIOLATED ⚠️")
    for msg in warnings:
        print(f"  ❌ {msg}")
else:
    print("✅ All limits OK")
```

---

## 7. Utility Functions (app_utils.py) {#7-utility-functions}

### Purpose: Shared Tools Used Across the System

This file contains functions that multiple modules need. Think of it as a toolbox.

---

### Function 1: load_json_data()

**What it does:** Loads and parses JSON files.

**Why it's separate:**
- Every module needs to load data
- Centralized error handling
- Easy to add logging/validation later

**Function code:**
```python
import json

def load_json_data(filepath):
    """
    Loads and returns data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
    
    Returns:
        dict or list: The parsed JSON data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data
```

**Example usage:**
```python
# Load seat map
seat_data = load_json_data("data/seat_map_new.json")

# Result: Python list/dict ready to use
# No need to worry about file handling
```

**Error handling:**
```python
try:
    data = load_json_data("data/seats.json")
except FileNotFoundError:
    print("❌ File not found! Check the path.")
except json.JSONDecodeError:
    print("❌ File is corrupted or not valid JSON.")
```

---

### Function 2: draw_cg_envelope_base()

**What it does:** Draws the certified CG envelope on a matplotlib axis.

**Why it's important:**
- This is THE reference chart for safety
- Used by both live plot and static plot
- Must be pixel-perfect accurate

**What it draws:**
1. Certified envelope (light grey)
2. Restricted area (dark grey with hatching)
3. Axis labels and grid
4. Proper scaling and limits

**Function signature:**
```python
def draw_cg_envelope_base(ax):
    """
    Draws the B777-300ER CG envelope on a matplotlib axis.
    
    Args:
        ax (matplotlib.axes.Axes): The axis to draw on
    
    The envelope data comes from config.py:
    - CG_ENVELOPE_LOWER_POINTS
    - CG_ENVELOPE_UPPER_POINTS
    - RESTRICTED_AREA_POINTS
    """
```

**How it works (step by step):**

**Step 1: Load envelope coordinates**
```python
lower_points = config.CG_ENVELOPE_LOWER_POINTS
upper_points = config.CG_ENVELOPE_UPPER_POINTS

# Each is a list of (weight_kg, %MAC) tuples
# Example: [(138573, 7.5), (204116, 7.5), ...]
```

**Step 2: Separate into X and Y coordinates**
```python
lower_weights, lower_mac = zip(*lower_points)
upper_weights, upper_mac = zip(*upper_points)

# Unzipping example:
# [(138573, 7.5), (204116, 7.5)] 
# becomes:
# weights = (138573, 204116)
# mac = (7.5, 7.5)
```

**Step 3: Create a filled polygon**
```python
# We need to draw a shape, so we connect the points:
# Lower boundary → Upper boundary (reversed) → back to start

X_poly = list(lower_mac) + list(reversed(upper_mac))
Y_poly = list(lower_weights) + list(reversed(upper_weights))

# This creates a closed polygon
```

**Step 4: Fill the envelope**
```python
ax.fill(X_poly, Y_poly, 
        color='lightgray',   # Light grey fill
        alpha=0.7,           # Slightly transparent
        label='Certified Envelope',
        zorder=1)            # Draw first (background)
```

**Step 5: Draw the boundaries**
```python
# Draw lower boundary line
ax.plot(lower_mac, lower_weights, 
        color='black', linewidth=2)

# Draw upper boundary line
ax.plot(upper_mac, upper_weights, 
        color='black', linewidth=2)
```

**Step 6: Add restricted area**
```python
if restricted_points:
    r_weights, r_mac = zip(*restricted_points)
    ax.fill(r_mac, r_weights,
            color='darkgray',
            alpha=0.6,
            label='Restricted Area',
            zorder=2,        # Draw on top of envelope
            hatch='///')     # Diagonal lines pattern
```

**Step 7: Configure axes**
```python
ax.set_xlabel("Center of Gravity (% MAC)")
ax.set_ylabel("Gross Weight (kg)")
ax.set_title("777-300ER Certified CG Envelope")

# Set limits
ax.set_xlim(5, 50)           # %MAC range
ax.set_ylim(130000, 380000)  # Weight range

# Set ticks
ax.set_xticks(range(5, 55, 5))     # Every 5%
ax.set_yticks(range(130000, 390000, 10000))  # Every 10,000 kg

# Rotate y-axis labels for readability
ax.set_yticklabels(range(130000, 390000, 10000), rotation=45)

# Add grid
ax.grid(axis='y', linestyle='--', alpha=0.5)
```

**Visual result:**
```
Weight (kg)
  ↑
380,000 |         _______________
        |        /               \
350,000 |       /                 \
        |      /  SAFE ZONE        \
300,000 |     /    (grey)           \
        |    /                       \
250,000 |   /    [Restricted]        \
        |  /     (dark grey)          \
200,000 | /___________________________\
        |
150,000 +--------------------------------→ CG (%MAC)
            10%   20%   30%   40%
```

---

### Function 3: plot_cg_envelope()

**What it does:** Creates a static (non-live) plot showing final ZFW and TOW points.

**When it's used:**
- After loading is complete
- User clicks "Show CG Envelope Chart"
- For documentation/printing

**Function signature:**
```python
def plot_cg_envelope(zfw_mac, zfw_weight, tow_mac, tow_weight):
    """
    Displays a static matplotlib chart with ZFW and TOW points.
    
    Args:
        zfw_mac (float): ZFW CG in %MAC
        zfw_weight (float): ZFW in kg
        tow_mac (float): TOW CG in %MAC
        tow_weight (float): TOW in kg
    """
```

**How it works:**
```python
def plot_cg_envelope(zfw_mac, zfw_weight, tow_mac, tow_weight):
    # Step 1: Create figure
    fig, ax = plt.subplots(figsize=(7, 10))
    
    # Step 2: Draw the base envelope
    draw_cg_envelope_base(ax)
    
    # Step 3: Plot ZFW point
    ax.scatter([zfw_mac], [zfw_weight],
              color='red',
              marker='o',
              s=100,           # Size
              zorder=3,        # On top
              label='ZFW CG')
    
    # Step 4: Plot TOW point
    ax.scatter([tow_mac], [tow_weight],
              color='blue',
              marker='o',
              s=100,
              zorder=3,
              label='TOW CG')
    
    # Step 5: Add legend and show
    ax.legend()
    plt.tight_layout()
    plt.show()
```

**Example output:**
```
[Window opens with graph showing:]
- Grey envelope
- Red dot at (24.34%, 237,003 kg) - ZFW
- Blue dot at (32.73%, 328,860 kg) - TOW
- Both dots clearly inside the safe zone
```

---

## 8. Passenger Loading Module {#8-passenger-loading-module}

### Purpose: Interactive Seat Selection Interface

**File:** `modules/passengers_module.py`

**What it does:**
- Shows a visual seat map of the entire aircraft
- User clicks seats to select/deselect passengers
- Calculates total passenger weight and moment
- Returns results to main app

---

### The Seat Map Layout

**Business Class (Rows 1-6):**
```
Row 1:  [A] [C]  [aisle]  [D] [F]  [aisle]  [G] [J]
        ↑   ↑              ↑   ↑              ↑   ↑
      Window              Center            Window
```

**Economy Class (Rows 10-48):**
```
Row 10: [A] [B]  [D] [E] [F] [G] [H]  [J] [K]
        ↑   ↑                             ↑   ↑
      Window                           Window
```

**Visual appearance:**
- **Unselected seat**: White (economy) or light blue (business)
- **Selected seat**: Bright lime green
- **Aisle gaps**: Grey spacers
- **Missing seats**: Empty (some rows have emergency exits)

---

### Class Structure

```python
class SeatSelector:
    def __init__(self, master, seat_map, on_change_callback=None):
        """
        Initializes the seat selection module.
        
        Args:
            master: Parent tkinter widget
            seat_map: JSON data with seat positions and arms
            on_change_callback: Function to call when selection changes
        """
        self.master = master
        self.seat_map = seat_map
        self.selected = set()     # Set of (row, seat) tuples
        self.buttons = {}         # Maps (row, seat) to Button widget
        self.on_change_callback = on_change_callback
```

**Key data structures:**

**self.selected:**
```python
# Example: User selected 3 seats
self.selected = {
    (1, "A"),    # Row 1, Seat A
    (1, "C"),    # Row 1, Seat C
    (10, "D")    # Row 10, Seat D
}
```

**self.buttons:**
```python
# Maps each seat to its button widget
self.buttons = {
    (1, "A"): <Button widget>,
    (1, "C"): <Button widget>,
    # ... for all 425 seats
}
```

---

### Creating the Seat Map UI

**Step 1: Organize seats by class**
```python
# Group rows by cabin class
current_class = None
for row_data in self.seat_map:
    if current_class != row_data["class"]:
        # Insert visual separator between classes
        separator = tk.Frame(height=3, bg='black')
        separator.grid(...)
        current_class = row_data["class"]
```

**Step 2: Get the seat layout**
```python
# From config: Which seats exist in this class?
seat_plan = (config.BUSINESS_SEATPLAN 
             if row_data["class"] == "F" 
             else config.ECONOMY_SEATPLAN)

# Business: ["A", "C", None, "D", "F", None, "G", "J"]
# Economy: ["A", "B", None, "D", "E", "F", "G", "H", None, "J", "K"]
#           ↑    ↑   ↑
#         Seat Seat Aisle
```

**Step 3: Create buttons for each seat**
```python
for seat_letter in seat_plan:
    if seat_letter is None:
        # Aisle gap - create spacer
        spacer = tk.Label(width=3, bg="#ccc")
        spacer.grid(row=row_idx, column=col_idx)
    elif seat_letter in row_data["seats"]:
        # Real seat - create button
        btn = tk.Button(
            text=seat_letter,
            width=4, height=2,
            bg='lightblue' if class=="F" else 'white',
            command=lambda r=row, s=seat_letter: self.toggle_seat(r, s)
        )
        btn.grid(row=row_idx, column=col_idx)
        self.buttons[(row, seat_letter)] = btn
```

---

### Seat Selection Logic

**Function: toggle_seat()**
```python
def toggle_seat(self, row, seat):
    """
    Toggles a single seat between selected and unselected.
    
    Args:
        row (int): Row number (1-48)
        seat (str): Seat letter ("A" through "K")
    """
    key = (row, seat)
    btn = self.buttons[key]
    
    if key in self.selected:
        # Currently selected → Deselect it
        self.selected.remove(key)
        btn.config(
            relief='raised',
            bg='lightblue' if self.get_class(row)=='F' else 'white'
        )
    else:
        # Currently unselected → Select it
        self.selected.add(key)
        btn.config(
            relief='sunken',
            bg='lime green'
        )
    
    # Notify main app that something changed
    self._trigger_callback()
```

**Visual feedback:**
```
Before click:           After click:
┌─────────┐            ┌─────────┐
│    A    │            │░░░A░░░░░│  (green, sunken)
└─────────┘            └─────────┘
(white, raised)
```

---

### Bulk Selection Functions

**Select All:**
```python
def select_all(self):
    """Selects every available seat."""
    for key, btn in self.buttons.items():
        self.selected.add(key)
        btn.config(relief='sunken', bg='lime green')
    self._trigger_callback()
```

**Deselect All:**
```python
def deselect_all(self):
    """Clears all selections."""
    for key, btn in self.buttons.items():
        self.selected.discard(key)
        class_bg = 'lightblue' if self.get_class(key[0])=='F' else 'white'
        btn.config(relief='raised', bg=class_bg)
    self._trigger_callback()
```

**Select Entire Row:**
```python
def select_row(self, row):
    """Selects all seats in a specific row."""
    for key, btn in self.buttons.items():
        if key[0] == row:  # key = (row, seat)
            self.selected.add(key)
            btn.config(relief='sunken', bg='lime green')
    self._trigger_callback()
```

---

### Calculating Passenger Load

**The main function: get_passenger_cg()**

This is what the main app calls to get the results.

```python
def get_passenger_cg(self, pax_weight=88.5):
    """
    Calculates total weight, moment, and CG for selected passengers.
    
    Args:
        pax_weight: Weight per passenger (kg), default 88.5
    
    Returns:
        tuple: (total_weight, total_moment, cg_arm)
               All in kg and inches
    """
    total_weight = 0
    total_moment = 0
    
    # Create quick lookup map: row → seat data
    row_map = {r['row']: r for r in self.seat_map}
    
    # Process each selected seat
    for (row, seat) in self.selected:
        # Get arm for this specific seat
        row_data = row_map[row]
        arm = next((s['arm_in'] for s in row_data['seats'] 
                   if s['seat'] == seat), 0)
        
        # Add to totals
        total_weight += pax_weight
        total_moment += pax_weight * arm
    
    # Calculate CG
    cg = total_moment / total_weight if total_weight > 0 else 0
    
    return total_weight, total_moment, cg
```

**Worked Example:**
```python
# User selected 3 seats:
# - Row 1, Seat A: arm = 570.0 inches
# - Row 1, Seat C: arm = 570.0 inches
# - Row 10, Seat D: arm = 850.0 inches

# Each passenger = 88.5 kg

# Calculation:
Seat 1A: 88.5 kg × 570.0 in = 50,445 kg-in
Seat 1C: 88.5 kg × 570.0 in = 50,445 kg-in
Seat 10D: 88.5 kg × 850.0 in = 75,225 kg-in

Total weight: 3 × 88.5 = 265.5 kg
Total moment: 50,445 + 50,445 + 75,225 = 176,115 kg-in
Passenger CG: 176,115 / 265.5 = 663.4 inches

Returns: (265.5, 176115.0, 663.4)
```

---

### The Callback System

**Why callbacks?**
The passenger module doesn't know about the main app or other modules. When something changes, it just says "Hey, I changed!" and the main app decides what to do.

**How it works:**
```python
# In the module:
def _trigger_callback(self):
    if self.on_change_callback:
        self.on_change_callback()

# When main app creates the module:
seat_module = SeatSelector(parent, data, 
                          on_change_callback=self.recalculate_everything)

# Now when user clicks a seat:
# 1. toggle_seat() runs
# 2. _trigger_callback() is called
# 3. main app's recalculate_everything() runs
# 4. Graph updates
```

---

## 9. Cargo Loading Module {#9-cargo-loading-module}

### Purpose: Cargo Bay Loading with Blocking Logic

**File:** `modules/cargo_module.py`

**What it does:**
- Shows cargo bay positions
- Handles ULD (Unit Load Device) loading
- Implements container/pallet blocking logic
- Calculates cargo weight and moment

---

### Understanding the Cargo Hold

**The B777-300ER has 3 cargo compartments:**

```
[Forward Hold]  [Aft Hold]  [Bulk Hold]
    11R 12R        31R 32R       51L 52R
    11L 12L        31L 32L
    
    [1P Pallet]    [3P Pallet]
    (spans 11R+12R) (spans 31R+32R)
```

**The Complexity: Containers vs Pallets**

- **Containers** (LD-3, LD-6): Small, one per position
- **Pallets** (96" × 125"): Large, span multiple container positions

**The Problem:**
- If you load a pallet, it blocks the containers under it
- If you load containers, you can't load the pallet over them

---

### Data Structure

**Container position:**
```json
{
  "compartment": "FWD",
  "position": "11R",
  "arm_in": 750.0,
  "allowed_ULDs": [
    {
      "type": "LD-3",
      "max_kg": 1587.6
    }
  ]
}
```

**Pallet position:**
```json
{
  "compartment": "FWD",
  "position": "1P",
  "arm_in": 760.0,
  "blocks": ["11R", "12R"],  ← Blocks these containers
  "allowed_ULDs": [
    {
      "type": "96x125-pallet",
      "max_kg": 6033.0
    }
  ]
}
```

---

### Class Structure

```python
class CargoLoadSystem:
    def __init__(self, master, cargo_data, on_change_callback=None):
        self.master = master
        self.cargo_data = cargo_data
        self.state = {}    # {(comp, pos): {"weight": w, "ULD_type": t}}
        self.buttons = {}  # {(comp, pos): (btn_load, btn_max, btn_custom)}
        self.on_change_callback = on_change_callback
```

**State tracking:**
```python
# Example state:
self.state = {
    ("FWD", "11R"): {"weight": 1587.6, "ULD_type": "LD-3"},
    ("FWD", "12R"): {"weight": 1200.0, "ULD_type": "LD-3"},
    ("AFT", "1P"): None  # Empty
}
```

---

### Creating the Cargo UI

**Step 1: Organize by compartment and type**
```python
# Separate containers from pallets
for slot in cargo_data:
    if "blocks" in slot:
        # This is a pallet
        pallets.append(slot)
    else:
        # This is a container
        containers.append(slot)
```

**Step 2: Create widget for each position**
```python
def _create_slot_widget(self, slot, row, col):
    key = (slot["compartment"], slot["position"])
    
    container = tk.Frame(bd=1, relief="solid")
    container.grid(row=row, column=col)
    
    # Position label
    tk.Label(container, text=slot["position"]).pack()
    
    # Load Max button
    btn_max = tk.Button(
        container, 
        text="Load Max",
        command=lambda k=key: self.load_max_weight(k)
    )
    btn_max.pack()
    
    # Custom Load button
    btn_custom = tk.Button(
        container,
        text="Custom Load",
        command=lambda k=key: self.custom_weight_input(k)
    )
    btn_custom.pack()
    
    # Select/Deselect button (shows current weight)
    btn_load = tk.Button(
        container,
        text="Select/Deselect",
        command=lambda k=key: self.toggle_load(k)
    )
    btn_load.pack()
    
    # Store button references
    self.buttons[key] = (btn_load, btn_max, btn_custom)
```

---

### Loading Functions

**Load Maximum Weight:**
```python
def load_max_weight(self, key):
    """Loads the maximum weight for a cargo position."""
    slot = next(s for s in self.cargo_data 
                if (s['compartment'], s['position']) == key)
    
    allowed_ULDs = slot.get("allowed_ULDs", [])
    if not allowed_ULDs:
        messagebox.showwarning("No ULD", "No ULD allowed here")
        return
    
    # Use first ULD as default
    max_uld = allowed_ULDs[0]
    self.state[key] = {
        "weight": max_uld["max_kg"],
        "ULD_type": max_uld["type"]
    }
    
    self.update_all_blocks()  # Check blocking
    self._trigger_callback()   # Notify main app
```

**Custom Weight Input:**
```python
def custom_weight_input(self, key):
    """Opens dialog for custom weight entry."""
    slot = next(s for s in self.cargo_data 
                if (s['compartment'], s['position']) == key)
    
    max_uld = slot["allowed_ULDs"][0]
    
    # Show input dialog
    input_val = simpledialog.askfloat(
        "Custom Weight",
        f"Enter weight (max {max_uld['max_kg']} kg):",
        minvalue=0,
        maxvalue=max_uld['max_kg']
    )
    
    if input_val is not None:
        self.state[key] = {
            "weight": round(input_val, 1),
            "ULD_type": max_uld["type"]
        }
        self.update_all_blocks()
        self._trigger_callback()
```

---

### The Blocking Logic - The Complex Part

**This is the most important function in the cargo module.**

```python
def update_all_blocks(self):
    """
    Updates UI based on blocking logic:
    - If pallet is loaded, block its containers
    - If container is loaded, block its pallet
    """
    blocked_keys = set()
    
    # Step 1: Find all blocked positions
    for key, load in self.state.items():
        if not load:
            continue  # Skip empty positions
        
        slot = next(s for s in self.cargo_data 
                    if (s['compartment'], s['position']) == key)
        
        if "blocks" in slot:
            # This is a PALLET - block its containers
            for pos in slot["blocks"]:
                blocked_keys.add((slot['compartment'], pos))
        else:
            # This is a CONTAINER - check if blocked by pallet
            for pallet_slot in self.cargo_data:
                if "blocks" in pallet_slot:
                    # Is this container in the pallet's footprint?
                    if key[1] in pallet_slot["blocks"]:
                        pallet_key = (pallet_slot['compartment'], 
                                     pallet_slot['position'])
                        # Is the pallet loaded?
                        if self.state.get(pallet_key):
                            blocked_keys.add(key)
                            break
    
    # Step 2: Update UI for all buttons
    for key, (btn_load, btn_max, btn_custom) in self.buttons.items():
        load_data = self.state.get(key)
        
        if key in blocked_keys:
            # BLOCKED
            btn_load.config(
                state=tk.DISABLED,
                bg="lightgray",
                text="Blocked"
            )
            btn_max.config(state=tk.DISABLED)
            btn_custom.config(state=tk.DISABLED)
            
        elif load_data:
            # LOADED
            btn_load.config(
                state=tk.NORMAL,
                bg="limegreen",
                text=f"{load_data['weight']} kg"
            )
            btn_max.config(state=tk.NORMAL)
            btn_custom.config(state=tk.NORMAL)
            
        else:
            # AVAILABLE
            btn_load.config(
                state=tk.NORMAL,
                bg="SystemButtonFace",
                text="Select/Deselect"
            )
            btn_max.config(state=tk.NORMAL)
            btn_custom.config(state=tk.NORMAL)
    
    self.update_summary()
```

**Example scenario:**
```
Initial state: All empty

User loads pallet 1P → Blocks 11R and 12R
┌─────────┐  ┌─────────┐     ┌──────────────┐
│  11R    │  │  12R    │ →   │  1P Pallet   │
│Available│  │Available│     │   LOADED     │
└─────────┘  └─────────┘     └──────────────┘
                                     ↓
                              ┌─────────┐  ┌─────────┐
                              │  11R    │  │  12R    │
                              │ BLOCKED │  │ BLOCKED │
                              └─────────┘  └─────────┘

User tries to load 11R → Error: "Blocked by pallet 1P"

User unloads pallet 1P → 11R and 12R become available again
```

---

### Calculating Cargo Load

**The main function:**
```python
def get_cargo_cg(self):
    """
    Calculates total cargo weight, moment, and CG.
    
    Returns:
        tuple: (total_weight, total_moment, cg)
    """
    total_weight = 0
    total_moment = 0
    
    for key, load in self.state.items():
        if not load:
            continue
        
        # Find the slot data
        slot = next(s for s in self.cargo_data 
                    if (s['compartment'], s['position']) == key)
        
        arm = slot.get("arm_in", 0)
        weight = load['weight']
        
        total_weight += weight
        total_moment += weight * arm
    
    cg = total_moment / total_weight if total_weight > 0 else 0
    return total_weight, total_moment, cg
```

**Example calculation:**
```python
# State:
# FWD 11R: 1500 kg at arm 750 in
# AFT 31R: 1200 kg at arm 1450 in

# Calculation:
Cargo 11R: 1500 × 750 = 1,125,000 kg-in
Cargo 31R: 1200 × 1450 = 1,740,000 kg-in

Total weight: 2,700 kg
Total moment: 2,865,000 kg-in
Cargo CG: 2,865,000 / 2,700 = 1,061.1 inches

Returns: (2700.0, 2865000.0, 1061.1)
```

---

## 10. Fuel Loading Module {#10-fuel-loading-module}

### Purpose: Fuel Tank Management with Variable CG

**File:** `modules/fuel_load_module.py`

**What it does:**
- Displays all fuel tanks
- Allows liter input for each tank
- Automatically calculates variable fuel CG (interpolation)
- Handles combined tank logic (Main 1 + Main 2)

---

### The Fuel Tank Challenge

**Why fuel is complex:**

1. **Tank CG changes as it fills**
```
Empty tank:         Half full:          Full tank:
    ___                 ___                 ___
   /   \               /   \               /###\
  /     \             /#####\             /#####\
 /_______\           /#######\           /#######\
 
CG at 1300"         CG at 1315"         CG at 1330"
```

2. **Main tanks use combined table**
When BOTH Main Tank 1 and Main Tank 2 have fuel, we use a special "combined" table that's more accurate than calculating them separately.

---

### The B777-300ER Fuel System

**Tank layout:**
```
        [Main Tank 1]                    [Main Tank 2]
        Wing Left                        Wing Right
        Max: 39,000 L                    Max: 39,000 L
        
                    [Center Tank]
                    Fuselage
                    Max: 103,332 L
```

**Total capacity:**
- Main 1: 39,000 L × 0.8507 kg/L = 33,177 kg
- Main 2: 39,000 L × 0.8507 kg/L = 33,177 kg
- Center: 103,332 L × 0.8507 kg/L = 87,904 kg
- **Total: 154,258 kg**

---

### Data Structure

**Individual tank:**
```json
{
  "tank": "Main Tank 1",
  "max_l": 39000,
  "max_kg": 33177,
  "arm_table": [
    [0, 1200.0],
    [10000, 1210.5],
    [20000, 1225.8],
    [30000, 1240.2],
    [39000, 1255.0]
  ]
}
```

**Combined table (backend only):**
```json
{
  "tank": "main_tanks_combined_table",
  "arm_table": [
    [0, 1220.0],
    [20000, 1230.5],
    [40000, 1238.2],
    [60000, 1244.8],
    [78000, 1250.0]
  ]
}
```

---

### Class Structure

```python
class FuelLoadSystem:
    def __init__(self, master, tank_data, on_change_callback=None):
        self.master = master
        self.tank_data = tank_data
        self.state = {}  # {tank_name: {"liters": L, "arm": A, "weight": W}}
        self.widgets = {}  # {tank_name: {entry, arm_label, kg_label}}
        self.fuel_density = config.DEFAULT_FUEL_DENSITY_KG_L
        self.on_change_callback = on_change_callback
```

**State example:**
```python
self.state = {
    "Main Tank 1": {
        "liters": 30000,
        "arm": 1240.2,
        "weight": 25521.0
    },
    "Main Tank 2": {
        "liters": 30000,
        "arm": 1240.2,
        "weight": 25521.0
    },
    "Center Tank": {
        "liters": 50000,
        "arm": 1350.8,
        "weight": 42535.0
    },
    "Main Tanks Combined": {  # Calculated when both mains have fuel
        "liters": 60000,
        "arm": 1244.8,
        "weight": 51042.0
    }
}
```

---

### Creating the Fuel UI

**For each tank:**
```python
for tank in self.tank_data:
    tname = tank["tank"]
    
    # Skip the combined table (backend only)
    if tname == "main_tanks_combined_table":
        continue
    
    # Create frame for this tank
    tf = tk.Frame(bd=1, relief="solid")
    tf.grid(row=0, column=col)
    
    # Tank name
    tk.Label(tf, text=tname).pack()
    
    # Max capacity
    tk.Label(tf, text=f"Max: {tank['max_l']} L").pack()
    
    # Entry field for liters
    entry = tk.Entry(tf, width=10)
    entry.insert(0, "0")
    entry.pack()
    
    # Buttons
    tk.Button(tf, text="Set Liters",
             command=lambda t=tank: self.set_liters_popup(t)).pack()
    tk.Button(tf, text="Load Max",
             command=lambda t=tank: self.set_liters(t, t["max_l"])).pack()
    
    # Display labels
    arm_label = tk.Label(tf, text="Arm: --")
    arm_label.pack()
    kg_label = tk.Label(tf, text="Weight: --")
    kg_label.pack()
    
    # Store widgets
    self.widgets[tname] = {
        "entry": entry,
        "arm_label": arm_label,
        "kg_label": kg_label
    }
```

---

### Setting Fuel Amount

**Main function:**
```python
def set_liters(self, tank, liters):
    """
    Sets fuel amount for a tank and recalculates arm/weight.
    
    Args:
        tank: Tank data dict
        liters: Amount of fuel in liters
    """
    liters = round(liters, 1)
    tname = tank["tank"]
    
    # Step 1: Interpolate arm from tank table
    arm = interpolate_arm(tank["arm_table"], liters)
    
    # Step 2: Calculate weight
    kg = round(liters * self.fuel_density, 1)
    
    # Step 3: Update state
    self.state[tname] = {
        "liters": liters,
        "arm": arm,
        "weight": kg
    }
    
    # Step 4: Update UI display
    w = self.widgets[tname]
    w["entry"].delete(0, tk.END)
    w["entry"].insert(0, str(liters))
    w["arm_label"].config(text=f"Arm: {arm:.2f} in")
    w["kg_label"].config(text=f"Weight: {kg:.1f} kg")
    
    # Step 5: Recalculate totals (handles combined logic)
    self.update_summary()
```

**Example:**
```python
# User enters 25,000 liters into Main Tank 1

# Tank table (simplified):
# [[0, 1200], [10000, 1210], [20000, 1225], [30000, 1240], [39000, 1255]]

# Interpolate between 20k and 30k:
# percentage = (25000 - 20000) / (30000 - 20000) = 0.5
# arm = 1225 + 0.5 × (1240 - 1225) = 1232.5 inches

# Weight = 25000 × 0.8507 = 21,267.5 kg

# State updated:
self.state["Main Tank 1"] = {
    "liters": 25000,
    "arm": 1232.5,
    "weight": 21267.5
}

# UI shows:
# "Arm: 1232.50 in"
# "Weight: 21267.5 kg"
```

---

### The Combined Tank Logic

**Why it exists:**
When both main wing tanks have fuel, their combined CG is NOT the average of their individual CGs. The tank shapes overlap in the wing root area.

Boeing provides a special "combined" table that's more accurate.

**The rules:**
```
If Main 1 empty AND Main 2 empty:
    → Use neither table

If Main 1 has fuel AND Main 2 empty:
    → Use Main 1 table only

If Main 1 empty AND Main 2 has fuel:
    → Use Main 2 table only

If Main 1 has fuel AND Main 2 has fuel:
    → Use COMBINED table (ignore individual tables)
```

**Implementation:**
```python
def update_summary(self):
    """Recalculates totals with combined tank logic."""
    total_weight = 0
    total_moment = 0
    
    # Check if we should use combined table
    main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
    main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
    
    combined_tank = next(
        (t for t in self.tank_data 
         if t.get("tank") == "main_tanks_combined_table"),
        None
    )
    
    use_combined = (combined_tank and 
                   main1_liters > 0 and 
                   main2_liters > 0)
    
    if use_combined:
        # Use combined table
        total_main_liters = main1_liters + main2_liters
        combined_arm = interpolate_arm(
            combined_tank["arm_table"],
            total_main_liters
        )
        combined_weight = round(total_main_liters * self.fuel_density, 1)
        
        # Store in state
        self.state["Main Tanks Combined"] = {
            "liters": total_main_liters,
            "arm": combined_arm,
            "weight": combined_weight
        }
        
        total_weight += combined_weight
        total_moment += combined_weight * combined_arm
    else:
        # Clear combined entry
        if "Main Tanks Combined" in self.state:
            del self.state["Main Tanks Combined"]
    
    # Add all other tanks
    for tank in self.tank_data:
        tname = tank["tank"]
        if tname == "main_tanks_combined_table":
            continue
        if use_combined and tname in ("Main Tank 1", "Main Tank 2"):
            continue  # Skip individual mains
        
        tank_data = self.state.get(tname, {})
        weight = tank_data.get("weight", 0)
        arm = tank_data.get("arm", 0)
        total_weight += weight
        total_moment += weight * arm
    
    # Calculate total CG
    total_cg = total_moment / total_weight if total_weight > 0 else 0
    
    # Update display
    self.summary_label.config(
        text=f"Total Fuel: {total_weight:.1f} kg\n"
             f"Total Moment: {total_moment:.1f} kg-in\n"
             f"Fuel CG: {total_cg:.2f} in"
    )
    
    self._trigger_callback()
```

**Example calculation:**
```
Scenario: Both main tanks have 30,000 liters

WRONG way (don't do this):
Main 1: 30000 L at 1240 in = 25521 kg × 1240 in = 31,646,040 kg-in
Main 2: 30000 L at 1240 in = 25521 kg × 1240 in = 31,646,040 kg-in
Total: 51042 kg, moment = 63,292,080 kg-in
CG = 1240.0 inches ❌ INACCURATE

CORRECT way (using combined table):
Total: 60000 L
Interpolate from combined table → arm = 1244.8 inches
Weight: 60000 × 0.8507 = 51,042 kg
Moment: 51042 × 1244.8 = 63,536,881.6 kg-in
CG = 1244.8 inches ✅ ACCURATE

Difference: 4.8 inches (significant for safety!)
```

---

### Fuel Density Changes

**Why density matters:**
```
Cold day (-20°C): Density = 0.8507 kg/L (heavy)
Hot day (+40°C): Density = 0.7309 kg/L (light)

Same volume, different weight!
```

**How to change density:**
```python
def set_density(self):
    """Opens dialog to change fuel density."""
    density = simpledialog.askfloat(
        "Fuel Density",
        "Enter fuel density (kg/L) between 0.7309 and 0.8507:",
        minvalue=0.7309,
        maxvalue=0.8507,
        initialvalue=self.fuel_density
    )
    
    if density:
        self.fuel_density = density
        
        # Recalculate ALL tanks with new density
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue
            
            liters = self.state.get(tname, {}).get("liters", 0)
            if liters > 0:
                self.set_liters(tank, liters)
```

**Example:**
```
Tank has 50,000 liters

At 0.8507 kg/L: 50000 × 0.8507 = 42,535 kg
At 0.7309 kg/L: 50000 × 0.7309 = 36,545 kg

Difference: 5,990 kg! (Significant for TOW)
```

---
## 11. Live Visualization System (continued)

```python
self.scatter_intermediate = self.ax.scatter(
    [], [], color='black', s=50,
    label="Intermediate Points")
self.scatter_zfw = self.ax.scatter(
    [], [], color='red', marker='o', s=120,
    label="ZFW CG")
self.scatter_tow = self.ax.scatter(
    [], [], color='blue', marker='o', s=120,
    label="TOW CG")

self.ax.legend()

# Show plot without blocking
plt.ion()
plt.show(block=False)
```

---

### Thread Safety - Why It Matters

**The problem:**

```
Main Thread (tkinter):          Plot Thread (matplotlib):
User clicks seat                     Drawing graph
  ↓                                       ↓
Triggers update                      Reading data
  ↓                                       ↓
Modifies data ──────── CONFLICT! ────────┘
```

Without locks: Data corruption, crashes, incorrect plots

With locks:

```python
with self._lock:
    # Only one thread can be here at a time
    self.line_pax.set_data(x, y)
    self.fig.canvas.draw()
```

### Updating the Trace

Main function:

```python
def update_full_trace(self, trace_points):
    """
    Updates the entire loading sequence.
    
    Args:
        trace_points: List of 4 (mac, weight) tuples:
                      [0] = DOW
                      [1] = DOW + Passengers
                      [2] = ZFW (DOW + Pax + Cargo)
                      [3] = TOW (ZFW + Fuel)
    """
    if not trace_points or len(trace_points) != 4:
        return  # Invalid data
    
    # Unpack the 4 points
    p_dow = trace_points[0]   # (mac%, weight)
    p_pax = trace_points[1]
    p_zfw = trace_points[2]
    p_tow = trace_points[3]
    
    # Acquire lock for thread safety
    with self._lock:
        # Update line 1: DOW → DOW+Pax (orange)
        self.line_pax.set_data(
            [p_dow[0], p_pax[0]],      # X coords (mac%)
            [p_dow[1], p_pax[1]]       # Y coords (weight)
        )
        
        # Update line 2: DOW+Pax → ZFW (green)
        self.line_cargo.set_data(
            [p_pax[0], p_zfw[0]],
            [p_pax[1], p_zfw[1]]
        )
        
        # Update line 3: ZFW → TOW (blue)
        self.line_fuel.set_data(
            [p_zfw[0], p_tow[0]],
            [p_zfw[1], p_tow[1]]
        )
        
        # Update scatter points
        import numpy as np
        self.scatter_intermediate.set_offsets(
            np.array([p_dow, p_pax])
        )
        self.scatter_zfw.set_offsets(np.array([p_zfw]))
        self.scatter_tow.set_offsets(np.array([p_tow]))
        
        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
```

Example call:

```python
# Main app calculates 4 points:
trace = [
    (28.0, 170200),   # DOW
    (29.5, 210113.5), # +Passengers
    (24.34, 237003.5),# ZFW (+Cargo)
    (32.73, 328860.4) # TOW (+Fuel)
]

# Update live plot
live_plot.update_full_trace(trace)

# Plot window instantly shows the new trace!
```

### Resetting the Trace

When to use:
- User clicks "Reset"
- Starting a new load plan
- Switching aircraft

```python
def reset_trace(self):
    """Clears all lines and points from the plot."""
    with self._lock:
        # Clear all 3 lines
        self.line_pax.set_data([], [])
        self.line_cargo.set_data([], [])
        self.line_fuel.set_data([], [])
        
        # Clear all scatter plots
        empty = np.empty((0, 2))  # Empty 2D array
        self.scatter_intermediate.set_offsets(empty)
        self.scatter_zfw.set_offsets(empty)
        self.scatter_tow.set_offsets(empty)
        
        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
```

Result: Empty envelope graph (just the grey certified area)

---

## 12. Main Application Integration

**Purpose:** The Orchestrator

**File:** `main_app.py`

**What it does:**
- Creates the main window
- Initializes all 3 modules (passengers, cargo, fuel)
- Coordinates all calculations
- Updates the live plot
- Displays the final summary

### Application Structure

```python
class AircraftSummaryApp:
    def __init__(self, master):
        """Initialize the main application."""
        self.master = master
        self.master.title("Full Aircraft Load Summary")
        
        # Load all data files
        self.weight_limits = load_json(config.LIMITS_FILEPATH)
        self.aircraft_ref_data = load_json(config.AIRCRAFT_REFERENCE_FILEPATH)
        seat_map_data = load_json(config.SEAT_MAP_FILEPATH)
        cargo_data = load_json(config.CARGO_POSITIONS_FILEPATH)
        fuel_data = load_json(config.FUEL_TANKS_FILEPATH)
        
        # Runtime configuration
        self.config = {
            "passenger_weight": 88.5,
            "fuel_density": 0.8507,
            "le_mac": 1174.5,
            "mac_length": 278.5,
            "klm_reference_arm": 1258
        }
        
        # Build UI
        self._build_ui_frames(master)
        
        # Initialize modules
        self.seat_module = SeatSelector(self.pax_tab, seat_map_data)
        self.cargo_module = CargoLoadSystem(self.cargo_tab, cargo_data)
        self.fuel_module = FuelLoadSystem(self.fuel_tab, fuel_data)
        
        # Register callbacks
        self._register_callbacks()
        
        # Initialize live plot
        self.live_plot = LiveCGPlot()
        
        # Build summary panel
        self._build_summary_panel(self.main_frame)
        self.build_config_ui()
        
        # Initial calculation
        self.calculate_aircraft_summary(update_plot=True)
```

---

### The UI Layout

```
┌────────────────────────────────────────────────────────────────┐
│  [Select Aircraft: PH-BVA ▼]  [Recalculate]                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐│
│  │  Tabs:                  │  │  Summary Panel               ││
│  │  ┌──────────────────┐   │  │                              ││
│  │  │ [Passengers]     │   │  │  [Calculate Summary]         ││
│  │  ├──────────────────┤   │  │  [Show CG Chart]             ││
│  │  │ [Cargo]          │   │  │  [Reset Live Trace]          ││
│  │  ├──────────────────┤   │  │                              ││
│  │  │ [Fuel]           │   │  │  ┌─────────────────────────┐││
│  │  ├──────────────────┤   │  │  │ Summary Text:           │││
│  │  │ [Config]         │   │  │  │                         │││
│  │  └──────────────────┘   │  │  │ DOW: 170200 kg          │││
│  │                         │  │  │ Pax: 39913.5 kg         │││
│  │  [Module content here]  │  │  │ Cargo: 26890 kg         │││
│  │                         │  │  │ Fuel: 91856.9 kg        │││
│  │                         │  │  │                         │││
│  │                         │  │  │ ZFW: 237003.5 kg        │││
│  │                         │  │  │ TOW: 328860.4 kg        │││
│  │                         │  │  │                         │││
│  │                         │  │  │ ✅ All limits OK        │││
│  │                         │  │  └─────────────────────────┘││
│  └─────────────────────────┘  └──────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

### The Core Calculation Function

This is the heart of the entire system.

```python
def calculate_aircraft_summary(self, update_plot=False):
    """
    Performs complete W&B calculation.
    
    This function:
    1. Gets DOW from aircraft reference
    2. Collects loads from all 3 modules
    3. Calculates sequential loading (DOW→+Pax→ZFW→TOW)
    4. Converts to %MAC
    5. Calculates KLM indices
    6. Checks limits
    7. Updates live plot (if requested)
    8. Displays summary
    """
```

Step-by-step breakdown:

#### Step 1: Get aircraft starting point (DOW)

```python
# Get selected aircraft
reg = self.selected_reg.get()  # e.g., "PH-BVA"
aircraft_ref = next(
    (d for d in self.dow_options if d["reg"] == reg),
    self.dow_options[0]
)

dow_weight = aircraft_ref["dow_weight_kg"]  # 170,200 kg
doi = aircraft_ref.get("doi", 0)            # 45.3

# Calculate DOW arm from DOI
dow_arm = calc.calculate_arm_from_doi(
    doi, dow_weight, self.config["klm_reference_arm"]
)  # Returns 1252.48 inches

dow_moment = dow_weight * dow_arm  # 212,841,856 kg-in
```

#### Step 2: Convert DOW to %MAC

```python
dow_mac = calc.calculate_mac_percent(
    dow_arm,
    self.config["le_mac"],
    self.config["mac_length"]
)  # Returns 28.0% MAC
```

#### Step 3: Collect loads from modules

```python
# Get passenger load
pax_weight, pax_moment, pax_cg = self.seat_module.get_passenger_cg(
    pax_weight=self.config["passenger_weight"]
)  # Returns (39913.5, 51144327.0, 1281.05)

# Get cargo load
cargo_weight, cargo_moment, cargo_cg = self.cargo_module.get_cargo_cg()
# Returns (26890.0, 38634511.1, 1436.7)

# Get fuel load
fuel_weight, fuel_moment, fuel_cg = self.fuel_module.get_fuel_cg()
# Returns (91856.9, 121649624.7, 1324.5)
```

#### Step 4: Calculate Point 2 (DOW + Passengers)

```python
dow_pax_weight = dow_weight + pax_weight
# = 170200 + 39913.5 = 210,113.5 kg

dow_pax_moment = dow_moment + pax_moment
# = 212841856 + 51144327 = 263,986,183 kg-in

dow_pax_cg = dow_pax_moment / dow_pax_weight if dow_pax_weight > 0 else dow_arm
# = 263986183 / 210113.5 = 1,256.4 inches

dow_pax_mac = calc.calculate_mac_percent(dow_pax_cg, ...)
# = 29.4% MAC
```

#### Step 5: Calculate Point 3 (ZFW = DOW + Pax + Cargo)

```python
zfw_weight = dow_pax_weight + cargo_weight
# = 210113.5 + 26890 = 237,003.5 kg

zfw_moment = dow_pax_moment + cargo_moment
# = 263986183 + 38634511 = 302,620,694 kg-in

zfw_cg = zfw_moment / zfw_weight
# = 302620694 / 237003.5 = 1,276.8 inches

zfw_mac = calc.calculate_mac_percent(zfw_cg, ...)
# = 36.7% MAC
```

#### Step 6: Calculate Point 4 (TOW = ZFW + Fuel)

```python
tow_weight = zfw_weight + fuel_weight
# = 237003.5 + 91856.9 = 328,860.4 kg

tow_moment = zfw_moment + fuel_moment
# = 302620694 + 121649625 = 424,270,319 kg-in

tow_cg = tow_moment / tow_weight
# = 424270319 / 328860.4 = 1,290.2 inches

tow_mac = calc.calculate_mac_percent(tow_cg, ...)
# = 41.5% MAC
```

#### Step 7: Update live plot

```python
if update_plot:
    trace_points = [
        (dow_mac, dow_weight),      # Point 1
        (dow_pax_mac, dow_pax_weight), # Point 2
        (zfw_mac, zfw_weight),      # Point 3
        (tow_mac, tow_weight)       # Point 4
    ]
    self.live_plot.update_full_trace(trace_points)
```

#### Step 8: Calculate KLM indices

```python
ref_arm = self.config["klm_reference_arm"]  # 1258

# DOW gets base function (with +50 offset)
klm_dow = calc.klm_index_base(dow_weight, dow_arm, ref_arm)
# = 45.3

# Components get component function (NO offset)
klm_pax = calc.klm_index_component(pax_weight, pax_cg, ref_arm)
# = 4.61

klm_car = calc.klm_index_component(cargo_weight, cargo_cg, ref_arm)
# = 7.13

klm_fuel = calc.klm_index_component(fuel_weight, fuel_cg, ref_arm)
# = 30.56

# Totals
klm_all_zfw = klm_dow + klm_pax + klm_car  # = 57.04
klm_all_tow = klm_all_zfw + klm_fuel        # = 87.60
```

#### Step 9: Check limits

```python
breach_messages = calc.check_limits(
    zfw_weight, tow_weight, self.weight_limits
)

# If any limits exceeded, returns list of warnings
# If all OK, returns empty list
```

#### Step 10: Build summary string

```python
summary_str = f"Selected Aircraft: {reg}\n\n"
summary_str += "------ 777-300ER Aircraft Load Summary ------\n\n"
summary_str += f"Operating (DOW):     {dow_weight:.1f} kg   @ {dow_arm:.2f} in (%MAC: {dow_mac:.2f})\n"
summary_str += f"Passengers:          {pax_weight:.1f} kg   Moment: {pax_moment:.1f}\n"
summary_str += f"Cargo:               {cargo_weight:.1f} kg   Moment: {cargo_moment:.1f}\n"
summary_str += f"Fuel:                {fuel_weight:.1f} kg   Moment: {fuel_moment:.1f}\n\n"
summary_str += f"ZERO FUEL WEIGHT:    {zfw_weight:.1f} kg   ZFW CG: {zfw_cg:.2f} in (%MAC: {zfw_mac:.2f})\n"
summary_str += f"TAKEOFF WEIGHT:      {tow_weight:.1f} kg   TOW CG: {tow_cg:.2f} in (%MAC: {tow_mac:.2f})\n\n"
summary_str += f"KLM INDEX (CGI) [ref {ref_arm} in]:\n"
summary_str += f"  ZFW Index:         {klm_all_zfw:.2f}\n"
summary_str += f"  TOW Index:         {klm_all_tow:.2f}\n"
# ... etc

# Display in text box
self.output_box.delete("1.0", tk.END)
self.output_box.insert(tk.END, summary_str)
```

### The Callback System

How modules notify the main app:

```python
def _register_callbacks(self):
    """Link module callbacks to main app."""
    self.seat_module.on_change_callback = self.on_load_change
    self.cargo_module.on_change_callback = self.on_load_change
    self.fuel_module.on_change_callback = self.on_load_change

def on_load_change(self):
    """
    Schedules an update after load changes.
    Uses debouncing to avoid too many rapid updates.
    """
    if self._update_after_id:
        self.master.after_cancel(self._update_after_id)
    
    # Schedule update 150ms from now
    self._update_after_id = self.master.after(
        150,  # milliseconds
        self._process_load_change
    )

def _process_load_change(self):
    """The actual update function."""
    self._update_after_id = None
    self.calculate_aircraft_summary(update_plot=True)
```

**Why debouncing?**

```
Without debouncing:
User clicks 5 seats rapidly
  ↓
5 recalculations (slow, unnecessary)

With debouncing:
User clicks 5 seats rapidly
  ↓
Wait 150ms after last click
  ↓
1 recalculation (fast, efficient)
```

---

## 13. Data Files - The Aircraft Database

**Purpose:** Separation of Data from Code

All aircraft-specific data lives in JSON files in the `data/` folder.

**Why JSON?**
- Human-readable (can open in any text editor)
- Easy to validate (JSON validators available)
- No code changes needed to update data
- Can be version-controlled separately

### File 1: seat_map_new.json

**Purpose:** Every seat's position and arm

**Structure:**

```json
[
  {
    "class": "F",
    "row": 1,
    "seats": [
      {"seat": "A", "arm_in": 570.0},
      {"seat": "C", "arm_in": 570.0},
      {"seat": "D", "arm_in": 570.0},
      {"seat": "F", "arm_in": 570.0},
      {"seat": "G", "arm_in": 570.0},
      {"seat": "J", "arm_in": 570.0}
    ]
  },
  {
    "class": "Y",
    "row": 10,
    "seats": [
      {"seat": "A", "arm_in": 850.0},
      {"seat": "B", "arm_in": 850.0},
      {"seat": "D", "arm_in": 850.0},
      {"seat": "E", "arm_in": 850.0},
      {"seat": "F", "arm_in": 850.0},
      {"seat": "G", "arm_in": 850.0},
      {"seat": "H", "arm_in": 850.0},
      {"seat": "J", "arm_in": 850.0},
      {"seat": "K", "arm_in": 850.0}
    ]
  }
  // ... more rows
]
```

**Total entries:** ~45 rows × 6-9 seats = ~380 seat entries

**Source:** Boeing WBCLM, Cabin Configuration Section

### File 2: cargo_positions.json

**Purpose:** All cargo bays with arms and ULD limits

Container example:

```json
{
  "compartment": "FWD",
  "position": "11R",
  "arm_in": 750.0,
  "allowed_ULDs": [
    {
      "type": "LD-3",
      "max_kg": 1587.6
    }
  ]
}
```

Pallet example:

```json
{
  "compartment": "FWD",
  "position": "1P",
  "arm_in": 760.0,
  "blocks": ["11R", "12R"],
  "allowed_ULDs": [
    {
      "type": "96x125-pallet",
      "max_kg": 6033.0
    }
  ]
}
```

**Total entries:** ~20-30 cargo positions

**Source:** Boeing WBCLM, Cargo Loading Manual Section

### File 3: fuel_tanks.json

**Purpose:** Tank capacities and variable arm tables

Example:

```json
[
  {
    "tank": "Main Tank 1",
    "max_l": 39000,
    "max_kg": 33177,
    "arm_table": [
      [0, 1200.0],
      [5000, 1205.2],
      [10000, 1210.5],
      [15000, 1216.1],
      [20000, 1222.8],
      [25000, 1230.2],
      [30000, 1238.5],
      [35000, 1247.2],
      [39000, 1255.0]
    ]
  },
  {
    "tank": "Center Tank",
    "max_l": 103332,
    "max_kg": 87904,
    "arm_table": [
      [0, 1342.1],
      [10000, 1345.2],
      [20000, 1348.8],
      // ... more points
      [103332, 1380.5]
    ]
  },
  {
    "tank": "main_tanks_combined_table",
    "arm_table": [
      [0, 1220.0],
      [10000, 1225.5],
      // ... more points
      [78000, 1250.0]
    ]
  }
]
```

**Source:** Boeing WBCLM, Fuel System Section, CG vs Volume tables

### File 4: aircraft_reference.json

**Purpose:** Aircraft registration and DOW/DOI data

**Structure:**

```json
{
  "dow_options": [
    {
      "reg": "PH-BVA",
      "dow_weight_kg": 170200,
      "doi": 45.3
    },
    {
      "reg": "PH-BVB",
      "dow_weight_kg": 171500,
      "doi": 46.8
    }
    // ... more aircraft
  ]
}
```

**Source:** Aircraft-specific Weight & Balance Report (from manufacturer)

### File 5: limits.json

**Purpose:** Certified weight limits

**Structure:**

```json
{
  "MZFW_kg": 237682,
  "MTOW_kg": 351534,
  "MTW_kg": 352441,
  "MFW_kg": 167829,
  "MLW_kg": 251290
}
```

**What these mean:**
- **MZFW**: Maximum Zero Fuel Weight (structural limit)
- **MTOW**: Maximum Takeoff Weight (performance limit)
- **MTW**: Maximum Taxi Weight (ground operations)
- **MFW**: Minimum Flight Weight (usually empty + crew)
- **MLW**: Maximum Landing Weight (structural limit)

**Source:** Boeing WBCLM, Limitations Section

---

## 14. How Everything Works Together

### The Complete Flow - From Click to Graph

Let's trace what happens when a user clicks a seat:

**User Action: Click seat 10A**

```
Step 1: User Interface (passengers_module.py)
----------------------------------------
- Button 10A clicked
- toggle_seat(10, "A") called
- Add (10, "A") to self.selected set
- Change button color to green
- Call self._trigger_callback()

Step 2: Callback Debouncing (main_app.py)
----------------------------------------
- on_load_change() called
- Cancel any pending update
- Schedule update in 150ms
- (If user clicks more seats, keep rescheduling)

Step 3: After 150ms - Start Calculation
----------------------------------------
- _process_load_change() runs
- Calls calculate_aircraft_summary(update_plot=True)

Step 4: Collect All Loads
----------------------------------------
- Get passengers: seat_module.get_passenger_cg()
  → Returns (total_weight, total_moment, cg)
  
- Get cargo: cargo_module.get_cargo_cg()
  → Returns (total_weight, total_moment, cg)
  
- Get fuel: fuel_module.get_fuel_cg()
  → Returns (total_weight, total_moment, cg)

Step 5: Calculate Sequential Loading
----------------------------------------
- Point 1 (DOW): From aircraft_reference.json
  - Weight: 170200 kg
  - Arm: 1252.48 in (from DOI)
  - %MAC: 28.0%

- Point 2 (DOW + Pax): Add passenger load
  - Weight: 170200 + 39913.5 = 210113.5 kg
  - Moment: DOW_moment + Pax_moment
  - CG: Total_moment / Total_weight
  - %MAC: 29.4%

- Point 3 (ZFW): Add cargo load
  - Weight: 210113.5 + 26890 = 237003.5 kg
  - CG: Recalculate
  - %MAC: 31.7%

- Point 4 (TOW): Add fuel load
  - Weight: 237003.5 + 91856.9 = 328860.4 kg
  - CG: Recalculate
  - %MAC: 32.7%

Step 6: Update Live Plot (live_cg_plot.py)
----------------------------------------
- update_full_trace([4 points])
- Acquire thread lock
- Update line 1 (orange): DOW → DOW+Pax
- Update line 2 (green): DOW+Pax → ZFW
- Update line 3 (blue): ZFW → TOW
- Update scatter points
- Redraw canvas
- Release lock

Step 7: Check Limits (calculations.py)
----------------------------------------
- check_limits(ZFW, TOW, limits)
- Compare against MZFW, MTOW, etc.
- Return list of warnings (empty if OK)

Step 8: Display Summary (main_app.py)
----------------------------------------
- Build summary string with all values
- Include KLM indices
- Add limit warnings (if any)
- Update text box in UI

Step 9: Complete
----------------------------------------
- User sees updated graph (0.15 seconds after click)
- User sees updated summary text
- System ready for next input
```

**Total time:** ~0.15-0.20 seconds from click to displayed result

---

### Data Flow Diagram

```
┌──────────────────┐
│   User Input     │
│  (Click seat)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Passenger Module │──┐
│  Updates state   │  │
└──────────────────┘  │
                      │
┌──────────────────┐  │
│   Cargo Module   │──┤ All modules
│  (unchanged)     │  │ notify main app
└──────────────────┘  │
                      │
┌──────────────────┐  │
│   Fuel Module    │──┘
│  (unchanged)     │
└──────────────────┘
         │
         ▼
┌──────────────────────────┐
│      Main App            │
│  Collects all loads      │
│  Performs calculations   │
└────────┬─────────────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌──────────────────┐
│  Live CG Plot   │    │  Summary Display │
│  Updates graph  │    │  Updates text    │
└─────────────────┘    └──────────────────┘
```

---

## 15. Installation & Setup Guide

### System Requirements

**Operating System:**
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, or equivalent)

**Python:**
- Python 3.8 or newer
- (Python 3.10+ recommended)

**Disk Space:**
- ~50 MB for program and data files

### Step 1: Install Python

**Windows:**
1. Download from [python.org](https://python.org)
2. Run installer
3. ✅ CHECK "Add Python to PATH"
4. Click "Install Now"

**macOS:**

```bash
# Using Homebrew
brew install python3
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-tk

# Fedora
sudo dnf install python3 python3-pip python3-tkinter
```

### Step 2: Install Required Libraries

Open terminal/command prompt and run:

```bash
pip install matplotlib numpy
```

**What these are:**
- **matplotlib**: For plotting graphs
- **numpy**: For numerical operations
- **tkinter**: Usually included with Python

**Verify installation:**

```bash
python -c "import matplotlib, numpy, tkinter; print('All libraries OK!')"
```

### Step 3: Download the Program

**Option A: From GitHub**

```bash
git clone https://github.com/yourusername/b777-loading-system.git
cd b777-loading-system
```

**Option B: From ZIP file**
1. Download ZIP
2. Extract to a folder
3. Open terminal in that folder

### Step 4: Verify File Structure

Make sure you have:

```
project_folder/
├── main_app.py
├── src/
│   ├── config.py
│   ├── calculations.py
│   ├── app_utils.py
│   └── live_cg_plot.py
├── modules/
│   ├── passengers_module.py
│   ├── cargo_module.py
│   └── fuel_load_module.py
└── data/

## 16. User Guide - How to Use the System {#16-user-guide}

### Basic Workflow

**Goal:** Plan a load for flight AMS → ICN

---

### Step 1: Select Aircraft

```
Top bar: [Select Aircraft: PH-BVA ▼]
```

- Click dropdown
- Choose your aircraft registration
- Each has its own DOW and DOI

---

### Step 2: Load Passengers

**Click "Passengers" tab**

**Option A: Select individual seats**
- Click any seat to select (turns green)
- Click again to deselect (turns white/blue)

**Option B: Select entire rows**
- Click "Select Row" button next to row
- All seats in that row turn green

**Option C: Bulk selection**
- "Select All" → All 425 seats selected
- "Deselect All" → Clear everything
- "Select Row" (bottom) → Enter row number
- "Select Seat Letter" → Enter letter (e.g., "A")

**Tips:**
- Business class rows: 1-6 (light blue)
- Economy rows: 10-48 (white)
- Grey gaps = aisles
- Empty spaces = emergency exits (no seats)

---

### Step 3: Load Cargo

**Click "Cargo" tab**

**For each cargo position:**

1. **Load Maximum:**
   - Click "Load Max"
   - Position loads its maximum ULD weight
   - Button turns green, shows weight

2. **Custom Weight:**
   - Click "Custom Load"
   - Enter weight in dialog
   - System enforces maximum

3. **Quick Toggle:**
   - Click "Select/Deselect" button
   - Toggles between max and empty

**Special buttons:**
- "Load Max to All" → Loads all containers (not pallets)
- "Deselect All" → Clears everything

**Understanding Blocking:**
```
If you load a pallet (e.g., 1P):
  → Containers below it (11R, 12R) show "Blocked"
  → Cannot load those containers

If you load containers first:
  → Pallet above shows "Blocked"
  → Must unload containers to load pallet
```

---

### Step 4: Load Fuel

**Click "Fuel" tab**

**For each tank:**

1. **Set Liters:**
   - Click "Set Liters"
   - Enter amount in dialog
   - System shows arm and weight

2. **Load Maximum:**
   - Click "Load Max"
   - Tank fills to capacity

**The display shows:**
```
Main Tank 1
Max: 39000 L / 33177 kg
[Entry field: 25000]
[Set Liters] [Load Max]
Arm: 1232.50 in
Weight: 21267.5 kg
```

**Special features:**
- "Set Fuel Density" → Adjust for temperature
- "Deselect All" → Empty all tanks

**Note:** When both main tanks have fuel, system automatically uses the combined table for better accuracy.

---

### Step 5: Review Summary

**Right panel shows:**
```
------ 777-300ER Aircraft Load Summary ------

Operating (DOW):     170200.0 kg   @ 1252.48 in (%MAC: 28.00)
Passengers:          39913.5 kg   Moment: 51144327.0
Cargo:               26890.0 kg   Moment: 38634511.1
Fuel:                91856.9 kg   Moment: 121649624.7

ZERO FUEL WEIGHT:    237003.5 kg   ZFW CG: 1276.8 in (%MAC: 31.74)
TAKEOFF WEIGHT:      328860.4 kg   TOW CG: 1290.2 in (%MAC: 32.73)

KLM INDEX (CGI) [ref 1258 in]:
  ZFW Index:         57.04
  TOW Index:         87.60

✅ All gross weight limits within certified ranges.
```

---

### Step 6: Check the Live Plot

**The live plot window shows:**
- Grey envelope = certified safe zone
- Dark grey area = restricted (not recommended)
- Orange line = passenger loading
- Green line = cargo loading
- Blue line = fuel loading
- Red dot = ZFW (Zero Fuel Weight)
- Blue dot = TOW (Takeoff Weight)

**What to look for:**
- ✅ All points inside grey area → SAFE
- ❌ Any point outside grey area → UNSAFE
- ⚠️ Points in dark grey area → Legal but not recommended

---

### Step 7: Generate Static Chart

**For documentation/printing:**

1. Click "Show CG Envelope Chart"
2. New window opens with static chart
3. Shows only final ZFW and TOW points
4. Can be saved using matplotlib toolbar

---

### Common Scenarios

**Scenario 1: Full passenger flight**
```
1. Select Aircraft
2. Passengers → Select All
3. Cargo → Load what fits
4. Fuel → Load for range
5. Check limits
```

**Scenario 2: Cargo-only flight**
```
1. Select Aircraft
2. Passengers → Leave empty
3. Cargo → Load Max to All
4. Fuel → Load for range
5. Check if MZFW exceeded
```

**Scenario 3: Finding maximum cargo**
```
1. Select Aircraft
2. Load passengers
3. Check ZFW remaining: MZFW - current weight
4. Load cargo up to that limit
5. Iterate until at limit
```

---

## 17. Developer Guide - How to Modify {#17-developer-guide}

### Adding a New Aircraft Type

**What you need:**
1. Boeing WBCLM for that aircraft
2. Empty weight and DOI from W&B report
3. Seat map configuration
4. Cargo bay layout
5. Fuel tank capacities and arm tables

**Steps:**

**1. Add aircraft to aircraft_reference.json**
```json
{
  "dow_options": [
    // ... existing aircraft
    {
      "reg": "PH-NEW",
      "dow_weight_kg": 165000,
      "doi": 42.8
    }
  ]
}
```

**2. Create new seat map (if configuration differs)**
- Copy seat_map_new.json
- Modify for new layout
- Update seat positions and arms
- Save as seat_map_new_config2.json

**3. Update config.py paths (if needed)**
```python
SEAT_MAP_FILEPATH = "data/seat_map_new_config2.json"
```

**4. Update limits.json (if different variant)**
```json
{
  "MZFW_kg": 240000,  // Different for -300ER vs standard -300
  "MTOW_kg": 348000,
  // ... etc
}
```

**5. Test thoroughly**
- Verify DOW calculation
- Check seat arms
- Validate cargo positions
- Test fuel interpolation

---

### Adding a New Feature

**Example: Add trip fuel calculation for landing weight**

**1. Add UI input (main_app.py)**
```python
# In build_config_ui():
tk.Label(self.config_tab, text="Trip Fuel (kg)").grid(...)
self.trip_fuel_var = tk.DoubleVar(value=0)
tk.Entry(self.config_tab, textvariable=self.trip_fuel_var).grid(...)
```

**2. Add calculation (main_app.py)**
```python
# In calculate_aircraft_summary():
trip_fuel = self.trip_fuel_var.get()
lw_weight = tow_weight - trip_fuel
lw_moment = tow_moment - (trip_fuel * fuel_cg)
lw_cg = lw_moment / lw_weight if lw_weight > 0 else tow_cg
lw_mac = calc.calculate_mac_percent(lw_cg, ...)
```

**3. Update plot (live_cg_plot.py)**
```python
# Add new scatter for LW
self.scatter_lw = self.ax.scatter(
    [], [], color='purple', marker='o', s=120, label='LW CG'
)

# In update_full_trace():
# Accept 5 points instead of 4
p_lw = trace_points[4]
self.scatter_lw.set_offsets(np.array([p_lw]))
```

**4. Update summary text**
```python
summary_str += f"LANDING WEIGHT:      {lw_weight:.1f} kg   "
summary_str += f"LW CG: {lw_cg:.2f} in (%MAC: {lw_mac:.2f})\n"
```

---

### Debugging Tips

**Problem: Calculations seem wrong**

**Check:**
```python
# Add debug prints in calculate_aircraft_summary()
print(f"DOW: {dow_weight} kg @ {dow_arm} in")
print(f"Pax: {pax_weight} kg @ {pax_cg} in")
print(f"Total moment: {total_moment}")
print(f"Total weight: {total_weight}")
print(f"CG: {total_moment / total_weight if total_weight > 0 else 0}")
```

**Problem: Module not updating**

**Check callbacks:**
```python
# In module __init__:
print(f"Callback registered: {self.on_change_callback is not None}")

# When state changes:
print(f"Triggering callback...")
self._trigger_callback()
```

**Problem: Plot not showing**

**Check matplotlib backend:**
```python
import matplotlib
print(f"Backend: {matplotlib.get_backend()}")
# Should be 'TkAgg' for tkinter integration
```

---

### Code Style Guidelines

**1. Naming conventions**
```python
# Classes: PascalCase
class SeatSelector:

# Functions: snake_case
def calculate_mac_percent():

# Constants: UPPER_SNAKE_CASE
MAX_FUEL_KG = 154229

# Variables: snake_case
total_weight = 0
```

**2. Documentation**
```python
def function_name(arg1, arg2):
    """
    Brief description of what function does.
    
    Args:
        arg1 (type): Description
        arg2 (type): Description
    
    Returns:
        type: Description
    """
```

**3. Error handling**
```python
try:
    data = load_json_data(filepath)
except FileNotFoundError:
    messagebox.showerror("Error", f"File not found: {filepath}")
    return None
except Exception as e:
    messagebox.showerror("Error", f"Unexpected error: {e}")
    return None
```

---

## 18. Testing & Validation {#18-testing-validation}

### Unit Testing

**Testing calculations.py functions:**

```python
import unittest
from src import calculations as calc

class TestCalculations(unittest.TestCase):
    
    def test_interpolate_arm(self):
        """Test fuel arm interpolation."""
        table = [[0, 1200], [10000, 1250], [20000, 1300]]
        
        # Test exact point
        self.assertEqual(calc.interpolate_arm(table, 10000), 1250)
        
        # Test interpolation
        result = calc.interpolate_arm(table, 5000)
        self.assertAlmostEqual(result, 1225, places=1)
        
        # Test below minimum
        self.assertEqual(calc.interpolate_arm(table, -100), 1200)
        
        # Test above maximum
        self.assertEqual(calc.interpolate_arm(table, 30000), 1300)
    
    def test_calculate_mac_percent(self):
        """Test %MAC conversion."""
        # Known values from Boeing manual
        arm = 1242.28
        mac = calc.calculate_mac_percent(arm, 1174.5, 278.5)
        self.assertAlmostEqual(mac, 24.34, places=2)
    
    def test_klm_index_base(self):
        """Test KLM index calculation."""
        # Boeing certified example
        dow = 170200
        arm = 1252.48
        index = calc.klm_index_base(dow, arm, 1258, 200000, 50)
        self.assertAlmostEqual(index, 45.3, places=1)
    
    def test_check_limits(self):
        """Test limit checking."""
        limits = {
            "MZFW_kg": 237682,
            "MTOW_kg": 351534,
            "MTW_kg": 352441,
            "MFW_kg": 167829
        }
        
        # Test within limits
        warnings = calc.check_limits(230000, 340000, limits)
        self.assertEqual(len(warnings), 0)
        
        # Test exceeding MZFW
        warnings = calc.check_limits(250000, 340000, limits)
        self.assertEqual(len(warnings), 1)
        self.assertIn("MZFW", warnings[0])

if __name__ == '__main__':
    unittest.main()
```

**Run tests:**
```bash
python -m unittest test_calculations.py
```

---

### Integration Testing

**Testing the full calculation flow:**

```python
def test_full_calculation():
    """Test complete load calculation."""
    
    # Setup
    app = create_test_app()
    
    # Load known scenario
    app.seat_module.select_all()  # 425 pax
    app.cargo_module.load_max_all()  # Max cargo
    app.fuel_module.set_liters(app.fuel_module.tank_data[0], 30000)
    
    # Calculate
    app.calculate_aircraft_summary(update_plot=False)
    
    # Verify results
    assert app._last_zfw_weight > 200000  # Reasonable ZFW
    assert app._last_tow_weight > 300000  # Reasonable TOW
    assert 10 < app._last_zfw_mac < 40    # CG within envelope
    assert 10 < app._last_tow_mac < 40    # CG within envelope
```

---

### Validation Against Boeing Data

**Test case from Boeing manual:**

```
Aircraft: B777-300ER
Configuration: 35C/390M
DOW: 170,200 kg
DOI: 45.3

Test Load:
- Passengers: Full (425 pax × 88.5 kg = 37,612.5 kg)
- Cargo: 15,000 kg at arm 1,450 in
- Fuel: 80,000 kg at arm 1,280 in

Expected Results (from Boeing):
ZFW: 222,812.5 kg at 30.2% MAC
TOW: 302,812.5 kg at 31.8% MAC
```

**Run test:**
```python
def test_boeing_example():
    # Calculate with our system
    zfw_mac, zfw_weight, tow_mac, tow_weight = run_scenario(
        pax_count=425,
        cargo_weight=15000,
        cargo_arm=1450,
        fuel_weight=80000,
        fuel_arm=1280
    )
    
    # Compare to Boeing
    assert abs(zfw_weight - 222812.5) < 100  # Within 100 kg
    assert abs(zfw_mac - 30.2) < 0.5         # Within 0.5% MAC
    assert abs(tow_weight - 302812.5) < 100
    assert abs(tow_mac - 31.8) < 0.5
```

---

### User Acceptance Testing (UAT)

**Test with real load controllers:**

**Test Scenario 1: Typical Full Flight**
```
Route: AMS → ICN
Booking: 380 passengers (90% full)
Cargo: 12 tons
Fuel: 90 tons (long haul)

Questions for testers:
1. Is the seat map intuitive?
2. Is the cargo blocking logic clear?
3. Is the fuel input straightforward?
4. Is the summary readable?
5. Does the live plot help decision-making?
```

**Test Scenario 2: Cargo Flight**
```
Route: AMS → DXB
Booking: 0 passengers
Cargo: Maximum possible
Fuel: 70 tons

Questions for testers:
1. Can you find max cargo capacity quickly?
2. Are limit warnings clear?
3. Would you trust this for real operations?
```

**Collect feedback on:**
- Ease of use (1-5 scale)
- Calculation trust (1-5 scale)
- Visual clarity (1-5 scale)
- Speed/performance (1-5 scale)
- Feature requests (open-ended)

---

## 19. Troubleshooting Common Issues {#19-troubleshooting}

### Issue 1: Program Won't Start

**Error:** `ModuleNotFoundError: No module named 'tkinter'`

**Solution (Linux):**
```bash
sudo apt install python3-tk
```

**Solution (Windows):**
- Reinstall Python with "tcl/tk" option checked

---

### Issue 2: Plot Window Doesn't Open

**Error:** Plot window missing or blank

**Solution 1: Check matplotlib backend**
```python
# Add to top of main_app.py
import matplotlib
matplotlib.use('TkAgg')
```

**Solution 2: Update matplotlib**
```bash
pip install --upgrade matplotlib
```

---

### Issue 3: Calculations Seem Wrong

**Symptom:** CG values don't match manual calculations

**Debug steps:**

1. **Verify input data:**
```python
# Check loaded JSON
print(json.dumps(seat_map_data[0], indent=2))
# Verify arms match Boeing manual
```

2. **Check intermediate values:**
```python
# In calculate_aircraft_summary(), add:
print(f"Passenger total: {pax_weight} kg @ {pax_cg} in")
print(f"Expected moment: {pax_weight * pax_cg}")
print(f"Actual moment: {pax_moment}")
```

3. **Compare to hand calculation:**
```
Manual calc:
100 pax × 88.5 kg = 8850 kg
8850 kg × 1100 in = 9,735,000 kg-in

Program output:
Pax weight: 8850.0 kg
Pax moment: 9735000.0 kg-in
✅ Match!
```

---

### Issue 4: Plot Updates Slowly

**Symptom:** Lag when clicking seats/cargo

**Solution 1: Increase debounce delay**
```python
# In main_app.py, on_load_change():
self._update_after_id = self.master.after(
    300,  # Increase from 150ms to 300ms
    self._process_load_change
)
```

**Solution 2: Disable live updates**
```python
# Only update on button click
self.calculate_aircraft_summary(update_plot=False)
# User manually clicks "Update Plot" button
```

---

### Issue 5: Data File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'data/seat_map_new.json'`

**Solution:**
```bash
# Check current directory
pwd  # Linux/Mac
cd   # Windows

# Should be in project root, not in src/ or modules/
# If in wrong directory:
cd ..  # Go up one level
python main_app.py
```

---

### Issue 6: Fuel Tank CG Incorrect

**Symptom:** Fuel CG doesn't change as expected

**Check:**
1. **Verify arm table in JSON:**
```json
{
  "tank": "Main Tank 1",
  "arm_table": [
    [0, 1200.0],     // Must be sorted by liters
    [10000, 1210.5], // ✅ Increasing
    [20000, 1225.8]
  ]
}
```

2. **Test interpolation:**
```python
from src.calculations import interpolate_arm
table = [[0, 1200], [10000, 1210], [20000, 1220]]
print(interpolate_arm(table, 5000))  # Should be ~1205
```

---

### Issue 7: KLM Index Values Wrong

**Symptom:** Index values too high or don't match Boeing

**Check:**
1. **Using correct functions:**
```python
# DOW: Use klm_index_base (with +50)
klm_dow = calc.klm_index_base(dow_weight, dow_arm)

# Components: Use klm_index_component (NO +50)
klm_pax = calc.klm_index_component(pax_weight, pax_cg)
```

2. **Verify constants in config.py:**
```python
KLM_REFERENCE_ARM_IN = 1258  # ✅ Correct
KLM_SCALE = 200000           # ✅ Correct
KLM_OFFSET = 50              # ✅ Correct
```

---

## 20. Future Enhancements {#20-future-enhancements}

### Short-Term Improvements (1-3 months)

**1. Landing Weight Calculation**
- Add trip fuel input
- Calculate LW = TOW - Trip Fuel
- Plot LW on envelope
- Check MLW limit

**2. Load Optimization**
- "Find max cargo" button
- Auto-distribute cargo for optimal CG
- Suggest passenger seating for balance

**3. Export Functionality**
- Export summary as PDF
- Save load sheet
- Email to crew

**4. Multiple Configurations**
- Support different seat layouts
- Quick-switch between configs
- Config creator tool

---

### Medium-Term Features (3-6 months)

**1. Database Integration**
- Connect to airline reservation system
- Auto-load passenger counts
- Real-time cargo manifests

**2. Historical Data**
- Save previous load plans
- Compare current to historical
- Trend analysis

**3. Advanced Warnings**
- Predict tail-strike risk
- Fuel burn optimization
- Runway length requirements

**4. Multi-User Support**
- Concurrent load planning
- Approval workflow
- Audit trail

---

### Long-Term Vision (6-12 months)

**1. Fleet Management**
- Multiple aircraft types in one system
- Fleet-wide optimization
- Maintenance integration

**2. Machine Learning**
- Predict no-shows
- Optimize cargo distribution
- Learn from past loads

**3. Mobile App**
- Tablet interface for ground crew
- Real-time updates
- Offline capability

**4. Certification**
- Work toward airline certification
- EASA approval process
- Production deployment

---

### Community Contributions

**How to contribute:**

1. **Report bugs:**
   - Open issue on GitHub
   - Include error message
   - Provide steps to reproduce

2. **Suggest features:**
   - Describe use case
   - Explain benefit
   - Propose implementation

3. **Submit code:**
   - Fork repository
   - Create feature branch
   - Submit pull request
   - Include tests

**Areas needing help:**
- Additional aircraft types (B787, A350)
- UI/UX improvements
- Documentation translation
- Performance optimization
- Test coverage

---

## Conclusion

This documentation has covered the complete B777-300ER Visual Loading System from first principles to advanced development.

**What you've learned:**
- ✅ Why weight and balance matters
- ✅ How the physics works
- ✅ How the system is architected
- ✅ How every module functions
- ✅ How to use the system
- ✅ How to modify and extend it

**Key takeaways:**
1. **Modular design** = Easy to maintain and expand
2. **Data-driven** = No code changes for new aircraft
3. **Real-time feedback** = Better user experience
4. **Thread-safe** = Reliable performance
5. **Well-documented** = Anyone can understand it

**Next steps:**
- Run the system and experiment
- Try the test cases
- Read the code alongside this doc
- Start making improvements
- Share your experience

---

**Questions or need help?**
- Email: XXXXXXXXXXXXXXX
- GitHub: [Repository URL]
- Documentation version: 2.0
- Last updated: November 2025

---

**Thank you for reading this documentation!**

Whether you're a pilot, engineer, developer, or student, I hope this guide has given you a complete understanding of the system. Safe flying! ✈️

---

## Appendix A: Quick Reference

### Key Formulas

```
Moment = Weight × Arm

CG = Σ(Moments) / Σ(Weights)

%MAC = ((Arm - LEMAC) / MAC_length) × 100

KLM Index (Base) = (Weight × (Arm - 1258)) / 200000 + 50

KLM Index (Component) = (Weight × (Arm - 1258)) / 200000
```

### Key Constants

```
LEMAC = 1174.5 inches
MAC Length = 278.5 inches
KLM Reference Arm = 1258 inches
Default Passenger Weight = 88.5 kg
Default Fuel Density = 0.8507 kg/L
MZFW = 237,682 kg
MTOW = 351,534 kg
```

### File Locations

```
Main program: main_app.py
Calculations: src/calculations.py
Configuration: src/config.py
Seat data: data/seat_map_new.json
Cargo data: data/cargo_positions.json
Fuel data: data/fuel_tanks.json
Limits: data/limits.json
```

---

**END OF DOCUMENTATION**
