# SmartLabOS

**An educational operating system simulator for demonstrating process scheduling, memory allocation, and performance analytics.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-HTTP%20layer-009688?logo=fastapi&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?logo=javascript&logoColor=black)
![Tests](https://img.shields.io/badge/Tests-pytest%2022%20passing-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

SmartLabOS is a web-based operating system simulator designed for educational purposes. It provides a clean, interactive environment to understand and visualize how operating systems manage processes, allocate memory, and schedule CPU time. Built for a college OS course, it demonstrates three core OS modules:

1. **Process Management & Scheduling** — Four scheduling algorithms (FCFS, SJF, Priority, Round Robin) with a deterministic simulation clock
2. **Physical Memory Management** — Fixed-size block allocation with First-Fit, Best-Fit, and Worst-Fit strategies
3. **Performance Analytics** — Per-process and system-wide metrics with algorithm comparison tools

The simulator runs entirely in your browser with a Python backend, featuring real-time updates, Gantt charts, memory visualizations, and comprehensive metrics.

---

## Features

### Module 1: Process Scheduling

- **Process Control Blocks (PCB)** with five states: New, Ready, Running, Waiting, and Completed
- **Four scheduling algorithms:**
  - **FCFS (First-Come, First-Served)** — Non-preemptive; processes run in arrival order
  - **SJF (Shortest Job First)** — Non-preemptive; shortest burst time first
  - **Priority (Non-preemptive)** — Lower priority number = higher priority
  - **Round Robin** — Preemptive with configurable quantum (time slice)
- **Deterministic simulation clock** with Start, Pause, Step, and Reset controls
- **Real-time Gantt chart** generated from actual execution trace
- **Process creation form** with name, arrival time, burst time, priority, and memory size fields
- **Demo workload button** to load sample processes for testing

### Module 2: Physical Memory

- **Fixed-size block allocation** — Memory divided into uniform blocks (configurable size)
- **Three allocation strategies:**
  - **First-Fit** — Allocate in the first hole that fits
  - **Best-Fit** — Allocate in the smallest hole that fits
  - **Worst-Fit** — Allocate in the largest hole available
- **Visual block map** showing allocated and free memory
- **Fragmentation metrics:**
  - **Internal fragmentation** — Wasted space within allocated blocks
  - **External fragmentation** — Free space split into non-contiguous holes
- **Memory admission control** — Processes wait if memory is insufficient
- **OS-reserved memory** — Configurable OS kernel reservation

### Module 3: Performance Analytics

- **Per-process metrics:**
  - **Waiting time** — Time spent in Ready queue
  - **Turnaround time** — Total time from arrival to completion
  - **Response time** — Time from arrival to first CPU dispatch
- **System-wide metrics:**
  - **Average waiting/turnaround/response times**
  - **Throughput** — Processes completed per unit time
  - **CPU utilization** — Percentage of time CPU is busy
  - **Context switches** — Number of process switches
- **Algorithm comparison tool:**
  - Runs the same workload under all four schedulers
  - Side-by-side results with charts
  - Compares memory strategies using classic textbook example
  - CSV export for analysis

### Optional Extension: I/O Simulation

- **Single I/O device** (Disk) with blocking queue
- **DMA model** — CPU continues with other processes while I/O executes
- Processes transition to **Waiting** state during I/O, return to **Ready** when complete

---

## Architecture

SmartLabOS follows a clean layered architecture with a pure Python core, a thin FastAPI HTTP layer, and a no-build vanilla JavaScript frontend.

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (UI)                        │
│  HTML + CSS + Vanilla JS (no build step)               │
│  • Process table  • Gantt chart  • Memory map          │
│  • Metrics panel  • Event log    • Controls            │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP / Server-Sent Events
┌────────────────┴────────────────────────────────────────┐
│              FastAPI (HTTP Layer)                       │
│  • Control endpoints  • Config endpoints               │
│  • SSE state stream   • Comparison API                 │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│         SimulationManager (Async Boundary)              │
│  • asyncio.Lock   • Play/Pause loop                    │
│  • SSE fan-out    • Snapshot publisher                 │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│            Core Engine (Pure Python)                    │
│  so_sim/core/ — Framework-free, fully unit-tested      │
│                                                          │
│  • world.py       — Orchestrator, tick pipeline        │
│  • scheduler/     — FCFS, SJF, Priority, RR            │
│  • dispatcher.py  — Context switch execution           │
│  • memfisica/     — Physical memory + strategies       │
│  • pcb.py         — Process control blocks             │
│  • metrics.py     — Performance calculations           │
│  • comparativa.py — Algorithm comparison engine        │
└──────────────────────────────────────────────────────────┘
```

**Design rationale:** The core has zero dependencies on FastAPI, so it can be tested in complete isolation with pytest. The web layer only marshals commands and streams snapshots; the client re-renders idempotently from each snapshot, so there's no hidden state to drift out of sync.

---

## Scheduling Algorithms

### 1. FCFS (First-Come, First-Served)

**Non-preemptive.** Processes run to completion in order of arrival. The first process to enter the Ready queue is the first to execute.

**Formula:** No preemption; processes run until burst completes.

**Pros:** Simple, fair in arrival order  
**Cons:** Long average waiting time if a long process arrives first (convoy effect)

### 2. SJF (Shortest Job First)

**Non-preemptive.** When the CPU becomes free, select the process with the shortest remaining burst time from the Ready queue.

**Formula:** Select `min(burst_time)` among ready processes.

**Pros:** Minimizes average waiting time (provably optimal for non-preemptive)  
**Cons:** Long processes may starve; requires knowing burst times in advance

### 3. Priority (Non-Preemptive)

**Non-preemptive.** Processes are assigned a priority number (lower = higher priority). When the CPU is free, the highest-priority ready process runs to completion.

**Formula:** Select `min(priority)` among ready processes.

**Pros:** Important processes run first  
**Cons:** Low-priority processes may starve; priority inversion possible

### 4. Round Robin

**Preemptive.** Each process gets a fixed time slice (quantum). If the process doesn't complete within its quantum, it's moved to the end of the Ready queue and the next process runs.

**Formula:** Run for `min(quantum, burst_remaining)` ticks, then context switch.

**Pros:** Fair time-sharing, good response time for interactive processes  
**Cons:** Higher average turnaround than SJF; performance depends on quantum choice

---

## Memory Allocation Strategies

All three strategies manage a memory space divided into **fixed-size blocks**. When a process arrives, the system calculates how many blocks it needs (rounding up) and searches for a contiguous hole.

### 1. First-Fit

**Strategy:** Scan the memory map from the beginning and allocate in the **first hole** large enough to fit the process.

**Pros:** Fast (stops at first fit)  
**Cons:** Can fragment memory at the beginning, leaving small unusable holes

### 2. Best-Fit

**Strategy:** Scan the entire memory map and allocate in the **smallest hole** that fits the process.

**Pros:** Minimizes wasted space in large holes  
**Cons:** Leaves many tiny holes (high external fragmentation); slower (must scan all holes)

### 3. Worst-Fit

**Strategy:** Scan the entire memory map and allocate in the **largest hole** available.

**Pros:** Leaves larger leftover holes (potentially useful for future allocations)  
**Cons:** Wastes large holes on small processes; slower; often performs poorly in practice

---

## Performance Metrics

### Per-Process Metrics

- **Turnaround Time** = (Completion Time) - (Arrival Time)  
  _Total time from process arrival to completion_

- **Waiting Time** = (Turnaround Time) - (Burst Time)  
  _Time spent in the Ready queue waiting for CPU_

- **Response Time** = (First Dispatch Time) - (Arrival Time)  
  _Time from arrival until the process first gets the CPU_

### System Metrics

- **Average Waiting Time** = Σ(Waiting Time) / N
- **Average Turnaround Time** = Σ(Turnaround Time) / N
- **Average Response Time** = Σ(Response Time) / N
- **Throughput** = (Processes Completed) / (Total Simulation Time)
- **CPU Utilization** = (CPU Busy Ticks) / (Total Ticks) × 100%
- **Context Switches** = Number of times the CPU switched between processes

### Context Switch Counting Rule

A context switch occurs when the CPU dispatcher moves from one process to another. We count:
- Process A to Process B: **1 context switch**
- Idle to Process A: No context switch (initial dispatch)
- Process A to Idle: No context switch (completion)

The context switch cost (configurable) is the number of ticks the dispatcher spends performing the switch (saving/loading registers, etc.).

---

## Installation & Running

### Prerequisites

- **Python 3.10 or newer**
- **pip** (Python package manager)

### Quick Start

1. **Clone or download the repository**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Start the server**

```bash
python -m uvicorn so_sim.app:app --host 0.0.0.0 --port 8000
```

4. **Open your browser** at `http://localhost:8000`

### Running Tests

SmartLabOS includes 22 comprehensive unit tests covering all four schedulers and memory strategies.

```bash
# Run all tests
python -m pytest

# Run scheduler tests only
python -m pytest tests/test_smartlabos_schedulers.py -v

# Run memory tests only
python -m pytest tests/test_smartlabos_memory.py -v
```

All tests use hand-worked expected results to verify correctness of scheduling order, metric calculations, and memory allocation decisions.

---

## Usage Guide

### 1. Load a Scenario

- Click **"Load demo workload"** to load 8 sample processes
- Or select a preset from the **Scenario** dropdown (Basic, Round Robin, Priority, I/O Overlap)
- Or click **"Create process"** to define your own workload

### 2. Configure Settings

- **Scheduler:** Choose FCFS, SJF, Priority, or Round Robin
- **Quantum:** Set time slice for Round Robin (1-20 ticks)
- **Memory Strategy:** Choose First-Fit, Best-Fit, or Worst-Fit
- **Speed:** Adjust simulation speed (50-2000 ms per tick)

### 3. Run the Simulation

- **▶ Play** — Run continuously at the configured speed
- **⏸ Pause** — Stop execution
- **⏭ Step** — Execute one tick at a time
- **⟲ Reset** — Restart from the beginning

### 4. Observe Execution

- **Process Table** shows each process's state, progress, priority, and memory address
- **Gantt Chart** displays the CPU schedule over time (which process ran each tick)
- **Memory Map** visualizes allocated and free blocks with fragmentation metrics
- **Metrics Panel** updates live with waiting times, turnaround, CPU utilization, etc.
- **Event Log** records every state transition, admission, dispatch, I/O, and completion

### 5. Compare Algorithms

Click **"Algorithm Comparison"** to run the current workload under all four schedulers and three memory strategies, displaying side-by-side results with charts. Export to CSV for further analysis.

---

## Project Structure

```
smartlabos/
├── so_sim/
│   ├── core/                  # Pure Python engine (no framework)
│   │   ├── world.py           # Simulation orchestrator
│   │   ├── pcb.py             # Process control block
│   │   ├── dispatcher.py      # Context switch handler
│   │   ├── scheduler/         # FCFS, SJF, Priority, RR
│   │   │   ├── __init__.py    # Scheduler factory
│   │   │   ├── base.py        # Scheduler interface
│   │   │   ├── fcfs.py
│   │   │   ├── sjf.py
│   │   │   ├── priority.py
│   │   │   └── round_robin.py
│   │   ├── memfisica/         # Physical memory module
│   │   │   ├── memoria.py     # Bitmap-based memory manager
│   │   │   └── estrategias.py # First/Best/Worst-Fit
│   │   ├── metrics.py         # Performance calculations
│   │   ├── comparativa.py     # Algorithm comparison
│   │   ├── enums.py           # State/event enumerations
│   │   └── config.py          # Configuration dataclass
│   ├── manager.py             # SimulationManager (async boundary)
│   ├── app.py                 # FastAPI application
│   ├── api/                   # HTTP routers
│   │   ├── routes_control.py  # Play/pause/step/reset
│   │   ├── routes_state.py    # SSE state stream
│   │   └── routes_config.py   # Load/compare endpoints
│   ├── scenarios/             # Demo workloads
│   │   └── presets.py
│   └── static/                # Frontend (no build)
│       ├── index.html
│       ├── css/styles.css
│       └── js/                # ES modules
│           ├── main.js
│           ├── controls.js
│           ├── render_*.js    # Idempotent panel renderers
│           └── api.js
├── tests/                     # pytest suite (22 tests)
│   ├── test_smartlabos_schedulers.py  # 11 scheduler tests
│   ├── test_smartlabos_memory.py      # 11 memory tests
│   └── helpers.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Algorithm Comparison Example

The comparison tool runs a **classic textbook scenario** to differentiate memory strategies:

1. Allocate Process 1 (4 blocks) at blocks 0-3
2. Allocate Process 2 (1 block) at block 4 (separator)
3. Allocate Process 3 (6 blocks) at blocks 5-10
4. Free Process 1 → hole of 4 blocks at 0-3
5. Free Process 3 → hole of 6 blocks at 5-10
6. Allocate Process 4 (3 blocks)
7. Allocate Process 5 (6 blocks)

**Results:**
- **First-Fit:** Uses first hole (4 blocks) for P4 → P5 fits in 6-block hole ✓
- **Best-Fit:** Uses 4-block hole (smallest fit) for P4 → P5 fits in 6-block hole ✓
- **Worst-Fit:** Uses 6-block hole (largest) for P4 → P5 fails (only 4-block hole left) ✗

This demonstrates how Worst-Fit can waste large holes on small allocations, causing external fragmentation failures that First/Best-Fit avoid.

---

## Deployment

SmartLabOS is deployed on **Render** with the following configuration:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn so_sim.app:app --host 0.0.0.0 --port $PORT`

The application binds to `0.0.0.0:$PORT` as required by Render. The filesystem is ephemeral (no persistent writes), which is fine since all state is in-memory simulation.

---

## Acknowledgments

This project is built upon the excellent foundation of **[os-simulator](https://github.com/mazk36/os-simulator)** by Marcelo Jáuregui (mazk36), originally created as a university OS course project. SmartLabOS simplifies and adapts that codebase to focus on the core educational modules (process scheduling, physical memory, and performance analytics) required for our college assignment.

**Original project features** included virtual memory/paging, additional schedulers (SRTF, preemptive priority, MLQ), and interactive keyboard interrupts. SmartLabOS removes these to maintain clarity and match the course specification.

**Changes made for SmartLabOS:**
- Reduced to 4 required schedulers (FCFS, SJF, non-preemptive Priority, Round Robin)
- Focused on physical memory allocation (removed virtual memory/paging module)
- Added comprehensive pytest test suite with hand-worked expected results
- Rebranded UI and simplified controls
- Rewrote documentation for educational clarity
- Streamlined demo workloads for classroom use

We are grateful to Marcelo for releasing the original simulator under the MIT License, enabling this educational adaptation.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Marcelo Jáuregui (original os-simulator)
Copyright (c) 2024 SmartLabOS contributors (educational adaptation)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Contributing

This is an educational project for a college assignment. If you're using SmartLabOS in your own course, feel free to fork and adapt it to your needs!

For questions or issues, please check the original [os-simulator](https://github.com/mazk36/os-simulator) repository or open an issue in this repository.

---

**Built with ❤️ for OS education**
