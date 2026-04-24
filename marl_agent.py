import numpy as np
import traci

class TrafficSignalAgent:
    def __init__(self, intersection_id):
        self.intersection_id = intersection_id
        self.state = None
        self.reward = 0

        # Fetch all detectors automatically
        self.detectors = self._assign_detectors()

    def _assign_detectors(self):
        """Assigns loop detectors dynamically based on traffic light control lanes."""
        assigned_detectors = []
        controlled_lanes = set(traci.trafficlight.getControlledLanes(self.intersection_id))
        
        for detector in traci.lanearea.getIDList():
            detector_lane = traci.lanearea.getLaneID(detector)
            if detector_lane in controlled_lanes:
                assigned_detectors.append(detector)

        return assigned_detectors

    def get_state(self):
        """Extracts real-time traffic data using lane area detectors."""
        queue_length = sum(traci.lanearea.getLastStepVehicleNumber(detector) for detector in self.detectors)
        waiting_time = sum(traci.lane.getWaitingTime(traci.lanearea.getLaneID(detector)) for detector in self.detectors)
        emergency_present = any(traci.vehicle.getTypeID(v) == "emergency" for v in traci.vehicle.getIDList())

        return np.array([queue_length, waiting_time, int(emergency_present)])

    def choose_action(self):
        """Selects an action (random for now, RL later)."""
        return np.random.choice([0, 1, 2, 3])

    def apply_action(self, action):
        """Changes traffic light phase based on selected action."""
        phases = traci.trafficlight.getAllProgramLogics(self.intersection_id)[0].phases
        traci.trafficlight.setPhase(self.intersection_id, action % len(phases))

    def get_reward(self):
        """Computes reward based on detector-based congestion and emergency handling."""
        queue_length = sum(traci.lanearea.getLastStepVehicleNumber(detector) for detector in self.detectors)
        waiting_time = sum(traci.lane.getWaitingTime(traci.lanearea.getLaneID(detector)) for detector in self.detectors)
        emergency_present = any(traci.vehicle.getTypeID(v) == "emergency" for v in traci.vehicle.getIDList())

        # Reward structure (aligns with PPO)
        reward = - (queue_length + 0.5 * waiting_time)
        if emergency_present:
            reward -= 50  # Lower penalty compared to before

        return reward
