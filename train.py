import pygame
import numpy as np
import torch
import matplotlib.pyplot as plt
from rl_agent import create_agent, preprocess_state, get_action_from_index
from game import Ball, Paddle, SCREEN_WIDTH, SCREEN_HEIGHT, BALL_RADIUS, WHITE, BLACK

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def calculate_reward(ball, paddle_left, paddle_right):
    reward = 0
    
    # Reward for hitting the ball
    if ball.rect.colliderect(paddle_left.rect) or ball.rect.colliderect(paddle_right.rect):
        reward += 1
    
    left_distance = abs(paddle_left.rect.centery - ball.rect.centery)
    right_distance = abs(paddle_right.rect.centery - ball.rect.centery)
    reward += max(0, (SCREEN_HEIGHT / 2 - left_distance) / SCREEN_HEIGHT)
    reward += max(0, (SCREEN_HEIGHT / 2 - right_distance) / SCREEN_HEIGHT)
    
    if ball.rect.x < -BALL_RADIUS or ball.rect.x > SCREEN_WIDTH + BALL_RADIUS:
        reward -= 1
    
    return reward

def train_agent(episodes=2000, max_steps=10000):
    state_size = 6
    action_size = 3
    agent = create_agent(state_size, action_size)

    scores = []
    epsilon_history = []

    for episode in range(episodes):
        ball = Ball()
        paddle_left = Paddle("left")
        paddle_right = Paddle("right")
        all_sprites = pygame.sprite.Group(ball, paddle_left, paddle_right)

        state = preprocess_state(ball.rect.x, ball.rect.y, paddle_left.rect.y, paddle_right.rect.y, ball.speed_x, ball.speed_y)
        score = 0

        for step in range(max_steps):
            # Get actions from agent for both paddles
            actions = agent.act(state)
            paddle_left.speed_y = get_action_from_index(actions[0])
            paddle_right.speed_y = get_action_from_index(actions[1])

            # Update game state
            all_sprites.update()

            # Check for collisions
            if ball.rect.colliderect(paddle_left.rect) or ball.rect.colliderect(paddle_right.rect):
                ball.speed_x *= -1

            # Calculate reward
            reward = calculate_reward(ball, paddle_left, paddle_right)
            score += reward

            # Get new state
            next_state = preprocess_state(ball.rect.x, ball.rect.y, paddle_left.rect.y, paddle_right.rect.y, ball.speed_x, ball.speed_y)

            # end condition 
            done = ball.rect.x < -BALL_RADIUS or ball.rect.x > SCREEN_WIDTH + BALL_RADIUS

            agent.remember(state, actions, reward, next_state, done)

            # Train agent
            agent.replay()

            # Update the state
            state = next_state

            # Render the game
            screen.fill(BLACK)
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(60)

            if done:
                break

        # Update target network
        if episode % 10 == 0:
            agent.update_target_network()

        scores.append(score)
        epsilon_history.append(agent.epsilon)
        print("Episode: {}/{}, Score: {:.2f}, Epsilon: {:.2f}".format(episode+1, episodes, score, agent.epsilon))

        if (episode + 1) % 100 == 0:
            torch.save(agent.q_network.state_dict(), "pong_agent_episode_{}.pth".format(episode+1))

    return agent, scores, epsilon_history

if __name__ == "__main__":
    trained_agent, training_scores, epsilon_history = train_agent()

    # Plot training scores
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(training_scores)
    plt.title('Training Scores')
    plt.xlabel('Episode')
    plt.ylabel('Score')

    # Plot epsilon
    plt.subplot(1, 2, 2)
    plt.plot(epsilon_history)
    plt.title('Epsilon History')
    plt.xlabel('Episode')
    plt.ylabel('Epsilon')

    plt.tight_layout()
    plt.savefig('training_results.png')
    plt.show()

    torch.save(trained_agent.q_network.state_dict(), "pong_agent_final.pth")
