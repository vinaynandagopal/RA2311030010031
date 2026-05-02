# Campus Hiring Evaluation - Backend Track

## Repository Structure

- logging_middleware/ — Pre-test: Reusable logging middleware
- vehicle_scheduling/ — Q1: Vehicle Maintenance Scheduler
- notification_app_be/ — Q2: Campus Notifications Backend
- notification_system_design.md — Q2: Design document of all the 6 stages

## Tech Stack
- Language: Python
- Track: Backend

## Pre-Test Setup
Logging middleware built as a reusable Log(stack, level, package, message) function.
Every API call in the codebase uses this middleware for logging.

## Question 1 - Vehicle Maintenance Scheduler
It fetches depot and vehicle data from the evaluation server.
I used a Knapsack algorithm to find the optimal set of vehicles.
Maximises total impact score within available mechanic hours per depot.

## Question 2 - Campus Notifications System
- Stage 1: REST API design with WebSocket real-time mechanism
- Stage 2: PostgreSQL schema, queries and scaling solutions
- Stage 3: Query optimization and indexing strategy
- Stage 4: Redis caching to reduce DB load
- Stage 5: Reliable async notification system redesign
- Stage 6: Priority inbox using Min-Heap (Placement > Result > Event is the priority)
