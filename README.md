CPU X-Ray Simulator 🖥️
The CPU X-Ray Simulator is an interactive, web-based educational tool engineered to visualize the internal mechanics of a modern processor. Built in Python using the Streamlit framework, this project transforms abstract Computer Architecture concepts into a dynamic, real-time dashboard.

It is designed to bridge the gap between software and physical silicon, allowing users to visually analyze Cycles Per Instruction (CPI), memory bottlenecks, and pipeline traffic jams.

🚀 Key Features
5-Stage RISC Pipeline: Visually tracks instructions as they move through Fetch (IF), Decode (ID), Execute (EX), Memory (MEM), and Writeback (WB) stages.

Hierarchical Memory Subsystem: Enforces realistic data locality with an ultra-fast L1 Cache, a secondary L2 Cache, and main RAM. Watch cache hits and misses happen in real-time.

Hazard Detection Unit: Actively monitors for branch prediction penalties. When the CPU mispredicts a loop path, it flushes the pipeline and increments the hazard counter.

Visual Code Builder: Write and compile custom assembly-style instructions (LOAD, STORE, ADD, BNE, SET) directly in the browser.

Cycle-by-Cycle Execution: Step through code one clock cycle at a time or use Auto-Play to watch the simulated hardware run at speed.

🛠️ Tech Stack
Backend Engine: Python (State-machine logic, CPU memory management, parsing)

Frontend Interface: Streamlit (Web deployment, UI/UX, live metrics)
💻 How to Run Locally
Clone the repository:

Bash
git clone https://github.com/soumyajitssyash-cmyk/CPU-XRay-Simulator.git
cd CPU-XRay-Simulator
Install the required dependencies:

Bash
pip install -r requirements.txt
Try the "Stress Test" Program
To see all features in action (Math, Memory Caching, and Branch Hazards), paste this exact code into the Visual Code Builder:
SET R1, 0
SET R2, 3
LOOP:
ADD R1, R1, 1
STORE R1, 100
BNE R1, R2, LOOP
LOAD R3, 100
LOAD R4, 100


What happens when you run this?

The CPU loops three times, storing data to RAM and the L1 Cache.

The BNE branch command triggers a Pipeline Flush (Hazard) because the CPU guesses the execution path incorrectly.

The final two LOAD commands trigger instant L1 Cache Hits, demonstrating how the processor saves time by not checking RAM.

👨‍💻 Author
Soumyajit Saha
