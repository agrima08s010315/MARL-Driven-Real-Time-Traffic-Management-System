<div align="center">

# 🚦 MARL-Driven Real-Time Traffic Management System

### Secure Multi-Agent Adaptive Traffic Signal Control with LSTM Forecasting

A simulation-based intelligent transportation system combining **multi-agent adaptive signal control, LSTM traffic-demand forecasting, SUMO/TraCI, emergency-vehicle prioritization, and cryptographically secured inter-agent communication**.

<br>

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)
[![Patent](https://img.shields.io/badge/Patent-202511108091%20A-2563EB?style=for-the-badge\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-111827?style=for-the-badge)

</div>

---

## ✨ Overview

Urban traffic signals operating with fixed schedules cannot respond effectively to rapidly changing demand, incidents, or emergency vehicles.

This project explores a more adaptive approach in which **traffic intersections operate as autonomous agents** inside a SUMO simulation. Each agent observes local traffic conditions and dynamically adjusts signal behaviour using congestion information and predicted demand.

The project also addresses a second problem that is often ignored in intelligent traffic-control prototypes:

> **What happens if an attacker can impersonate an intersection, alter a message, replay an old command, or fraudulently request emergency priority?**

To address this, the adaptive control layer is combined with a security architecture using **TLS 1.3, mutual authentication, X.509 identities, RSA-PSS signatures, SHA-256, timestamps, and nonces**.

---

## 📜 Patent

### Indian Patent Application No. 202511108091 A

The traffic-management approach developed through this project forms the basis of an Indian patent application related to **MARL-driven real-time traffic signal management**.

[![View Patent](https://img.shields.io/badge/View%20Patent%20Document-Google%20Drive-4285F4?style=for-the-badge\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)

---

## 📊 Results at a Glance

The adaptive controller was evaluated against the project's **rule-based traffic-control baseline** using SUMO simulation.

| Metric               | Rule-Based Baseline | Adaptive System |                     Change |
| -------------------- | ------------------: | --------------: | -------------------------: |
| Average waiting time |                55 s |            32 s |                **↓ 41.8%** |
| Queue length         |         30 vehicles |     15 vehicles |                **↓ 50.0%** |
| Fuel consumption     |               120 L |            90 L |                **↓ 25.0%** |
| Traffic throughput   |                 65% |             82% | **↑ 17 percentage points** |

### Security Validation

* ✅ **17 automated security tests**
* 🛡️ **6 simulated attack classes blocked**
* 🔒 **TLS 1.3 mutual authentication**
* 🪪 **X.509 agent identities**
* ✍️ **RSA-PSS signed messages**
* 🔐 **SHA-256 integrity protection**
* ⏱️ **Timestamp + nonce replay defence**

> **Evaluation note:** Traffic-performance figures are derived from the project's SUMO simulation experiments. They are not measurements from a deployed municipal traffic network.

---

## 🎯 Problem Statement

Traditional fixed-time traffic signals use predefined schedules even when traffic conditions change significantly.

This can contribute to:

* increased vehicle waiting time
* growing intersection queues
* reduced network throughput
* unnecessary fuel consumption
* delayed emergency vehicles
* poor coordination between neighbouring intersections

The project models intersections as independent intelligent agents that observe current traffic conditions and adapt their signal behaviour accordingly.

---

## 🏗️ System Architecture

```text
                         Historical Traffic Data
                                   │
                                   ▼
                         ┌───────────────────┐
                         │  LSTM Forecasting │
                         └─────────┬─────────┘
                                   │
                           Predicted Demand
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SUMO Environment                         │
│                                                                 │
│   ┌────────────┐        ┌────────────┐        ┌────────────┐    │
│   │  Agent J1  │ ◄────► │  Agent J2  │ ◄────► │  Agent J3  │    │
│   └──────┬─────┘        └──────┬─────┘        └──────┬─────┘    │
│          │                     │                     │           │
│     Queue Length          Traffic Density       Emergency       │
│     Waiting Time                                Vehicle State   │
│          └─────────────────────┬──────────────────────┘          │
│                                ▼                                │
│                    Adaptive Signal Decisions                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
                    Waiting Time • Queue Length
                      Throughput • Fuel Usage
```

### Core Components

**SUMO**
Provides microscopic traffic simulation and vehicle movement.

**TraCI**
Allows Python agents to read vehicle states and control simulated traffic signals.

**Multi-Agent Controller**
Represents each controlled intersection as an autonomous decision-making agent.

**LSTM Forecasting**
Models changing traffic demand to support dynamic simulation scenarios.

**Security Layer**
Authenticates agents and protects inter-agent control messages.

---

## 🧠 Multi-Agent Traffic Control

Each controlled intersection acts as an independent traffic-signal agent operating inside the shared SUMO environment.

### State

Agents observe traffic features including:

```text
Queue Length
Waiting Time
Traffic Density
Emergency Vehicle Presence
```

### Action

An agent can modify traffic-light behaviour based on its observed state rather than relying exclusively on a permanently fixed schedule.

### Reward

The controller penalizes congestion and accumulated waiting time.

```python
reward = -(queue_length + 0.5 * waiting_time)
```

This provides an optimization signal favouring lower queues and reduced vehicle delay.

---

## 📈 LSTM Traffic-Demand Forecasting

Traffic conditions are not static. To model changing demand, the system includes an **LSTM-based forecasting component**.

```text
Historical Traffic Data
         │
         ▼
     LSTM Model
         │
         ▼
  Predicted Demand
         │
         ▼
 Vehicle Generation
         │
         ▼
   SUMO Simulation
         │
         ▼
 Adaptive Agents
```

Predicted demand can influence simulated vehicle arrivals, allowing experiments to represent changing traffic patterns instead of a single fixed scenario.

---

## 🚑 Emergency Vehicle Prioritization

Emergency vehicles introduce another objective beyond general congestion reduction.

When an authorized emergency vehicle is detected, signal behaviour can adapt to facilitate faster movement through an intersection.

However, blindly accepting a message such as:

```json
{
  "emergency": true
}
```

would create a serious security vulnerability.

A malicious participant could attempt to obtain traffic priority by simply claiming emergency status.

For this reason, emergency requests are processed through the same authenticated communication architecture used by the traffic agents.

---

# 🔐 Security Architecture

A distributed traffic-control system must protect both **network transport** and **application-level messages**.

Without authentication and integrity controls, an attacker could potentially:

* impersonate a traffic controller
* modify legitimate commands
* replay previously valid messages
* redirect traffic-control data
* spoof emergency priority
* insert unauthorized participants into the agent network

---

## 🛡️ Threat Model

| Threat              | Security Risk                   | Implemented Defence             |
| ------------------- | ------------------------------- | ------------------------------- |
| MITM interception   | Read or modify agent traffic    | **TLS 1.3 + mTLS**              |
| Agent impersonation | Rogue controller joins network  | **X.509 certificates**          |
| Message tampering   | Modify legitimate commands      | **RSA-PSS signatures**          |
| Replay attack       | Reuse previously valid messages | **Nonce + timestamp**           |
| Message redirection | Misroute legitimate commands    | **Signed metadata**             |
| Emergency spoofing  | Fraudulent priority request     | **Cryptographic authorization** |

---

## 🧱 Defence in Depth

```text
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                      │
│            Emergency Vehicle Authorization              │
├─────────────────────────────────────────────────────────┤
│                    MESSAGE LAYER                        │
│        RSA-PSS • SHA-256 • Nonce • Timestamp           │
├─────────────────────────────────────────────────────────┤
│                    IDENTITY LAYER                       │
│             X.509 PKI • Agent Certificates             │
├─────────────────────────────────────────────────────────┤
│                   TRANSPORT LAYER                       │
│                 TLS 1.3 Mutual TLS                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Security Modules

| Module                | Responsibility                                         |
| --------------------- | ------------------------------------------------------ |
| `crypto_utils.py`     | RSA-2048, SHA-256, and RSA-PSS primitives              |
| `pki.py`              | Certificate authority and per-agent X.509 certificates |
| `secure_message.py`   | Signed, timestamped, and nonced message envelopes      |
| `secure_channel.py`   | TLS 1.3 mutual-authentication channel                  |
| `emergency_auth.py`   | Emergency-vehicle authorization                        |
| `secure_agent.py`     | Security integration with traffic agents               |
| `attack_simulator.py` | Executable adversarial scenarios                       |

📄 Read the full security design in [`SECURITY.md`](./SECURITY.md).

---

# ⚔️ Adversarial Validation

The security architecture is validated through executable tests rather than documentation alone.

## Automated Security Tests

```bash
python -m pytest -v tests/test_security.py
```

The security suite contains **17 tests** covering authentication, integrity, replay protection, certificate handling, and emergency authorization.

---

## Attack Simulation

```bash
python demo.py
```

Six adversarial scenarios are exercised:

| Attack                     | Result      |
| -------------------------- | ----------- |
| Message tampering          | 🛡️ Blocked |
| Agent impersonation        | 🛡️ Blocked |
| Replay attack              | 🛡️ Blocked |
| MITM redirection           | 🛡️ Blocked |
| Emergency spoofing         | 🛡️ Blocked |
| Forged authorization token | 🛡️ Blocked |

---

## TLS Verification

```bash
python tls_smoke_test.py
```

The TLS smoke test validates the **TLS 1.3 mutual-authentication path** between simulated traffic-system participants.

---

# 📊 Simulation Evaluation

The adaptive controller is compared with the project's rule-based traffic-control baseline.

| Metric               |  Rule-Based | Adaptive System |      Change |
| -------------------- | ----------: | --------------: | ----------: |
| Average waiting time |        55 s |            32 s | **↓ 41.8%** |
| Queue length         | 30 vehicles |     15 vehicles | **↓ 50.0%** |
| Fuel consumption     |       120 L |            90 L | **↓ 25.0%** |
| Traffic throughput   |         65% |             82% | **↑ 17 pp** |

The measurements demonstrate the behaviour of the system under the evaluated SUMO configuration.

They should **not** be interpreted as guaranteed performance improvements on a real-world road network.

---

# 🛠️ Technology Stack

| Area                    | Technologies                 |
| ----------------------- | ---------------------------- |
| **Core Language**       | Python                       |
| **Traffic Simulation**  | SUMO, TraCI                  |
| **Adaptive Control**    | Multi-Agent Learning         |
| **Traffic Forecasting** | LSTM, TensorFlow/Keras       |
| **Numerical Computing** | NumPy                        |
| **Cryptography**        | RSA-2048, RSA-PSS, SHA-256   |
| **Identity**            | X.509 PKI                    |
| **Transport Security**  | TLS 1.3, mTLS                |
| **Testing**             | pytest                       |
| **Evaluation**          | CSV-based simulation metrics |

---

# 📁 Repository Structure

```text
MARL-Driven-Real-Time-Traffic-Management-System/
│
├── marl_agent.py
├── run_marl_agent.py
├── run_secure_marl_agent.py
├── csv_gen.py
├── final2.sumocfg
│
├── fixed_timing_results.csv
├── Marl_timing_results.csv
│
├── generate_keys.py
├── demo.py
├── tls_smoke_test.py
│
├── security/
│   ├── crypto_utils.py
│   ├── pki.py
│   ├── secure_message.py
│   ├── secure_channel.py
│   ├── emergency_auth.py
│   ├── secure_agent.py
│   └── attack_simulator.py
│
├── tests/
│   └── test_security.py
│
├── SECURITY.md
├── LICENSE
└── README.md
```

---

# 🚀 Running the Project

## Prerequisites

You will need:

* Python 3.10+
* SUMO
* TraCI
* NumPy
* `cryptography`
* `pytest`

Install the Python dependencies:

```bash
pip install numpy traci cryptography pytest
```

SUMO must also be installed and accessible from your environment.

---

## 1. Run the Adaptive Traffic Simulation

```bash
python run_marl_agent.py
```

---

## 2. Run the Security-Enabled Simulation

Generate PKI material for the traffic agents:

```bash
python generate_keys.py --agents J1 J2 J3 J4
```

Then run:

```bash
python run_secure_marl_agent.py
```

---

## 3. Generate Evaluation Data

```bash
python csv_gen.py
```

---

## 4. Run Security Tests

```bash
python -m pytest -v tests/test_security.py
```

---

## 5. Run Attack Scenarios

```bash
python demo.py
```

---

## 6. Verify TLS Communication

```bash
python tls_smoke_test.py
```

---

# 🔬 Engineering Highlights

### 🤖 Multi-Agent Decision Making

Intersections are modelled as independent decision-making agents operating inside a shared traffic environment.

### 🚦 Adaptive Signal Control

Traffic-light behaviour adapts to observed traffic conditions rather than relying exclusively on fixed signal schedules.

### 📈 Temporal Demand Modelling

LSTM-based forecasting represents changing traffic demand within simulation experiments.

### 🚑 Emergency-Aware Control

Emergency-vehicle priority is incorporated alongside general congestion-reduction objectives.

### 🔐 Secure Agent Communication

Inter-agent communication combines:

* TLS 1.3
* mutual authentication
* X.509 identities
* RSA-PSS signatures
* SHA-256
* timestamp validation
* nonce-based replay protection

### ⚔️ Adversarial Testing

Security assumptions are tested through executable attack scenarios involving:

* tampering
* replay
* impersonation
* MITM behaviour
* emergency-priority abuse
* forged authorization

---

# 🗺️ Engineering Roadmap

Potential future extensions include:

* larger multi-intersection SUMO networks
* cooperative multi-agent policies
* comparison with additional adaptive-control baselines
* real-world traffic sensor integration
* camera-based vehicle detection
* federated traffic-model training
* edge deployment of intersection agents
* adaptive vehicle routing
* city-scale simulation
* richer emergency-response coordination
* post-quantum authentication experiments
* stronger reproducibility and benchmarking pipelines

---

# ⚠️ Scope & Limitations

This repository is a **research and simulation project**.

Traffic-performance measurements were obtained from SUMO-based experiments and **do not represent deployment results from a real municipal transportation network**.

The cybersecurity components demonstrate defensive mechanisms within the simulated multi-agent environment and should **not be interpreted as a certified production Intelligent Transportation System security implementation**.

The repository is intended to demonstrate engineering concepts involving:

**adaptive control · multi-agent systems · traffic forecasting · secure distributed communication · adversarial testing**

---

# 📚 Project Resources

| Resource                 | Link                                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- |
| 🚦 Source Repository     | [View Repository](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)         |
| 📜 Patent Document       | [View Patent Application](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing) |
| 🔐 Security Architecture | [Read SECURITY.md](./SECURITY.md)                                                                             |
| 🧪 Security Tests        | [`tests/test_security.py`](./tests/test_security.py)                                                          |

---
<div align="center">

## 👩‍💻 Author

### Agrima Saxena

**Software Engineering · Applied AI · Secure Systems**

### Interested in the project?

Explore the implementation · reproduce the simulation · review the security architecture · run the adversarial tests · contribute improvements

<br>

<a href="https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System">
<img src="https://img.shields.io/badge/Explore-Repository-181717?style=flat-square&logo=github&logoColor=white"/>
</a>

<a href="./SECURITY.md">
<img src="https://img.shields.io/badge/Read-Security%20Architecture-2563EB?style=flat-square&logo=securityscorecard&logoColor=white"/>
</a>

</div>

