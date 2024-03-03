import torch
import gym
from matplotlib import pyplot as plt
import argparse
import numpy as np
from torch import nn
from torch.distributions import Categorical
from torch import optim
import time 
import pybullet
import pybulletgym.envs
from torch.distributions import MultivariateNormal
import pickle

showLogs=False

##PARAMS
GAMMA=0.9
EPISODES=500
ITERATIONS=200
LR=0.01
REWARD_ITERS_STOP_THRESHOLD=498

# torch.manual_seed(42)

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




def selectAction(policy_network, state, evalPlcy=False):

	epsilon=1e-3
	probs = policy_network.forward(state)
	cov = torch.abs(policy_network.sigma) + epsilon   
	m = MultivariateNormal(probs, cov)
	action = m.sample()
	logProbs = m.log_prob(action)
	
	if evalPlcy:
		return probs.tolist(), logProbs

	return action.tolist(), logProbs




class Policy(nn.Module):

	def __init__(self, env):

		super(Policy, self).__init__()
		# get state space and action space dimension
		self.obs_space_n = env.observation_space.shape[0] - 1   # should be 8 (TODO: bug in env showing wrong observation space?)
		self.action_space_n = env.action_space.shape[0]   # should be 2
		print("Obs Space {}\n Action Space {}\n".format(self.obs_space_n,self.action_space_n))
		
		# layers
		self.l1 = nn.Linear(self.obs_space_n, 64)
		self.l2 = nn.Linear(64, self.action_space_n)
		self.sigma = nn.Parameter(torch.diag(torch.FloatTensor([0.2, 0.2])))

	def forward(self, x):
		"""
		Feed fwd fn
		"""
		# build neural network
		network = nn.Sequential(
			self.l1,
			nn.Tanh(),
			# self.l2,
			# nn.ReLU(),
			self.l2,
			nn.Tanh())

		return network(torch.FloatTensor(x).to(device))



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

if __name__== "__main__":
	
	## setup gpu/cpu
	isCuda=torch.cuda.is_available()
	if(isCuda):
		deviceName="cuda:0"
	else:
		deviceName="cpu"
	device=torch.device(deviceName)


	parser = argparse.ArgumentParser(None)
	parser.add_argument('--mode', help='1/0 - Test/Train if you want to train the model')
	parser.add_argument("--modelPath", help='defaults to \'./q2Model.pkl\'', default='./ModelPolicy.pkl')

	args = parser.parse_args()
	isTest=(args.mode=="1")
	isTrain=(args.mode=="0")
	modelPath=args.modelPath

	if(isTrain):
		print("***** Training Model *****\n")
		env = gym.make("modified_gym_env:ReacherPyBulletEnv-v1", rand_init=False)

		#setup network
		policy_network = Policy(env).to(device)
		average_reward_list = trainTwo(env, policy_network,device,episodeCount=500, iterCount=200,lr=0.01, gamma=0.9)
		print(average_reward_list)

		# save model
		with open('q2Model.pkl', 'wb') as pickle_file:
			pickle.dump(policy_network, pickle_file)

		print("Training Done - Saved Model: q2Model.pkl\n") 
		plot1Fgr(average_reward_list,"figr 1")

	if(isTest):
		print("***** Testing Model *****\n")
		print("Training- Using pre trained {} model \n".format(modelPath))

		env = gym.make("modified_gym_env:ReacherPyBulletEnv-v1", rand_init=False)
		env.render(mode='human')
		state = env.reset()
		pybullet.resetDebugVisualizerCamera(2, 5, -80, np.array([0,0,0]))
		
		# load policy
		with open(modelPath, 'rb') as pickle_file:
			policy_network = pickle.load(pickle_file)		

		done = False
		steps = 0
		time.sleep(3)

		while not done:
			action, log_prob = selectAction(policy_network, state, evalPlcy=True)
			print(action)
			state_next, reward, done, _ = env.step(action)
			env.render(mode='human')
			steps += 1
			state = state_next
			time.sleep(0.1)

		print('Finished in {} steps'.format(steps))
		time.sleep(10)