import random
import time
from typing import List

from testgen.models.test_case import TestCase
from testgen.reinforcement.environment import ReinforcementEnvironment
from testgen.service.logging_service import get_logger


class ReinforcementAgent:
    def __init__(self, file_name: str, environment: ReinforcementEnvironment, test_cases: List[TestCase], q_table=None):
        self.learning_rate = 0.1
        self.file_name = file_name
        self.env = environment
        self.q_table = q_table if q_table else {}
        self.actions = ["add", "merge", "remove", "z3"]
        self.logger = get_logger()

    def collect_test_cases(self) -> List[TestCase]:
        max_time = 30
        if not self.q_table:
            print("Q_TABLE IS EMPTY, RUN TRAIN FIRST")
            return []
        else:
            current_state = self.env.get_state()

            goal_state: float = 100.0

            start_time = time.time()

            while current_state[0] != goal_state and time.time() - start_time < max_time:
                action = self.choose_action(current_state)
                next_state, reward = self.env.step(action)

                if not isinstance(next_state, tuple) or len(next_state) != 2:
                    raise ValueError(f"Expected new_state to be a tuple (covered_statements, coverage_percentage, len(test_cases)), but got: {next_state}")

                self.update_q_table(next_state, action, next_state, reward)

                current_state = next_state

            return self.env.test_cases


    def do_q_learning(self, episodes=10):
        max_time = 30
        best_coverage = 0.0
        best_test_cases = []

        for episode in range(episodes):
            print(f"\nNEW EPISODE {episode}")
            self.env.reset()

            current_state = self.env.get_state()
            self.logger.debug(f"Current state after reset: {current_state}")

            goal_state: float = 100.0
            steps_in_episode = 1
            max_steps_per_episode = 100

            start_time = time.time()

            while current_state[0] != goal_state and steps_in_episode < max_steps_per_episode and time.time() - start_time < max_time:
                print(f"\nStep {steps_in_episode} in episode {episode}")

                action = self.choose_action(current_state)
                next_state, reward = self.env.step(action)

                if not isinstance(next_state, tuple) or len(next_state) != 2:
                    raise ValueError(f"Expected new_state to be a tuple (covered_statements, coverage_percentage, len(test_cases)), but got: {next_state}")

                print(f"AFTER NEW STATE, REWARD: {reward}")

                # Update q_table
                self.update_q_table(current_state, action, next_state, reward)
                current_state = next_state

                steps_in_episode += 1
                if current_state[0] > best_coverage:
                    best_coverage = current_state[0]
                    best_test_cases = self.env.test_cases.copy()
                    self.logger.debug(f"New best coverage: {best_coverage}% with {len(best_test_cases)} test cases")
                elif current_state[0] == best_coverage and len(best_test_cases) > len(self.env.test_cases):
                    best_test_cases = self.env.test_cases.copy()
                    self.logger.debug(f"New best coverage: {best_coverage}% with {len(best_test_cases)} test cases")

        return best_test_cases


    def choose_action(self, state):
        EXPLORATION = 0
        EXPLOITATION = 1

        weights = [0.33, 0.67]
        
        choice = random.choices([EXPLORATION, EXPLOITATION], weights=weights, k=1)[0]
        action_list = self.get_action_list(state[1])

        if not isinstance(state, tuple) or len(state) != 2:
            raise ValueError(f"Expected state to be a tuple (covered_statements, coverage_percentage, len(test_cases)), but got: {state}")

        if choice == EXPLORATION:
            chosen_action = random.choice(action_list)
            print(f"CHOSEN EXPLORATION ACTION: {chosen_action}")
            return chosen_action
        else:
            chosen_action = max(action_list, key=lambda action: self.q_table.get((state, action), 0), default=random.choice(action_list))
            print(f"CHOSEN EXPLOITATION ACTION: {chosen_action}")
            return chosen_action

    

    @staticmethod
    def get_action_list(test_case_length: int) -> List[str]:
        action_list = ["add", "z3"]
        if test_case_length >= 2:
            action_list.extend(["merge", "remove"])
        return action_list

    def update_q_table(self, state: tuple, action: str, new_state:tuple, reward:float):
        current_q = self.q_table.get((state, action), 0)
        self.logger.debug(f"CURRENT Q: {current_q}")
        valid_actions = self.get_action_list(new_state[1])

        max_next_q = max(self.q_table.get((new_state, a), 0) for a in valid_actions)
        self.logger.debug(f"MAX NEXT Q: {max_next_q}")

        print(f"UPDATING Q TABLE FOR STATE: {state}, ACTION: {action} WITH REWARD: {reward}")
        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (reward + max_next_q)
        
        self.q_table[(state, action)] = new_q
        
        """def optimize_test_suit(self, current_state, executable_statements):
        # Try to optimize test cases by repeatedly performing remove actions if reached full coverage
        test_case_count = current_state[1]
        optimization_attempts = min(10, test_case_count - 1)

        for _ in range(optimization_attempts):
            if test_case_count <= 1:
                break

            action = "remove"
            next_state, reward = self.env.step(action)

            new_covered = next_state[0]
            new_uncovered = [stmt for stmt in executable_statements if stmt not in new_covered]

            if len(new_uncovered) == 0:
                current_state = next_state
                test_case_count = current_state[2]
                print(f"Optimized to {test_case_count} test cases.")
            else:
                # Add a test case back if removing broke coverage
                self.env.step("add")
                break

        return current_state"""