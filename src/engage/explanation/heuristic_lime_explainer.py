import copy
import numpy as np

from engage.decision_maker.engage_state import EngageState
from engage.explanation.engage_state_observation import EngageStateObservation
from engage.decision_maker.decision_manager import DecisionManager
from engage.decision_maker.heuristic_decision import HeuristicDecision

import lime.lime_tabular

class HeuristicLimeExplainer:
    def __init__(self,decision_maker) -> None:
        self.decision_maker = decision_maker

    def setup_explanation(self,decision_state_msg,query=None,decision_maker="heuristic"):
        self.state,self.bodies = EngageState.single_state_from_msg(decision_state_msg)
        self.discrete_state = EngageState.discretise(self.state,self.bodies)
        self.true_observation = EngageStateObservation(self.discrete_state,self.bodies)
        self.true_outcome = DecisionManager.decision_outcomes[decision_maker](decision_state_msg.decision)

        # Vector stuff
        self.indices = copy.deepcopy(self.state)
        self.vector_vars = []
        self.var_names = []
        i = 0
        for key in self.state:
            for var in self.state[key]:
                self.indices[key][var] = i
                self.vector_vars.append((key,var))
                self.var_names.append("{}_{}".format(key,var))
                i += 1
        self.num_vars = len(self.var_names)

        i = 0
        self.action_indices = {}
        self.vector_actions = []
        self.action_names = []
        
        for action in HeuristicDecision.takes_target:
            self.action_indices[action] = {}
            if HeuristicDecision.takes_target[action]:
                for body in self.bodies:
                    self.action_indices[action][body] = i
                    self.vector_actions.append((action,body))
                    self.action_names.append("{}_{}".format(HeuristicDecision.action_names[action],body))
                    i += 1
            else:
                self.action_indices[action] = i
                self.vector_actions.append((action,None))
                self.action_names.append("{}".format(HeuristicDecision.action_names[action]))
                i += 1
        self.num_actions = len(self.vector_actions)

        self.true_state_vec = self.state_to_vec(self.state)
        self.true_decision_vec = self.decision_to_vec(self.true_outcome)
        self.training_set = self.fabricate_training_set()
        self.explainer = lime.lime_tabular.LimeTabularExplainer(self.training_set, feature_names=self.var_names, class_names=self.action_names, discretize_continuous=True)

    def explain(self,**kwargs):
        exp = self.explainer.explain_instance(self.true_state_vec, self.predict, num_features=6, top_labels=1)
        print(exp)

    def fabricate_training_set(self):
        # TODO
        pass

    def predict(self,feature_vector):
        state = self.vec_to_state(feature_vector)
        decision_state = EngageState()
        decision_state.dict_to_state(state,self.bodies)

        decision = self.decision_maker.decide(decision_state)
        dec_vec = self.decision_to_vec(decision)
        probs = np.zeros((5000,self.num_actions))
        probs[0,:] = dec_vec
        return probs
        

    def state_to_vec(self,state):
        vec = []
        for state_var in self.vector_vars:
            vec.append(state[state_var[0]][state_var[1]])
        return np.array(vec)
    
    def vec_to_state(self,vector):
        print(self.num_vars,self.num_actions)
        state = copy.deepcopy(self.state)
        for row in range(5000):
            print(vector[row,:])
        vector = vector[0,:]
        for i in range(len(vector)):
            var = self.vector_vars[i]
            # TODO: Undiscretise
            state[var[0]][var[1]] = vector[i]
        return state
    
    def decision_to_vec(self,decision):
        action_vector = np.zeros(self.num_actions)
        if HeuristicDecision.takes_target[decision.action]:
            action_vector[self.action_indices[decision.action][decision.target]] = 1
        else:
            action_vector[self.action_indices[decision.action]] = 1

        return np.array(action_vector)