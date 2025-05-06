
import ast
from abc import ABC
import random
from typing import List

import testgen.util.randomizer
from testgen.models.test_case import TestCase
from testgen.analyzer.test_case_analyzer import TestCaseAnalyzerStrategy
from testgen.reinforcement.environment import ReinforcementEnvironment


# Goal: Learn a policy to generate a set of test cases with optimal code coverage, and minimum number of test cases
# Environment: FUT (Function Under Test)
# Agent: System
# Actions: Create new test case, combine test cases, delete test cases
# Rewards:

# Maybe consider the state as number of branches covered in a function possibly considering it the same state

class ReinforcementAnalyzer(TestCaseAnalyzerStrategy, ABC):
    def __init__(self, module, class_name: str, env: ReinforcementEnvironment):
        super().__init__(module, class_name)
        self.env = env # includes file name, module/fut, coverage, and test cases
        self.q_table = {} # Dictionary of key: state, action pairs and value: q-value
        self.actions = ["add", "merge", "remove"] # three possible actions

    def collect_test_cases(self, func_node: ast.FunctionDef) -> List[TestCase]:
        self.env.test_cases.append(testgen.util.randomizer.new_random_test_case(f"{self._module.__name__}.py", func_node))
        return self.env.test_cases

    def set_env(self, env: ReinforcementEnvironment):
        self.env = env

    def refine_test_cases(self, func: ast.FunctionDef) -> List[TestCase]:
        state = self.env.get_state() # Should return state as Tuple(List[TestCase], coverage)

        if not isinstance(state, tuple) or len(state) != 2:
            raise ValueError(f"Expected state to be a tuple (test_cases, coverage_score), but got: {state}")

        action = self.choose_action(state)
        new_state, reward = self.env.step(action)

        if not isinstance(new_state, tuple) or len(new_state) != 2:
            raise ValueError(f"Expected new_state to be a tuple (test_cases, coverage_score), but got: {new_state}")

        print(f"AFTER NEW STATE, REWARD: {reward}")

        self.update_q_table(state, action, reward, new_state)

        return self.env.test_cases

    def choose_action(self, state):
        choice = random.choice(["EXPLORATION", "EXPLOITATION"])
        test_cases, coverage_score = state  # Unpack state properly
        state_key = (tuple((tc.func_name, tc.inputs, tc.expected) for tc in test_cases), coverage_score)

        if choice == "EXPLORATION":
            return random.choice(self.actions)
        else:
            # Is going to try to pick the highest value in the q_table with the state_key and action pair
            # Is probably always going to be 0 unless we have the same exact test cases and coverage as represented in the state key
            return max(self.actions, key=lambda action: self.q_table.get((state_key, action), 0), default=random.choice(self.actions))

    def update_q_table(self, state, action, reward, next_state):
        test_cases, coverage_score = state
        next_test_cases, next_coverage_score = next_state

        state_key = (tuple((tc.func_name, tc.inputs, tc.expected) for tc in test_cases), coverage_score)
        next_state_key = (tuple((tc.func_name, tc.inputs, tc.expected) for tc in next_test_cases), next_coverage_score)

        print("HERE UPDATE TABLE")
        old_q = self.q_table.get((state_key, action), 0)
        future_q = max(self.q_table.get((next_state_key, a), 0) for a in self.actions)
        self.q_table[(state_key, action)] = old_q * (reward + future_q)
