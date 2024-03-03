import torch
import gym
from matplotlib import pyplot as plt
import argparse
import numpy as np
from torch import nn
from torch.distributions import Categorical
from torch import optim
import time 

## Logging Setup
import logging
LOG_FILE = "main3.log"
LOG_FILE_Q1 = "q1.log"
LOG_FILE_Q2 = "q2.log"
LOG_FILE_Q3 = "q3.log"
LOG_FILE_Q4 = "q4.log"
LOG_MODE="a"
FORMATTER1 = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
FORMATTER2 = "%(asctime)s — %(levelname)s — %(message)s"
FORMATTER3 = "%(asctime)s — %(message)s"

showLogs=False


## PARAMS
GAMMA=0.99
LR=0.01
EPISODES=500
ITERATIONS=200

#### Utils Start ####


def plot1Fgr(lst, title, name="fig"):
	plt.figure()
	plt.plot(lst)
	plt.xlabel('Iteration')
	plt.ylabel('Mean Reward')
	plt.title(title)
	name=name+'.png'
	plt.savefig(name)
	plt.show()
	

def plot2Fgr(l1,l2, title, name="fig"):
	plt.figure()
	plt.plot(l1)
	plt.plot(l2)
	plt.xlabel('Iteration')
	plt.ylabel('Mean Reward')
	plt.title(title)
	name=name+'.png'
	plt.savefig(name)
	plt.show()

def plot3Fgr(l1,l2,l3, title, name="fig"):
	plt.figure()
	plt.plot(l1)
	plt.plot(l2)
	plt.plot(l3)
	plt.xlabel('Iteration')
	plt.ylabel('Mean Reward')
	plt.title(title)
	name=name+'.png'
	plt.savefig(name)
	plt.show()




# functions
## Ref - https://pytorch.org/docs/stable/distributions.html
def selectAction(plcyNet, state, dv):
	p=plcyNet.forward(state,dv)
	cat=Categorical(p)
	act=cat.sample()
	logProb=cat.log_prob(act)
	return act.item(),logProb

# classes
class Policy(nn.Module):
	"""
	Policy Network 
	"""
	def __init__(self, env, dv):
		"""
		:param env: object, gym env, device
		"""
		layerDims=48
		self.device=dv
		super(Policy, self).__init__()
		# get state space and action space dimension
		self.obs_space_n = env.observation_space.shape[0]
		self.action_space_n = env.action_space.n

		print("Obs Space:{}\n Action Space:{}\n".format(self.obs_space_n,self.action_space_n))

		self.l1 = nn.Linear(self.obs_space_n,layerDims)
		self.l2 = nn.Linear(layerDims, self.action_space_n)

	def forward(self, x, dv):
		
		## Feed forward fn
		
		# build nn
		network = nn.Sequential(self.l1,nn.ReLU(),self.l2,nn.Softmax(dim=-1))
		return network(torch.FloatTensor(x).to(self.device))

def trainOne(env,plcy,dv,log=None,episodeCount=EPISODES,iterCount=ITERATIONS, lr=LR, gamma=GAMMA):
	rewardsPerIter=np.zeros(iterCount)
	optimizer=optim.Adam(plcy.parameters(),LR)
	
	for iter in range(iterCount):
		totalReward=0
		loss=torch.tensor(0.0).to(dv)

		for episode in range(episodeCount):
			state=env.reset()
			logEp=[]
			rewardEp=[]

			time=0
			while True:
				action,logPi=selectAction(plcy,state,device)
				nextState,reward,done,info=env.step(action)
				
				## store log prob and rewards
				logEp.append(logPi)
				rewardEp.append(reward)
				state=nextState

				if done:
					break
				time+=1
			
			## convert to a vertical vec
			logProbTime=torch.stack(logEp).to(dv)
			## here its excluding T as it runs from 0 to T-1 but its fine. Trend is not affected
			rewardTime=torch.tensor([(GAMMA**i)*(rew) for i, rew in enumerate(rewardEp)])

			## Q1.1 Equation Sum(GT*LogProbs)
			loss-= (rewardTime.sum() * logProbTime.sum())
			totalReward+=sum(rewardEp)
		
		loss=loss/episodeCount
		loss.backward()
		optimizer.step()
		optimizer.zero_grad()
		rewardsPerIter[iter]=(totalReward/episodeCount)
		status='Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item())
		print(status)
		if(log):
			log.info(status)
		# print('Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item()))
	log.info(rewardsPerIter)
	return rewardsPerIter


