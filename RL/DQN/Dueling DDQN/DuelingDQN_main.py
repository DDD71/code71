# Double DQN + Dueling

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import gym


class Dueling_Net(nn.Module):
    def __init__(self,n_input,n_hidden,n_output):
        super(Dueling_Net, self).__init__()
        self.fc1 = nn.Linear(n_input, n_hidden)
        self.fc1.weight.data.normal_(0, 0.1)   # initialization
        self.out1 = nn.Linear(n_hidden, n_output)
        self.out1.weight.data.normal_(0, 0.1)   # initialization

        self.fc2 = nn.Linear(n_input,n_hidden)
        self.fc2.weight.data.normal_(0,0.1)
        self.out2 = nn.Linear(n_hidden,n_output)
        self.out2.weight.data.normal_(0,0.1)

    def forward(self, x):
        x1 = self.fc1(x)
        x1 = F.relu(x1)
        y1 = self.out1(x1)  # value function: just related with value  V(S,w,α)

        x2 = self.fc1(x)
        x2 = F.relu(x2)
        y2 = self.out2(x2)  # Advantage Function : A(S,A,w,β)

        x3 = y1 + (y2 - y2.mean(1).reshape(-1,1))  # 去中心化
        actions_value = x3
        return actions_value


env = gym.make('CartPole-v0')
env = env.unwrapped
N_ACTIONS = env.action_space.n   #2
N_STATES = env.observation_space.shape[0]  #4
ENV_A_SHAPE = 0 if isinstance(env.action_space.sample(), int) else env.action_space.sample().shape # to confirm the shape

class DQN(object):
    def __init__(self):
        # # Hyper Parameters
        self.lr = 0.01
        self.epsilon = 0.9  # e-greedy policy 
        self.gamma = 0.9
        self.memory_capacity = 200
        self.max_episode = 300
        self.batch_size = 32
        self.target_update_freq = 10

        self.learn_step_counter = 0                                     # for target updating
        self.memory_counter = 0                                        # for storing memory
        self.memory = np.zeros((self.memory_capacity, N_STATES * 2 + 2))     # initialize memory

        self.eval_net, self.target_net = Dueling_Net(N_STATES,50,N_ACTIONS), Dueling_Net(N_STATES,50,N_ACTIONS)  # network
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=self.lr)
        self.loss_func = nn.MSELoss()

    def get_reward(self,s_):
        # modify the reward to learn ,如果简单的给一些值容易跑飞
        x, x_dot, theta, theta_dot = s_
        # r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
        # r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
        r1 = -abs(x)
        r2 = -20*abs(theta)    #角度奖励大一点,负奖励（惩罚）效果好一些，引入一些先验经验，比如控制力矩小一些比较好
        r = r1 + r2
        return r

    def choose_action(self, x):
        x = torch.unsqueeze(torch.FloatTensor(x), 0)
        # input only one sample
        if np.random.uniform() > self.epsilon :   # greedy
            actions_value = self.eval_net.forward(x)
            action = torch.max(actions_value, 1)[1].data.numpy()
            action = action[0] if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)  # return the argmax index
        else:   # random
            action = np.random.randint(0, N_ACTIONS)
            action = action if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)
        self.epsilon -= self.epsilon/self.max_episode   # decrease epsilon, 从“强探索弱利用”过渡到“弱探索强利用”
        return action

    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, [a, r], s_))
        # replace the old memory with new memory
        index = self.memory_counter % self.memory_capacity
        self.memory[index, :] = transition
        self.memory_counter += 1

    def get_samples(self,batchs):
        # sample batch transitions
        sample_index = np.random.choice(self.memory_capacity, batchs)
        b_memory = self.memory[sample_index, :]
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES+1].astype(int))
        b_r = torch.FloatTensor(b_memory[:, N_STATES+1:N_STATES+2])
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])
        return b_s,b_a,b_r,b_s_

    def training(self):
        # target parameter update
        if self.learn_step_counter % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
        self.learn_step_counter += 1

        b_s,b_a,b_r,b_s_ = self.get_samples(batchs=self.batch_size)

        # # Double DQN   
        # #q_eval w.r.t the action in experience  
        q_eval = self.eval_net(b_s).gather(1, b_a)  # shape (batch, 1)
        next_action = self.eval_net(b_s_).argmax(1).reshape(self.batch_size, 1)   # the different from nature DQN 先从q_eval net 中选出价值最大的动作
        q_next = self.target_net(b_s_).gather(1, next_action).detach()     # detach from graph, don't backpropagate
        q_target = b_r + self.gamma * q_next

        loss = self.loss_func(q_eval, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.loss_value = loss.item()

    
if __name__ == "__main__": 
    dqn = DQN()
    print('\nCollecting experience...')
    for i_episode in range(dqn.max_episode):
        s = env.reset()
        exp_r = 0
        step_record = 0
        while True:
            env.render()
            a = dqn.choose_action(s)           # take action
            # step 函数，包含reward的定义
            s_, r, done, info = env.step(a)    # s_, r, done, info 新状态,采取这个行动的奖励，是否结束当前回合，其他信息，如性能和表现可用于调优
            r = dqn.get_reward(s_)  # modify the reward to learn
            dqn.store_transition(s, a, r, s_)
            exp_r += r
            step_record+=1
            if dqn.memory_counter > dqn.memory_capacity: #积累到一定数量开始训练
                dqn.training()
                if done:
                    print('loss:', dqn.loss_value)
                    print('i_episode: ', i_episode,
                        '| Expect_reward: ', round(exp_r, 2))
            if done:
                print("step_record:",step_record)
                print("x:",s[0],"|theta:",s[2],'\n')
                if step_record>1000:
                    print('convergence!!!')
                break
            s = s_

