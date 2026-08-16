<div align="center">

# MARL-Driven Real-Time Traffic Management System

### Adaptive traffic control, demand forecasting and secure inter-agent communication

A SUMO-based traffic management project that combines **multi-agent adaptive signal control, LSTM traffic forecasting, emergency vehicle prioritization and a secure communication layer for traffic agents**.

<br>

[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square\&logo=github\&logoColor=white)](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)
[![Patent](https://img.shields.io/badge/Patent-202511108091%20A-2563EB?style=flat-square\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square\&logo=python\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-222222?style=flat-square)

</div>

## Overview

This project started with a simple question: can traffic signals respond to changing traffic conditions instead of following the same fixed timing plan throughout a simulation?

The system models intersections as traffic-control agents inside **SUMO**. Python communicates with the simulation through **TraCI**, allowing the agents to observe local traffic conditions and change signal behaviour.

The project also includes:

* LSTM-based traffic demand prediction
* emergency vehicle prioritization
* comparison against a rule-based baseline
* TLS 1.3 mutual authentication between simulated agents
* X.509 certificates for agent identity
* RSA-PSS signed messages
* timestamp and nonce-based replay protection
* security tests and simulated attack scenarios

The traffic-control and security parts are kept separate so that the control logic does not have to trust every incoming message automatically.

## Patent

### Indian Patent Application No. 202511108091 A

A patent application has been filed for the traffic-management approach developed through this project.

[View the patent document](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)

## Results

The adaptive traffic-control implementation was compared with the project's rule-based baseline in SUMO.

| Metric               | Rule-Based Baseline | Adaptive System |                          Change |
| -------------------- | ------------------: | --------------: | ------------------------------: |
| Average waiting time |                55 s |            32 s |                 **41.8% lower** |
| Queue length         |         30 vehicles |     15 vehicles |                   **50% lower** |
| Fuel consumption     |               120 L |            90 L |                   **25% lower** |
| Throughput           |                 65% |             82% | **17 percentage points higher** |

These figures come from the simulation setup included with the project. They should not be interpreted as expected performance on a real road network.

### Security validation

The security layer is also tested separately.

* **17 security-focused automated tests**
* **6 simulated attack classes**
* TLS 1.3 mutual authentication
* X.509 identities
* RSA-PSS signatures
* SHA-256 hashing
* nonce and timestamp validation
* emergency authorization checks

## Why this project

Fixed-time traffic signals are easy to implement, but they do not respond well when traffic conditions change.

A static schedule may continue assigning green time to one road while another approach develops a long queue. The problem becomes more noticeable when the system also has to deal with emergency vehicles or coordination between nearby intersections.

The project therefore focuses on three connected areas:

1. **Adaptive traffic control**
   Signals react to observed traffic conditions rather than relying only on fixed timings.

2. **Traffic demand forecasting**
   An LSTM model is used to represent changing traffic demand in the simulation.

3. **Secure agent communication**
   Messages exchanged between simulated traffic agents are authenticated and checked before they are trusted.

## System Architecture

```text
                    Historical Traffic Data
                              |
                              v
                     +------------------+
                     |  LSTM Forecast   |
                     +--------+---------+
                              |
                       Predicted Demand
                              |
                              v
                +---------------------------+
                |      SUMO Simulation      |
                |                           |
                |  J1 <-> J2 <-> J3 <-> J4 |
                |                           |
                +-------------+-------------+
                              |
                    Traffic observations
                              |
            +-----------------+-----------------+
            |                                   |
            v                                   v
   Adaptive Signal Logic              Emergency Priority
            |                                   |
            +-----------------+-----------------+
                              |
                              v
                     Signal Decisions
                              |
                              v
              Waiting Time / Queue / Throughput
```

**SUMO** provides the microscopic traffic simulation.

**TraCI** allows the Python code to inspect vehicles, queues and traffic lights during execution.

## Adaptive Traffic Control

Each controlled intersection is treated as an independent traffic-control agent.

### Observed state

The controller can use values such as:

```text
queue length
waiting time
traffic density
emergency vehicle presence
```

### Actions

The traffic agent changes the active signal phase or associated timing based on the observed traffic state.

### Reward signal

The implementation uses congestion and waiting time as negative feedback.

```python
reward = -(queue_length + 0.5 * waiting_time)
```

Lower queue lengths and lower accumulated waiting time therefore produce a better reward.

## LSTM Traffic Forecasting

Traffic demand changes over time, so the project also includes a forecasting component.

```text
Historical traffic observations
            |
            v
        LSTM model
            |
            v
     Predicted demand
            |
            v
     Vehicle generation
            |
            v
      SUMO simulation
```

The prediction component is useful for experiments where vehicle arrivals should vary over time rather than follow only one static pattern.

## Emergency Vehicle Priority

Emergency vehicle requests are treated differently from ordinary traffic observations.

A controller should not grant priority only because an incoming message contains:

```json
{
  "emergency": true
}
```

That would make emergency priority easy to spoof.

The project therefore connects emergency requests to the security layer. A request must pass the relevant authentication and authorization checks before it is treated as trusted emergency traffic.

## Security Design

The traffic agents form a small distributed system, so the communication layer is protected separately from the traffic-control algorithm.

The main threats considered are:

| Threat                | Example                                      | Protection                                |
| --------------------- | -------------------------------------------- | ----------------------------------------- |
| Agent impersonation   | A rogue process claims to be intersection J2 | X.509 identity and certificate trust      |
| Message tampering     | Signal command is changed in transit         | RSA-PSS signature and SHA-256             |
| Replay                | An old valid command is sent again           | Nonce and timestamp checks                |
| MITM                  | Traffic is intercepted or redirected         | TLS 1.3 mTLS and signed receiver metadata |
| Emergency spoofing    | Normal vehicle requests emergency priority   | Signed authorization token                |
| Untrusted participant | Certificate is not issued by trusted CA      | CA validation                             |

The design uses several layers instead of relying on only TLS.

```text
Application layer
Emergency authorization

Message layer
RSA-PSS
SHA-256
Nonce
Timestamp
Sender / receiver binding

Identity layer
X.509 certificates
Traffic authority CA

Transport layer
TLS 1.3
Mutual TLS
```

For a more detailed explanation, see [`SECURITY.md`](./SECURITY.md).

## Security Modules

| File                           | Purpose                                      |
| ------------------------------ | -------------------------------------------- |
| `security/crypto_utils.py`     | RSA, SHA-256, signing and verification       |
| `security/pki.py`              | Certificate authority and X.509 certificates |
| `security/secure_message.py`   | Signed message envelopes                     |
| `security/secure_channel.py`   | TLS 1.3 communication                        |
| `security/emergency_auth.py`   | Emergency authorization                      |
| `security/secure_agent.py`     | Integration with traffic agents              |
| `security/attack_simulator.py` | Simulated attacks                            |

## Security Testing

Run the automated tests with:

```bash
python -m pytest -v tests/test_security.py
```

The current test suite contains **17 security-focused tests**.

The tests cover areas such as:

* message tampering
* replayed messages
* stale timestamps
* sender impersonation
* untrusted certificates
* receiver modification
* emergency authorization
* expired tokens
* token reassignment

### Attack simulation

Run:

```bash
python demo.py
```

The attack simulation covers six scenarios:

| Scenario                   | Expected Result |
| -------------------------- | --------------- |
| Message tampering          | Blocked         |
| Agent impersonation        | Blocked         |
| Replay                     | Blocked         |
| MITM redirection           | Blocked         |
| Emergency spoofing         | Blocked         |
| Forged authorization token | Blocked         |

### TLS smoke test

Run:

```bash
python tls_smoke_test.py
```

This checks the mutual TLS communication path independently from the signed-message tests.

## Technology Stack

| Area                | Technology                   |
| ------------------- | ---------------------------- |
| Language            | Python                       |
| Traffic simulation  | SUMO                         |
| Simulation control  | TraCI                        |
| Traffic forecasting | LSTM                         |
| Numerical work      | NumPy                        |
| Cryptography        | RSA-2048, RSA-PSS, SHA-256   |
| Identity            | X.509 PKI                    |
| Transport security  | TLS 1.3, mTLS                |
| Testing             | pytest                       |
| Evaluation          | CSV-based simulation metrics |

## Repository Structure

```text
MARL-Driven-Real-Time-Traffic-Management-System/
|
├── marl_agent.py
├── run_marl_agent.py
├── run_secure_marl_agent.py
├── csv_gen.py
├── final2.sumocfg
|
├── fixed_timing_results.csv
├── Marl_timing_results.csv
|
├── generate_keys.py
├── demo.py
├── tls_smoke_test.py
|
├── security/
│   ├── crypto_utils.py
│   ├── pki.py
│   ├── secure_message.py
│   ├── secure_channel.py
│   ├── emergency_auth.py
│   ├── secure_agent.py
│   └── attack_simulator.py
|
├── tests/
│   └── test_security.py
|
├── SECURITY.md
├── LICENSE
└── README.md
```

## Running the Project

### Requirements

You need:

* Python 3.10+
* SUMO
* TraCI
* NumPy
* `cryptography`
* `pytest`

Install the Python packages:

```bash
pip install numpy traci cryptography pytest
```

SUMO must also be installed and available in your environment.

### Run the traffic simulation

```bash
python run_marl_agent.py
```

### Generate agent certificates and keys

```bash
python generate_keys.py --agents J1 J2 J3 J4
```

### Run the secure traffic simulation

```bash
python run_secure_marl_agent.py
```

### Generate evaluation output

```bash
python csv_gen.py
```

### Run the security tests

```bash
python -m pytest -v tests/test_security.py
```

### Run the attack demo

```bash
python demo.py
```

### Test mutual TLS

```bash
python tls_smoke_test.py
```

## What I focused on

### Traffic control

The project experiments with adapting traffic signals using local traffic measurements instead of depending entirely on fixed timings.

### Forecasting

LSTM-based demand modelling is used to represent changing traffic conditions.

### Emergency handling

Emergency vehicles receive special handling, but their requests still have to pass authorization checks.

### Distributed system security

Each traffic agent has an identity and messages are authenticated before they affect another controller.

### Testing

The project includes separate validation for traffic behaviour and security behaviour instead of presenting the architecture only as documentation.

## Limitations

This is a **simulation and research project**.

The traffic results were produced using SUMO and do not represent a deployed city traffic network.

The security implementation is also a prototype used to demonstrate defensive concepts. It is not a certified Intelligent Transportation System security product.

Some limitations of the current work include:

* simulation-scale network size
* no real municipal sensor feed
* no production certificate revocation service
* no hardware-backed key storage
* no large-scale DoS protection
* no compromised-controller recovery
* no post-quantum cryptography

## Possible Next Steps

Some useful extensions would be:

* larger SUMO road networks
* cooperative traffic agents
* additional control baselines
* real traffic sensor datasets
* camera-based vehicle detection
* edge deployment
* certificate revocation and rotation
* controller attestation
* Byzantine-agent detection
* security telemetry
* post-quantum authentication experiments

## Project Resources

| Resource               | Link                                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| Repository             | [GitHub](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)        |
| Patent                 | [View document](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing) |
| Security documentation | [`SECURITY.md`](./SECURITY.md)                                                                      |
| Security tests         | [`tests/test_security.py`](./tests/test_security.py)                                                |

<div align="center">

## Author

### Agrima Saxena

**Software Engineering · Applied AI · Secure Systems**

<table align="center">
<tr>

<td align="center" width="70">
<a href="https://www.linkedin.com/in/agrima-saxena-142960426/">
<img src="https://img.icons8.com/color/48/linkedin.png" width="32" height="32" alt="LinkedIn"/>
</a>
</td>

<td align="center" width="70">
<a href="mailto:agrimalc@gmail.com">
<img src="https://img.icons8.com/color/48/gmail-new.png" width="32" height="32" alt="Email"/>
</a>
</td>

<td align="center" width="70">
<a href="https://github.com/agrima08s010315">
<img src="https://img.icons8.com/ios-glyphs/48/ffffff/github.png" width="32" height="32" alt="GitHub"/>
</a>
</td>

</tr>
</table>

<br>

If you want to explore the project further, start with the simulation code and [`SECURITY.md`](./SECURITY.md).

</div>
