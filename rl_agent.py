import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size * 2)  # For both paddles 

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)

class RLAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        torch.set_default_dtype(torch.float32)
        print("Using device:", self.device)

        self.q_network = QNetwork(state_size, action_size).to(self.device)
        self.target_network = QNetwork(state_size, action_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.memory = deque(maxlen=100000)
        self.batch_size = 32

        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return [random.randrange(self.action_size), random.randrange(self.action_size)]
        
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            action_values = self.q_network(state)
        left_action = np.argmax(action_values.cpu().data.numpy()[0][:self.action_size])
        right_action = np.argmax(action_values.cpu().data.numpy()[0][self.action_size:])
        return [left_action, right_action]

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)

        # float64 is not supported in mps framework
        states = torch.tensor(np.array(states), dtype=torch.float32).to(self.device)
        actions = torch.tensor(np.array(actions), dtype=torch.long).to(self.device)
        rewards = torch.tensor(np.array(rewards), dtype=torch.float32).to(self.device)
        next_states = torch.tensor(np.array(next_states), dtype=torch.float32).to(self.device)
        dones = torch.tensor(np.array(dones), dtype=torch.float32).to(self.device)

        current_q_values = self.q_network(states)
        next_q_values = self.target_network(next_states).detach()

        target_q_values = current_q_values.clone()
        for i in range(self.batch_size):
            for j in range(2):
                if dones[i]:
                    target_q_values[i][actions[i][j] + j*self.action_size] = rewards[i]
                else:
                    target_q_values[i][actions[i][j] + j*self.action_size] = rewards[i] + \
                        self.gamma * torch.max(next_q_values[i][j*self.action_size:(j+1)*self.action_size])

        loss = self.criterion(current_q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

def create_agent(state_size, action_size):
    return RLAgent(state_size, action_size)

def preprocess_state(ball_x, ball_y, paddle_left_y, paddle_right_y, ball_speed_x, ball_speed_y):
    return np.array([ball_x, ball_y, paddle_left_y, paddle_right_y, ball_speed_x, ball_speed_y], dtype=np.float32)

def get_action_from_index(index):
    if index == 0:
        return -5  # Move up
    elif index == 1:
        return 0   # Stay
    else:
        return 5   # Move down
