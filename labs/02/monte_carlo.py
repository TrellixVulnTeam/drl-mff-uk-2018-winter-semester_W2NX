#!/usr/bin/env python3
#
# All team solutions **must** list **all** members of the team.
# The members must be listed using their ReCodEx ids anywhere
# in the first comment block in the source file, i.e., in the first
# consecutive range of lines beginning with `#`.
#
# You can find out ReCodEx id on URL when watching ReCodEx profile.
# The id has the following format: 01234567-89ab-cdef-0123-456789abcdef.
#
# 090fa5b6-d3cf-11e8-a4be-00505601122b (Jan Rudolf)
# 08a323e8-21f3-11e8-9de3-00505601122b (Karel Ha)
#
import numpy as np

import cart_pole_evaluator

if __name__ == "__main__":
    # Fix random seed
    np.random.seed(42)

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default=1000, type=int, help="Training episodes.")
    parser.add_argument("--render_each", default=None, type=int, help="Render some episodes.")

    parser.add_argument("--epsilon", default=0.1, type=float, help="Exploration factor.")
    parser.add_argument("--epsilon_final", default=None, type=float, help="Final exploration factor.")
    parser.add_argument("--gamma", default=0.95, type=float, help="Discounting factor.")
    args = parser.parse_args()

    # Create the environment
    env = cart_pole_evaluator.environment()

    # Monte-Carlo RL algorithm for epsilon-soft policies.

    class C:
        def __init__(self, enviroment):
            self._state_action = np.zeros((enviroment.states, enviroment.actions))

        def add(self, state, action):
            self._state_action[state][action] += 1
            return self._state_action[state][action]

        def get(self, state, action):
            return self._state_action[state][action]


    class Q:
        def __init__(self, enviroment):
            self._state_action = np.zeros((enviroment.states, enviroment.actions))

        def update_value(self, state, action, value):
            self._state_action[state][action] = value

        def value(self, state, action):
            return self._state_action[state][action]

        def argmax(self, state):
            return np.argmax(self._state_action[state])

    q = Q(env)
    c = C(env)

    reward_per_100_episodes = [0] * 100
    average_rewards = [0] * 100
    flag_stop_training = False
    # The overall structure of the code follows.
    training = True
    while training:
        # Perform a training episode
        state, done = env.reset(start_evaluate=flag_stop_training), False

        history_per_episode = []
        cumulative_reward_per_episode = 0

        while not done:
            if args.render_each and env.episode and env.episode % args.render_each == 0:
                env.render()

            if np.random.uniform() > args.epsilon:
                action = q.argmax(state)
            else:
                action = np.random.randint(0, env.actions)

            next_state, reward, done, _ = env.step(action)

            history_per_episode.append((state, reward, action))
            state = next_state
            cumulative_reward_per_episode += reward

        reward_per_100_episodes.pop(0)
        reward_per_100_episodes.append(cumulative_reward_per_episode)
        # print('average reward', sum(reward_per_100_episodes)/100)

        goal = 0

        for history_item in reversed(history_per_episode):
            state, reward, action = history_item

            goal = args.gamma * goal + reward

            c_value = c.add(state, action)
            q_value = q.value(state, action)

            new_q_value = q_value + (1/c_value) * (goal - q_value)
            q.update_value(state, action, new_q_value)

        average_rewards.pop(0)
        average_rewards.append(sum(reward_per_100_episodes) / 100)

        if (sum(average_rewards)/100 > 490):
            flag_stop_training = True
            print(' STOP training')
    # Perform last 100 evaluation episodes
