# Smart AI-Based Traffic Management using Multi-Agent Reinforcement Learning

An intelligent traffic optimization system that uses **Multi-Agent Reinforcement Learning (MARL)**, **LSTM traffic prediction**, and **SUMO simulation** to dynamically control urban traffic signals, reduce congestion, and improve traffic throughput.  
Developed as a research-driven project focused on scalable smart city traffic control. :contentReference[oaicite:0]{index=0}

---

## Problem Statement

Traditional fixed-time traffic signals cannot adapt to real-time congestion, causing:

- Long vehicle waiting times  
- Increased queue lengths  
- Fuel wastage and emissions  
- Poor intersection coordination  
- Delayed emergency vehicle movement  

This project solves this by enabling **traffic lights to act as intelligent learning agents** that adapt signal timings in real time. :contentReference[oaicite:1]{index=1}

---

# Proposed Solution

This system combines:

### 1. Traffic Flow Prediction (LSTM)
- Predicts dynamic vehicle arrivals
- Simulates realistic traffic demand
- Supports proactive signal control

### 2. Multi-Agent Reinforcement Learning (MARL)
Each intersection acts as an autonomous RL agent that learns optimal signaling based on:

- Queue Length
- Waiting Time
- Traffic Density
- Emergency Vehicle Presence

Agents coordinate to optimize city-wide flow.

### 3. SUMO Simulation + TraCI
- Realistic urban traffic simulation
- Real-time traffic light control
- Agent-environment interaction

### 4. Emergency Vehicle Prioritization
- Dynamic signal adaptation for emergency clearance
- Priority routing logic

---
# Cybersecurity Layer (Novel Contribution)

Beyond traffic optimization, the project incorporates a cybersecurity layer to secure intelligent transportation infrastructure from malicious attacks.

## Security Challenges Addressed
Modern smart traffic systems are vulnerable to:

- Man-in-the-Middle (MITM) attacks on signal communication
- Signal spoofing / false traffic data injection
- Compromised agent-to-agent communication
- Replay attacks on signal phase commands
- Emergency vehicle priority abuse
- Traffic infrastructure cyber sabotage

---

## Security Architecture

### Secure Multi-Agent Communication
Protected communication between traffic control agents using:

- TLS 1.3 encrypted channels
- Digital Signatures for authentication
- SHA-256 integrity verification
- OpenSSL / Python Cryptography primitives

This prevents:

1. Message tampering  
2. Agent impersonation  
3. Unauthorized phase manipulation  
4. MITM interception attacks

---

## Threat Detection in Traffic Network
Integrated cyber-resilience concepts include:

- Detection of anomalous traffic signal behavior
- False data injection monitoring
- Secure control command validation
- Trust verification among agents

---

## Emergency Vehicle Authentication
Emergency prioritization is protected against spoofing by:

- Cryptographic vehicle identity verification
- Authenticated priority requests
- Secure emergency signal overrides

Prevents misuse of emergency routing privileges.

---

## Secure MARL Framework
Each agent optimizes traffic while operating under:

State:
- Traffic congestion states
- Security anomaly states

Reward includes:
- Traffic efficiency
- Security compliance
- Attack resistance

This extends MARL into secure cyber-physical system control.


# System Architecture

```text
Traffic Data
   ↓
LSTM Prediction
   ↓
Dynamic Vehicle Insertion in SUMO
   ↓
MARL Agents at Intersections
   ↓
Adaptive Signal Optimization
   ↓
Reduced Congestion + Higher Throughput
```

---

# Tech Stack

- Python
- SUMO
- TraCI
- Multi-Agent Reinforcement Learning
- PPO / DQN concepts
- TensorFlow / Keras (LSTM)
- NumPy
- XML + CSV Analysis

---

# Project Structure

```bash
├── marl_agent.py               # Traffic signal MARL agent
├── run_marl_agent.py           # Simulation runner
├── csv_gen.py                  # Extract performance metrics
├── final2.sumocfg              # SUMO simulation config
├── fixed_timing_results.csv    # Baseline traffic results
├── marl_timing_results.csv     # MARL performance results
└── README.md
```

---

# Reinforcement Learning Formulation

## State Space
Each agent observes:

- Queue length
- Vehicle waiting time
- Traffic density
- Emergency vehicle presence

## Actions
Agent selects signal phase changes dynamically.

## Reward Function
Optimizes:

- Lower congestion
- Reduced waiting time
- Higher throughput
- Emergency prioritization

Example reward logic implemented in code: :contentReference[oaicite:2]{index=2}

```python
reward = -(queue_length + 0.5 * waiting_time)
```

---

# Results

Compared with rule-based traffic control:

| Metric | Traditional | MARL System |
|--------|------------|-------------|
Average Waiting Time | 55 sec | 32 sec |
Queue Length | 30 vehicles | 15 vehicles |
Fuel Consumption | 120 L | 90 L |
Traffic Throughput | 65% | 82% |

### Improvements
✅ Reduced congestion  
✅ Lower delay  
✅ Improved throughput  
✅ Better emergency handling  

Results derived from simulation study in report. :contentReference[oaicite:3]{index=3}

---

# Running the Project

## Install dependencies

```bash
pip install numpy traci
```

Install SUMO:
https://www.eclipse.org/sumo/

---

## Run Simulation

```bash
python run_marl_agent.py
```

Generate performance CSV:

```bash
python csv_gen.py
```

---

# Research Contributions

This project addresses challenging problems in:

- Multi-agent coordination
- Real-time adaptive control
- Multi-objective optimization
- Intelligent transportation systems
- AI for Smart Cities

## Key Contributions

- Hybrid LSTM + MARL traffic optimization
- Multi-agent adaptive signal coordination
- Emergency vehicle prioritization
- Cybersecure inter-agent communication using TLS 1.3 + SHA-256
- Protection against spoofing and MITM attacks in smart traffic systems

---

# Future Work

- Real-world sensor integration
- Computer vision traffic detection
- Federated multi-city training
- Edge deployment
- Smart route recommendation
- Large-scale city traffic optimization

---

# Author

Agrima  
B.Tech Computer & Communication Engineering  
Manipal University Jaipur

---

## If you found this interesting
Star the repository and feel free to contribute.