import traci
import numpy as np
from marl_agent import TrafficSignalAgent

# Start SUMO
traci.start(["sumo-gui", "-c", "C:\\Users\\Lenovo\\Downloads\\final2.sumocfg"])

# Create MARL agents for each traffic light (detectors assigned dynamically)
traffic_lights = traci.trafficlight.getIDList()
agents = {tl: TrafficSignalAgent(tl) for tl in traffic_lights}

# Initialize tracking variables
vehicle_counts = {tl: [] for tl in traffic_lights}
rewards = {tl: [] for tl in traffic_lights}

# Run simulation for 37172 steps
for step in range(37172):
    traci.simulationStep()

    for agent in agents.values():
        state = agent.get_state()  # Extract state
        action = agent.choose_action()  # Choose an action
        agent.apply_action(action)  # Apply action
        reward = agent.get_reward()  # Compute reward

        # Store data for analysis
        vehicle_counts[agent.intersection_id].append(state[0])
        rewards[agent.intersection_id].append(reward)

    # Print summary every 7435 steps
    if step % 7435 == 0:
        print(f"\n==== Step {step} Summary ====")
        for tl in traffic_lights:
            avg_vehicles = np.mean(vehicle_counts[tl])
            avg_reward = np.mean(rewards[tl])
            print(f"{tl}: Avg Vehicles = {avg_vehicles:.2f}, Avg Reward = {avg_reward:.2f}")

traci.close()
