from engage.explanation.explain_test.engage_state_explainability_test import ExplainabilityTest
from engage.msg import HeuristicDecision as HeuristicDecisionMSG
from explanation_msgs.msg import Explainability

import numpy as np
from random import shuffle

class PilotHeuristicExplainabilityTest(ExplainabilityTest):
    def __init__(self, 
                 explanations, 
                 group, 
                 var_nums, 
                 ignore_uninteresting=True,
                 names=None,
                 language="english",
                 restricted_actions=[HeuristicDecisionMSG.ELICIT_GENERAL,HeuristicDecisionMSG.ELICIT_TARGET]
                 ) -> None:
        '''
        Group 0 - explanation but not counterfactial, no uncertainty
        Group 1 - explanation and counterfactual, no uncertainty
        Group 2 - explanation but not counterfactial, uncertainty
        Group 3 - explanation and counterfactual on gaze, uncertainty
        Group 4 - explanation and counterfactual on confidence, uncertainty
        '''
        self.group = group
        self.no_explanations = False

        if len(explanations) == 0:
            self.no_explanations = True
            return
                
        # Pick an appropriate explanation - always use gaze and uncertainty
        exp_vars = [(i,exp.variables[0]) for i,exp in zip(range(len(explanations)),explanations) if self.valid_variable(exp.variables[0],ignore_uninteresting)]       
        exp_counts = np.array([var_nums[exp_var[1].split("_")[1]] for exp_var in exp_vars])

        if exp_counts.size == 0:
            self.no_explanations = True
            return
           

        # For testing
        #self.group = 4

        body_exps = {}
        for exp in explanations:
            if exp.num_vars == 1:
                var = exp.variables[0]
                if exp.var_cats[var] != "GENERAL":
                    if exp.var_cats[var] not in body_exps:
                        body_exps[exp.var_cats[var]] = {}
                    body_exps[exp.var_cats[var]][exp.var_names[var]] = exp

        valid_bodies = []
        for body in body_exps:
            if self.group in [0,1]:
                if "Mutual Gaze" in body_exps[body]:
                    valid_bodies.append(body)
            else:
                 if "Mutual Gaze" in body_exps[body] and "Pose Estimation Confidence" in body_exps[body]:
                     valid_bodies.append(body)

        if len(valid_bodies) == 0:
            self.no_explanations = True
            return
        picked_body = np.random.choice(valid_bodies)

        self.gaze_explanation = body_exps[picked_body]["Mutual Gaze"]
        self.gaze_explanation.update_names(names)
        self.gaze_explanation.set_language(language)

        if self.group in [2,3,4]:
            self.confidence_explanation = body_exps[picked_body]["Pose Estimation Confidence"]
            self.confidence_explanation.update_names(names)
            self.confidence_explanation.set_language(language)

        # Generate explanation texts

        self.exp_counterfactual = ""
        if self.group == 0:
            # e.g. "I ___ because MG = X"
            self.exp_reason,_ = self.gaze_explanation.present_explanation()
        elif self.group == 1:
            # e.g. "I ___ because MG = X. If MG = Y, I would have ___"
            self.exp_reason,self.exp_counterfactual = self.gaze_explanation.present_explanation()
        elif self.group == 2:
            # e.g. "I ___ because MG = X and PEC = A"
            self.exp_reason,_ = self.gaze_explanation.present_uncertainty_explanation(self.gaze_explanation,self.confidence_explanation)
        elif self.group == 3:
            # e.g. "I ___ because MG = X and PEC = A. If MG = Y, I would have ___"
            self.exp_reason,self.exp_counterfactual = self.gaze_explanation.present_uncertainty_explanation(self.gaze_explanation,self.confidence_explanation,cf_gaze=True)
        elif self.group == 4:
            # e.g. "I ___ because MG = X and PEC = A. If PEC = B, I would have ___"
            self.exp_reason,self.exp_counterfactual = self.gaze_explanation.present_uncertainty_explanation(self.gaze_explanation,self.confidence_explanation,cf_gaze=False)

        print("REASON: ",self.exp_reason)
        print("CF: ", self.exp_counterfactual)

        possible_answers = self.gaze_explanation.uncertainty_test_answers()
        print(possible_answers)

        # TODO: Double check
        # Test 1: Gaze
        correct_answer_gaze_unshuffle = 1
        self.answer_list_gaze = possible_answers.copy()
        shuffle(self.answer_list_gaze)
        self.correct_answer_gaze = self.answer_list_gaze.index(possible_answers[correct_answer_gaze_unshuffle])

        # Test 2: Uncertainty
        correct_answer_uncertainty_unshuffle = 1
        self.answer_list_uncertainty = possible_answers.copy()
        shuffle(self.answer_list_uncertainty)
        self.correct_answer_uncertainty = self.answer_list_uncertainty.index(possible_answers[correct_answer_uncertainty_unshuffle])



    def valid_variable(self,var,ignore_uninteresting):
        varsplit = var.split("_")
        if ignore_uninteresting:
            if varsplit[0] in ["GENERAL","ROBOT"]:
                return False
        return True

    def to_message(self,image,time,blank_image,user_id=0,num_people=0):
        msg = Explainability()

        msg.header.stamp = time
        msg.id = user_id
        msg.group = self.group
        msg.num_people = num_people
        msg.is_minor = False
        msg.image = image
        msg.blank_image = blank_image
        msg.explanation = self.exp_reason
        msg.counterfactual = self.exp_counterfactual
        msg.question_context = ""
        msg.question_text = ""
        msg.answer_list_gaze = self.answer_list_gaze
        msg.correct_answer_gaze = self.correct_answer_gaze+1
        msg.answer_list_uncertainty = self.answer_list_gaze
        msg.correct_answer_uncertainty = self.correct_answer_gaze+1

        return msg
    