def trainTwo(env,plcy,dv,log=None,episodeCount=EPISODES,iterCount=ITERATIONS, lr=LR, gamma=GAMMA):
	rewardsPerIter=np.zeros(iterCount)
	optimizer=optim.Adam(plcy.parameters(),LR)
	
	for iter in range(iterCount):
		totalReward=0
		loss=torch.tensor(0.0).to(dv)

		for episode in range(episodeCount):
			state=env.reset()
			logEp=[]
			rewardEp=[]
			
			## Episode Start 
			time=0
			while True:
				action,logPi=selectAction(plcy,state,device)
				nextState,reward,done,info=env.step(action)
				
				## store log prob and rewards
				logEp.append(logPi)
				rewardEp.append(reward)
				state=nextState

				if done:
					break
				time+=1
			
			## Episode Completed 

			TProd=0
			localSum=0
			for t in range(time):
				_T1=0
				_T2=0
				_T1=logEp[t]
				## find T2
				for t_dash in range(t,time):
					_T2+=((GAMMA**(t_dash-t))*rewardEp[t_dash])
				TProd=_T1*_T2
				localSum+=TProd
			loss-=localSum
			totalReward+=sum(rewardEp)
		# loss=loss/episodeCount
		loss=loss/episodeCount
		loss.backward()
		optimizer.step()
		optimizer.zero_grad()
		rewardsPerIter[iter]=(totalReward/episodeCount)
		status='Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item())
		print(status)
		if(log):
			log.info(status)
		# print('Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item()))
	log.info(rewardsPerIter)
	return rewardsPerIter
		
def trainThree(env,plcy,dv,log=None,episodeCount=EPISODES,iterCount=ITERATIONS, lr=LR, gamma=GAMMA):
	rewardsPerIter=np.zeros(iterCount)
	optimizer=optim.Adam(plcy.parameters(),LR)
	
	for iter in range(iterCount):
		totalReward=0
		loss=torch.tensor(0.0).to(dv)

		for episode in range(episodeCount):
			state=env.reset()
			logEp=[]
			rewardEp=[]
			
			## Episode Start 
			time=0
			while True:
				action,logPi=selectAction(plcy,state,device)
				nextState,reward,done,info=env.step(action)
				
				## store log prob and rewards
				logEp.append(logPi)
				rewardEp.append(reward)
				state=nextState

				if done:
					time+=1
					break
				time+=1
			
			## Episode Completed 
			TProd=0
			localSum=0
			for t in range(time):
				##Term 1 and Term 2 in formula
				_T1=0
				_T2=0
				_T2Vec=[]
				_T1=logEp[t]
				## find T2
				for t_dash in range(t,time):
					_T2Vec.append((GAMMA**(t_dash-t))*rewardEp[t_dash])
				b=np.mean(_T2Vec)
				## is array has 1 element std is 0-> division by 0 in formula
				if(len(_T2Vec)==1):
					sigma=1
				else:
					sigma=np.std(_T2Vec)
				_T2Vec=torch.tensor(_T2Vec)
				# _T2Vec-=b
				_T2=(torch.sum(_T2Vec)-b)/sigma
				TProd= _T1*_T2
				localSum+=TProd
			loss=localSum
			totalReward+=sum(rewardEp)
		loss=loss/episodeCount
		loss.backward()
		optimizer.step()
		optimizer.zero_grad()
		rewardsPerIter[iter]=(totalReward/episodeCount)
		status='Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.10f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item())
		print(status)
		if(log):
			log.info(status)
		# print('Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item()))
	log.info(rewardsPerIter)
	return rewardsPerIter
		
		
