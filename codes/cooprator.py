from config import NUMBER_OF_AGENTS, MODEL_PATH, AGREEGATION, MODEL_SELECTION,POLICY_UPDATE_RATE
from clientselection import policygradient 
import numpy as np
class cooprator:
    def __init__(self) -> None:
        self.is_ready=False
        self.number_of_agents=NUMBER_OF_AGENTS
        self.roh=0.9
        if MODEL_SELECTION=='policy_gradient_method':
            self.update_counter=0
            self.reset_experience()
            self.graph={'agent1':['agent1','agent2','agent3','agent4','agent5'],
                        'agent2':['agent1','agent2','agent3'],
                        'agent3':['agent1','agent2','agent3','agent4','agent5'],
                        'agent4':['agent1','agent2','agent3','agent4'],
                        'agent5':['agent1','agent3','agent5']}
            self.agents_policy=[policygradient(numberOfAgents=len(self.graph[key])) for key in self.graph.keys()]
        # if AGREEGATION=='weightedAveraging':
        #     self.A=[[0.5,0.5],[0.5,0.5]]
    def reset_experience(self):
        self.states={'agent1':[],
                   'agent2':[],
                   'agent3':[],
                   'agent4':[],
                   'agent5':[]}
        self.actions={'agent1':[],
                   'agent2':[],
                   'agent3':[],
                   'agent4':[],
                   'agent5':[]}
        self.rewards={'agent1':[],
                   'agent2':[],
                   'agent3':[],
                   'agent4':[],
                   'agent5':[]}
    def fedavg_aggregate(self,agents_weights,total_rewards):
        model_weights=[]
        for i in range(len(agents_weights[0])):
            layer_weights=[]
            for ag in range(self.number_of_agents):
                layer_weights.append(agents_weights[ag][i]*total_rewards[ag])
            model_weights.append(sum(layer_weights)/sum(total_rewards))
        self.last_weights=model_weights
    def fedADMM_aggregate(self,agents_weights,y_k):
        model_weights=[]
        for i in range(len(agents_weights[0])):
            layer_weights=[]
            for ag in range(self.number_of_agents):
                layer_weights.append(agents_weights[ag][i])
                layer_weights.append(y_k[ag][i]/self.roh)
            model_weights.append(sum(layer_weights)/self.number_of_agents)
        self.last_weights=model_weights
        model1_weights=[]
        model2_weights=[]
        for ag in range(self.number_of_agents):
            layer_weights=[]
            for i in range(len(agents_weights[0])):
                layer_weights=y_k[ag][i]+self.roh*(agents_weights[ag][i]-self.last_weights[i])
                if ag==0:
                    model1_weights.append(layer_weights/self.number_of_agents)
                elif ag==1:
                    model2_weights.append(layer_weights/self.number_of_agents)
        self.yk_1=model1_weights
        self.yk_2=model2_weights
    def weightedAveraging(self,agents_weights,states=None):
        weights=[]
        if MODEL_SELECTION=='policy_gradient_method':
            state=[]
            for key in self.graph.keys():
                s=[]
                other_rewards=[]
                for val in self.graph[key]:
                    if val==key:
                        agent_reward=states[val][0]
                    else:
                        other_rewards.append(states[val][0])
                    s=s+states[val]
                state.append(s)
                self.states[key].append(state)
                reward=agent_reward-sum(other_rewards)/len(other_rewards)
                self.rewards[key].append(reward)
            self.agent_selection(state)
        for ag2,agent in enumerate(self.graph.keys()):
            model_weights=[]
            for i in range(len(agents_weights[0])):
                tmp=[self.A[ag2][ag1]*agents_weights[ag1][i] for ag1 in range(len(self.graph[agent]))]
                model_weights.append(sum(tmp))
            weights.append(model_weights)
        self.update_counter+=1
        if self.update_counter%POLICY_UPDATE_RATE==0:
            [agent.train_model() for agent in self.agents_policy]
            self.reset_experience()
        return weights
    def agent_selection(self,states):
        self.A=[]
        for i,agent in enumerate(self.agents_policy):
            actions,dist=agent.sellect_action(states[i])
            self.actions[list(self.graph)[i]].append(actions)
            selected_prob=np.zeros(self.number_of_agents)
            selected_prob[actions]=dist[actions]
            selected_prob/=selected_prob.sum()
            self.A.append(selected_prob)
        
    @staticmethod
    def save_model(model):
        model.save(MODEL_PATH+'/model.h5')