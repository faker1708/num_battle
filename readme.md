
强化学习_多阵营对抗_初涉
2023_0514

运行环境 （充分非必要）
win11
miniconda3
cuda 11.7
python 3.9
torch 1.13.1+cu117

执行
python run_this.py


写一个简单的对战游戏

两个阵营，每个阵营一个角色。

每人每回合采取一个行动。

甲方 0123 对应 1357

乙方 0123 对应 2468

这是不公平的有限时间内的零和博弈

然后 谁大谁就赢





有限时间，不公平，零和游戏

比如围棋







没有找到合并起来的ac代码

把store函数封装一下

中途reward 肯定不给了。但是计0 还是计 结局时的奖励呢？




不行。不可靠
<!-- 随机探索是有效的。也不一定会像之前 那个围棋一样导致网络损坏
                # action = random.randint(0,self.n_actions-1) -->


我验证了，一个已经学坏了的ppo，它是不会再自发地学好的。
原理也很简单，好的决策的概率已经接近0了，它不会再尝试了。自然即使可能拿到奖励，它也不会尝试。
这时，可以通过随机探索的方法来让它学好。


但是随机取值网络会损坏。



1   训练 时应当加入随机探索，但容易损坏网络，要怎么办？
2   动态学习，加速收敛
3   延时奖励。决策若干次，随机取一次作为判据，结束时才发奖励。


