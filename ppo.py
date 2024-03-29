# 代码用于离散环境的模型
# import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

# ----------------------------------- #
# 构建策略网络--actor
# ----------------------------------- #

class PolicyNet(nn.Module):
    def __init__(self, n_visions, n_actions):
        # n_hiddens = 2**
        super(PolicyNet, self).__init__()

        # print('Ploci',n_visions,n_actions)
        n_hiddens0 = 2**3
        n_hiddens1 = 2**3
        n_hiddens2 = 2**3
        # n_hiddens0 = 2**3
        # n_hiddens1 = 2**3
        # n_hiddens2 = 2**3


        # n_hiddens0 = 2**9
        # n_hiddens1 = 2**8
        # n_hiddens2 = 2**7

        self.in_put = nn.Linear(n_visions, n_hiddens0)

        self.fc1 = nn.Linear(n_hiddens0, n_hiddens1)
        self.fc2 = nn.Linear(n_hiddens1, n_hiddens2)
        
        self.out_put = nn.Linear(n_hiddens2, n_actions)
    def forward(self, x):

        x = x.float()
        x = self.in_put(x)  # [b,n_visions]-->[b,n_hiddens]
        x = F.relu(x)

        
        
        x = self.fc1(x)  # [b,n_visions]-->[b,n_hiddens]
        x = F.relu(x)
        x = self.fc2(x)  # [b,n_visions]-->[b,n_hiddens]
        x = F.relu(x)
        
        
        x = self.out_put(x)  # [b, n_actions]
        x = F.softmax(x, dim=1)  # [b, n_actions]  计算每个动作的概率
        return x

# ----------------------------------- #
# 构建价值网络--critic
# ----------------------------------- #

class ValueNet(nn.Module):
    def __init__(self, n_visions):

        super(ValueNet, self).__init__()


        n_hiddens = 2**3
        self.in_put = nn.Linear(n_visions, n_hiddens)

        self.fc1 = nn.Linear(n_hiddens, n_hiddens)
        self.fc2 = nn.Linear(n_hiddens, n_hiddens)

        self.out_put = nn.Linear(n_hiddens, 1)
    def forward(self, x):
        x = self.in_put(x)  # [b,n_visions]-->[b,n_hiddens]
        x = F.relu(x)

        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)

        x = self.out_put(x)  # [b,n_hiddens]-->[b,1]  评价当前的状态价值view_value
        return x

# ----------------------------------- #
# 构建模型
# ----------------------------------- #

class ppo:
    def __init__(self, n_visions, n_actions,
                 actor_lr, critic_lr, lmbda, epochs, eps, gamma):
        
        device = torch.device('cpu')
        if( torch.cuda.is_available()   ):
            device = torch.device('cuda')

        # device = torch.device('cuda') if torch.cuda.is_available() \
        #                             else torch.device('cpu')
        

        # 实例化策略网络
        self.actor = PolicyNet(n_visions, n_actions).to(device)
        # 实例化价值网络
        self.critic = ValueNet(n_visions).to(device)


        # 策略网络的优化器
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=actor_lr)
        # 价值网络的优化器
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr = critic_lr)

        self.gamma = gamma  # 折扣因子
        self.lmbda = lmbda  # GAE优势函数的缩放系数
        self.epochs = epochs  # 一条序列的数据用来训练轮数
        self.eps = eps  # PPO中截断范围的参数
        self.device = device

        self.n_visions = n_visions

    def store(self,experience):

        return 

    # 动作选择
    def take_action(self, vision):
        # 输入一个列表 view，表示该角色的视野

        # 维度变换 [n_view]-->tensor[1,n_visions]


        # view = torch.tensor(view[np.newaxis, :]).to(self.device)
        # view = 
        # view = torch.tensor(view).to(self.device)
        # view = torch.reshape(view,(1,self.n_view))
        vision = [vision]
        vision = torch.tensor(vision, dtype=torch.float).to(self.device)
        # vision = torch.reshape(vision,(1,self.n_visions))

        # print('take_action',vision)
        # 当前状态下，每个动作的概率分布 [1,n_visions]
        probs = self.actor(vision)
        # 创建以probs为标准的概率分布
        try:
            # raise(BaseException("wefioj"))
            # a = 1/0
            action_list = torch.distributions.Categorical(probs)
        except Exception as ex:
            # print(ex)
            wrong = 1
            return 0,0,wrong
        # 依据其概率随机挑选一个动作
        action = action_list.sample().item()
        return action,probs,0

    # 训练
    def learn(self, transition_dict):


        # print('learn',transition_dict['visions'])
        # 提取数据集
        visions = torch.tensor(transition_dict['visions'], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions']).to(self.device).view(-1,1)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).to(self.device).view(-1,1)
        next_visions = torch.tensor(transition_dict['next_visions'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'], dtype=torch.float).to(self.device).view(-1,1)

        # print('\nlearn')
        # print(visions)
        # print(next_visions)

        # 目标，下一个状态的view_value  [b,1]
        next_q_target = self.critic(next_visions)
        # 目标，当前状态的view_value  [b,1]
        td_target = rewards + self.gamma * next_q_target * (1-dones)
        # 预测，当前状态的view_value  [b,1]
        td_value = self.critic(visions)
        # 目标值和预测值view_value之差  [b,1]
        td_delta = td_target - td_value

        # 时序差分值 tensor-->numpy  [b,1]
        td_delta = td_delta.cpu().detach().numpy()
        advantage = 0  # 优势函数初始化
        advantage_list = []

        # 计算优势函数
        for delta in td_delta[::-1]:  # 逆序时序差分值 axis=1轴上倒着取 [], [], []
            # 优势函数GAE的公式
            advantage = self.gamma * self.lmbda * advantage + delta
            advantage_list.append(advantage)
        # 正序
        advantage_list.reverse()
        # numpy --> tensor [b,1]
        advantage = torch.tensor(advantage_list, dtype=torch.float).to(self.device)

        # 策略网络给出每个动作的概率，根据action得到当前时刻下该动作的概率
        old_log_probs = torch.log(self.actor(visions).gather(1, actions)).detach()

        # 一组数据训练 epochs 轮
        for _ in range(self.epochs):
            # 每一轮更新一次策略网络预测的状态
            log_probs = torch.log(self.actor(visions).gather(1, actions))
            # 新旧策略之间的比例
            ratio = torch.exp(log_probs - old_log_probs)
            # 近端策略优化裁剪目标函数公式的左侧项
            surr1 = ratio * advantage
            # 公式的右侧项，ratio小于1-eps就输出1-eps，大于1+eps就输出1+eps
            surr2 = torch.clamp(ratio, 1-self.eps, 1+self.eps) * advantage

            # 策略网络的损失函数
            actor_loss = torch.mean(-torch.min(surr1, surr2))
            # 价值网络的损失函数，当前时刻的view_value - 下一时刻的view_value
            critic_loss = torch.mean(F.mse_loss(self.critic(visions), td_target.detach()))

            # 梯度清0
            self.actor_optimizer.zero_grad()
            self.critic_optimizer.zero_grad()
            # 反向传播
            actor_loss.backward()
            critic_loss.backward()
            # 梯度更新
            self.actor_optimizer.step()
            self.critic_optimizer.step()
