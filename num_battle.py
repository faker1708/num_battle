
# # 前端
# import pygame
# import time
# import sys


# # 后端
# import math
# import copy

class num_battle():



    def __init__(self):
        self.view_dimension = 1    # 没有状态
        self.action_dimension = 2**2
        self.flag_quantity = 2 # 几个队伍
        self.team_volume = 1    # 一个队伍几个人

    
    def reset(self):

        flag = 1
        view = list()
        view.append(0)
        view.append(88)

        self.now_playing_flag = 1

        self.__status = [-1,-1,-1]  #记录每个阵营出的牌

        self.__step = 0
        self.__terminal_step = 1    # 设置强制结局回合数 设置为-1 则不用回合数限制结局

        flag = self.now_playing_flag
        
        done = list()
        done.append(0)  # 额外补一个空阵营
        for id in range(self.flag_quantity):
            done.append(0)
        self.done = done

        return view,flag

    def liquidate(self):
        # 当所有玩家都结局时,计算各个阵营的分数

        # 初始化输出值
        score = list()
        score.append(0)  # 额外补一个空阵营
        for id in range(self.flag_quantity):
            score.append(0)

        #
        sa = self.__status[1]
        sb = self.__status[2]
        if(sa>sb):
            score[1]=1
        else:
            score[2]=1
        
        return score,self.__status
        




    def step(self,action):

        # 初始化输出值


        flag = self.now_playing_flag 
        status = self.__status


        # 执行玩家的决策，修改游戏状态

        fa = -1
        if(flag==1):
            fa = 2*action +1
        else:
            fa = 2*action +2
        status[flag] = fa


        




        if(flag == self.flag_quantity):
            # 所有玩家都执行一次后，step+1
            self.__step +=1

        termi = 0
        if(self.__terminal_step >=0):
            if(self.__step >=self.__terminal_step ):
                # for iid,dd in enumerate(done):
                    # done[iid]=1
                    termi = 1

        # if(self.__terminal_step >=0):
        #     if(self.__step >=self.__terminal_step ):




        # 切换阵营
        flag = 3-flag



        self.now_playing_flag = flag 
        self.__status = status  # 提交


        next_flag = flag   # 12阵营交替
        
        next_view = list()
        next_view.append(0)
        next_view.append(77)

        return next_view,next_flag,termi