def trainThreeThreeMain(env,plcy,dv,log=None,episodeCount=500,iterCount=200, lr=LR, gamma=GAMMA):
	rewardsPerIter=np.zeros(iterCount)
	optimizer=optim.Adam(plcy.parameters(),LR)
	
	for iter in range(iterCount):
		totalReward=0
		loss=torch.tensor(0.0).to(dv)

		logProbsAllEpisodes=[]
		forwardRewardAllEpisodes=[]
		policyLossForIters=[]

		for episode in range(episodeCount):
			state=env.reset()
			logEp=[]
			rewardEp=[]
			
			## Episode Start 
			time=0
			epRewardSum=0
			while True:
				action,logPi=selectAction(plcy,state,device)
				nextState,reward,done,info=env.step(action)
				
				## store log prob and rewards
				logEp.append(logPi)
				rewardEp.append(reward)
				state=nextState

				if done:
					time+=1
					break
				time+=1
			## Episode Completed 
			if(showLogs):
				print("time {} rew len {}".format(time,len(rewardEp)))
			epFutureRewardSums=[]
			if(showLogs):
				print("\n\n**** NEW EP****\n")
			for t in range(time):
				##contains [future reward sum for t=0, future reward sum for t=1,..... , T]
				if(showLogs):
					print(t)
					print("time range {} reward len {}\n".format(len(range(0,time-t)),len(rewardEp[t:time])))
					print([ele for ele in zip(range(0,time-t),rewardEp[t:time])])
				sumVal=sum([ (GAMMA**power)*rwd for (power,rwd) in zip(range(0,time-t),rewardEp[t:time])])
				if(showLogs):
					print("sum {}\n".format(sumVal))
				epFutureRewardSums.append(sum([ (GAMMA**power)*rwd for (power,rwd) in zip(range(0,time-t),rewardEp[t:time])]))
			
			epFutureRewardSums=torch.FloatTensor(epFutureRewardSums).to(device)
			logProbsAllEpisodes.append(logEp)
			forwardRewardAllEpisodes.append(epFutureRewardSums)
			# print("future reward {} \n\n".format(forwardRewardAllEpisodes))
			totalReward+=sum(rewardEp)

		rewardsPerIter[iter]=(totalReward/episodeCount)
		forwardRewardsForIteration= torch.cat(forwardRewardAllEpisodes)
		mu=forwardRewardsForIteration.mean()
		std=forwardRewardsForIteration.std()

		## now implement the formula 
		for logPiArray,futureRewards in zip(logProbsAllEpisodes,forwardRewardAllEpisodes):
			##normalize
			futureRewards=(futureRewards-mu)/std
			policyLossForEP=[]
			if(showLogs):
				print("logPi len {} _futureReward Len {}\n".format(len(logPiArray),len(futureRewards)))
			for logPi,_futureRewardSum in zip(logPiArray,futureRewards):
				if(showLogs):
					print("log pi val {} - ftr rwd array {}\n".format(logPi,_futureRewardSum))
				policyLossForEP.append(-logPi*_futureRewardSum)
			policyLossForEP=torch.stack(policyLossForEP).to(device)
			policyLossForIters.append(policyLossForEP)
		
		
		for epVec in policyLossForIters:
			loss+=torch.sum(epVec)

		loss=(loss)/episodeCount
		loss.backward()
		optimizer.step()
		optimizer.zero_grad()
		status='Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.10f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item())
		print(status)
		if(log):
			log.info(status)
	
		# print('Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item()))
	if(log):		
		log.info(rewardsPerIter)
	return rewardsPerIter

	
def trainThreeTwo(env,plcy,dv,log=None,episodeCount=EPISODES,iterCount=ITERATIONS, lr=LR, gamma=GAMMA):
	exit(1)
	rewardsPerIter=np.zeros(iterCount)
	optimizer=optim.Adam(plcy.parameters(),LR)
	
	for iter in range(iterCount):
		totalReward=0
		loss=torch.tensor(0.0).to(dv)
		episodeLogPis=[]
		episodeRewards=[]
		episodeFutureRewards=[]

		for episode in range(episodeCount):
			state=env.reset()
			logEp=[]
			rewardEp=[]
			
			## Episode Start 
			time=0
			while True:
				action,logPi=selectAction(plcy,state,device)
				nextState,reward,done,info=env.step(action)
				
				## store log prob and rewards
				logEp.append(logPi)
				rewardEp.append(reward)
				state=nextState

				if done:
					time+=1
					break
				time+=1
			
			## for this episode whats the future reward array
			thisEpFutureRewards=[]
			for t in range(time):
				_FT_REWARD=[(GAMMA**power)*rwd for power,rwd in zip(range(time-t),rewardEp[t:time])]
				thisEpFutureRewards.append(_FT_REWARD)
			episodeFutureRewards.append(thisEpFutureRewards)
			episodeLogPis.append(logEp)
			episodeRewards.append(rewardEp)
		
		
		for epIdx in range(episodeCount):
			logPisForEp=episodeLogPis[epIdx]
			for logPi in logPisForEp:
				_T1=logPi
				_T2=None


			## Episode Completed 
			TProd=0
			localSum=0
			for t in range(time):
				##Term 1 and Term 2 in formula
				_T1=0
				_T2=0
				_T2Vec=[]
				_T1=logEp[t]
				## find T2
				for t_dash in range(t,time):
					_T2Vec.append((GAMMA**(t_dash-t))*rewardEp[t_dash])
				b=np.mean(_T2Vec)
				## is array has 1 element std is 0-> division by 0 in formula
				if(len(_T2Vec)==1):
					sigma=1
				else:
					sigma=np.std(_T2Vec)
				_T2Vec=torch.tensor(_T2Vec)
				# _T2Vec-=b
				_T2=(torch.sum(_T2Vec)-b)/sigma
				TProd= _T1*_T2
				localSum+=TProd
			loss-=localSum
			totalReward+=sum(rewardEp)
		loss=loss/episodeCount
		loss.backward()
		optimizer.step()
		optimizer.zero_grad()
		rewardsPerIter[iter]=(totalReward/episodeCount)
		status='Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.10f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item())
		print(status)
		if(log):
			log.info(status)
		# print('Iter ({}/{}) Mean Reward: {:.2f}, Loss: {:.2f}'.format(iter+1, iterCount, rewardsPerIter[iter], loss.item()))
	log.info(rewardsPerIter)
	return rewardsPerIter
		

