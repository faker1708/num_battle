

# 本埠

# 人工智能
import ppo

# 游戏
import num_battle



# 外埠


# 人工智能
# 删除
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

import matplotlib.pyplot as plt


import os

import random
import pickle


class dva_train():

    def simulate(self,mode,num_episode):

        # 后端 
        game = self.game
        
        agent_list = self.agent_list

        score_sum = [-1,0,0]
        # 开启新的对局
        for i in range(num_episode):
            # 新的对局

            # 后端
            view,flag = game.reset()

            # 构造数据集，保存每个回合的状态数据
            transition_dict_1 = {
                'views': [],
                'actions': [],
                'next_views': [],
                'rewards': [],
                'dones': [],
            }
            transition_dict_2 = {
                'views': [],
                'actions': [],
                'next_views': [],
                'rewards': [],
                'dones': [],
            }
            transition_dict_list = list()
            transition_dict_list.append(0)
            transition_dict_list.append(transition_dict_1)
            transition_dict_list.append(transition_dict_2)

            # 每局游戏时，选择一个智能体参战
            flag1x = random.randint(0,self.agent_quantity_per_flag-1)
            flag2x = random.randint(0,self.agent_quantity_per_flag-1)
            cf = [0,flag1x,flag2x]

            opponent_list= list()  # 随机从两个阵营各选两个棋手
            opponent_list.append(0)
            opponent_list.append(self.agent_list[1][flag1x])
            opponent_list.append(self.agent_list[2][flag2x])

            while(1):   # 游戏中
                
                agent = opponent_list[flag]
                view = np.array([view])
                action,prob,wrong = agent.take_action(view)
                # if(flag ==2):
                #     print('prob',prob)
                if(wrong==1):return 0,wrong

                next_view,next_flag,terminal = game.step(action)


                transition_dict_list[flag]['views'].append(view)
                transition_dict_list[flag]['actions'].append(action)
                transition_dict_list[flag]['next_views'].append(next_view)
                transition_dict_list[flag]['rewards'].append(0)    # 对局结束前不给奖励
                transition_dict_list[flag]['dones'].append(0)

                # terminal = all(done)


                if(terminal):
                    # result = game.result()   # 查看各家得分多少          查看谁是赢家  # 零和游戏
                    score,game_status = game.liquidate()

                    # if(score[2]==0):
                    #     print('score',score,game_status)
                    print('score',score,game_status)
                    
                    transition_dict_list[1]['rewards'][-1]= score[1]
                    transition_dict_list[2]['rewards'][-1]= score[2]
                    # transition_dict_list[2]['rewards'].append(score[2])
                    transition_dict_list[1]['dones'][-1]=1
                    transition_dict_list[2]['dones'][-1]=1
                    # transition_dict_list[2]['dones'].append(1)

                    score_sum[1]+=score[1]
                    score_sum[2]+=score[2]
                    break
                else:
                    view = next_view
                    flag = next_flag
            # while(1) end 
            
            # 游戏结束

            # 用结局的分评价该智能体的所有行为。
            # for flag in range(1,self.game.flag_quantity):
            #     # flag = 1+fi
            #     l_rewards = transition_dict_list[flag]['rewards']
            #     for ii ,ele in enumerate(l_rewards):
            #         # if(l_flag[ii]==winner):  # 如果这样下能赢，就给1的奖励
            #             l_rewards[ii]=result[flag]
            
            # 学习
            for ff in range(0,self.game.flag_quantity):
                flag = ff+1
                # print(flag)
                flag_x = cf[flag]    # 它是flag阵营中的第几个军师？
                agent = agent_list[flag][flag_x]
                experience = transition_dict_list[flag]

                if(flag ==2):
                    # print(experience)
                    pass
                agent.learn(experience)



            # for ia,agent in enumerate(component_list):
            #     if(ia>=1):
            #         if(not kk):
            #             agent.learn(transition_dict_list[ia])

        wrong = 0
        s1m = score_sum[1]/num_episode
        return s1m,wrong

    def main(self):
        # 前端
        plt_on  = 1

        # 人工智能 参数
        agent_quantity_per_flag = 2**0  # 每个阵营有几个军师
        n_views  = 1
        n_actions = 2**2

        device = torch.device('cuda') if torch.cuda.is_available() \
                                    else torch.device('cpu')

        game = num_battle.num_battle()



        self.game = game
        self.agent_quantity_per_flag = agent_quantity_per_flag
        
        ie = 0        

        save_pace = 5
        folder_path = './model'
        while(1):
            # print("\n\n")
            if(plt_on ==1):
                t_list = list()
                black_win_rate_list = list()
                plt.close()
            files= os.listdir(folder_path)
            if(files):
                load = 1
                # print('files',files)
                max = -1
                ln = list()
                for _,ele in enumerate(files):
                    num = int(ele.split('.')[0])
                    ln.append(num)
                    # if(num>max):
                        # max = num
                ln.sort()
                # print(ln)
                if(1 <= len(files)):
                    ie = ln[-1]
                else:
                    ie = 0

            else:
                load= 0
                ie = 0
            if(load):
                    # print(int(num),'wefwef')
                # ie = 96
                # print('load',ie)
                with open('./model/'+str(ie)+'.pkl', "rb") as f:
                    self.agent_list = pickle.load(f)
            else:
                print('new')
                self.agent_list = list()
                self.agent_list.append(0)   # 0阵营是空的，不需要棋手

                for _ in range(0,2):
                    flag_x_player_list = list()
                    for j in range(0,agent_quantity_per_flag):
                        ax = ppo.ppo(n_views=n_views,  # 状态数
                            n_actions=n_actions,  # 动作数
                            actor_lr=1e-3,  # 策略网络学习率
                            critic_lr=1e-2,  # 价值网络学习率
                            lmbda = 0.95,  # 优势函数的缩放因子
                            epochs = 10,  # 一组序列训练的轮次
                            eps = 0.2,  # PPO中截断范围的参数
                            gamma=0.9,  # 折扣因子
                            device = device
                            )
                        flag_x_player_list.append(ax)
                    self.agent_list.append(flag_x_player_list)

                ie = 0        

            black_win_rate = 0.5
            while(1):
                ie = ie + 1
                # print(ie)
                black_win_rate,wrong = self.simulate('train',2**4)
                if(wrong):
                    save_pace -= 1                   
                    if(save_pace<=0):
                        files= os.listdir(folder_path)
                        # ln = list()
                        max = -1
                        for _,ele in enumerate(files):
                            num = int(ele.split('.')[0])
                            # ln.append(num)
                            if(num>max):
                                max = num
                        if(max>0):
                            last_file = folder_path+'/'+str(max)+'.pkl'
                            os.remove(last_file)
                            # print('remove',last_file)
                        save_pace = 5
                        break

                    # print('meet wrong',save_pace) 
                    
                    if(plt_on ==1):
                        t_list = list()
                        black_win_rate_list = list()
                        plt.close()

                    break


                # w,wr = self.simulate('show',2**0)


                # print('w',w)
                # if(w==1):
                #     print('1')
                # else:
                #     print('2')


                if(ie % 2**save_pace==0):
                    with open('./model/'+str(ie)+'.pkl', "wb") as f:
                            pickle.dump(self.agent_list, f)
                    # print('\n')
                    print('save',ie,black_win_rate)
                    # print('\n')
                    # print(ie,black_win_rate)
                    
                    if(plt_on ==1):
                        plt.close()
                        t_list = list()
                        black_win_rate_list = list()

                    # save_pace +=1
                    # if(save_pace>5):save_pace = 5
                    save_pace = 5
                
                # print('black_win_rate',black_win_rate)
                if(plt_on ==1):
                    t_list.append(ie)
                    black_win_rate_list.append(black_win_rate)
                    
                    # if(black_win_rate==0 or black_win_rate==1):
                    if(1):
                        print(ie,black_win_rate)
                    # print(t_list,black_win_rate_list)
                    # print(t_list[-1],black_win_rate_list[-1])
                    plt.plot(t_list,black_win_rate_list,c='blue')
                    plt.pause(0.001)

        return

    def __init__(self):
        self.main()
        return
    

if __name__ == "__main__":
    dva_train()