#### Utils End ####


if __name__== "__main__":
	parser = argparse.ArgumentParser(None)
	parser.add_argument('--qn', help='question no.')
	args = parser.parse_args()
	qn=args.qn

	## setup gpu/cpu
	isCuda=torch.cuda.is_available()
	if(isCuda):
		deviceName="cuda:0"
	else:
		deviceName="cpu"
	device=torch.device(deviceName)
	

	## setup env
	envName="CartPole-v1"
	env=gym.make(envName)
	## init state
	state=env.reset()

	plcy=Policy(env,device).to(device)

	if(qn=="22"):
		logging.basicConfig(filename=LOG_FILE_Q2,format=FORMATTER2,filemode=LOG_MODE,level=logging.INFO)
		logger2 = logging.getLogger()
		logger2.info("Q1.2")

		# avgRwdListOne=trainOne(env,plcy,device, logger2)
		avgRwdListTwo=trainTwo(env,plcy,device,logger2)
		plot1Fgr(avgRwdListTwo, "'Average Rewards in each iteration","q2-"+time.asctime(time.localtime()))
		logger2.info(avgRwdListTwo)

	if(qn=="1.1"):
		logging.basicConfig(filename=LOG_FILE_Q1,format=FORMATTER2,filemode=LOG_MODE,level=logging.INFO)
		logger1 = logging.getLogger()
		logger1.info("Q1.1")

		avgRwdListOne=trainOne(env,plcy,device, logger1)
		plot1Fgr(avgRwdListOne, "'Average Rewards in each iteration", "q1-"+time.asctime(time.localtime()))
		logger1.info(avgRwdListOne)

	if(qn=="1.2"):
		logging.basicConfig(filename=LOG_FILE_Q2,format=FORMATTER2,filemode=LOG_MODE,level=logging.INFO)
		logger2 = logging.getLogger()
		logger2.info("Q1.2")

		avgRwdListTwo=trainTwo(env,plcy,device,logger2)
		plot1Fgr(avgRwdListTwo, "'Average Rewards in each iteration","q2-"+time.asctime(time.localtime()))
		logger2.info(avgRwdListTwo)

	if(qn=="1.3"):
		logging.basicConfig(filename=LOG_FILE_Q3,format=FORMATTER2,filemode=LOG_MODE,level=logging.INFO)
		logger3 = logging.getLogger()
		logger3.info("Q1.3")

		avgRwdListThree=trainThreeThreeMain(env,plcy,device,logger3)
		plot1Fgr(avgRwdListThree, "'Average Rewards in each iteration","q3-"+time.asctime(time.localtime()))
		logger3.info(avgRwdListThree)

	if(qn=="1.4"):
		logging.basicConfig(filename=LOG_FILE_Q4,format=FORMATTER2,filemode=LOG_MODE,level=logging.INFO)
		logger4 = logging.getLogger()

		logger4.info("Q1.4E100")
		avgRwdListThreeEp100=trainThreeThreeMain(env,plcy,device,logger4,episodeCount=100)
		print(avgRwdListThreeEp100)
		logger4.info(avgRwdListThreeEp100)
		print("\nCompleted Ep100\n")

		logger4.info("Q1.4E300")
		avgRwdListThreeEp300=trainThreeThreeMain(env,plcy,device,logger4,episodeCount=300)
		print(avgRwdListThreeEp300)
		logger4.info(avgRwdListThreeEp300)
		print("\nCompleted Ep300\n")

		logger4.info("Q1.4E1000")
		avgRwdListThreeEp1000=trainThreeThreeMain(env,plcy,device,logger4,episodeCount=1000)
		print(avgRwdListThreeEp1000)
		logger4.info(avgRwdListThreeEp1000)
		print("\nCompleted Ep1000\n")

		plot3Fgr(avgRwdListThreeEp100,avgRwdListThreeEp300,avgRwdListThreeEp1000, "Average Rewards in each iteration- EP 100,300,1000")
		logger4.info("*************")

		# plot3Fgr(avgRwdListThreeEp100,avgRwdListThreeEp300,avgRwdListThreeEp1000, "q4-"+time.asctime(time.localtime()))