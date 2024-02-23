from engage.explanation.language.heuristic_text import HeuristicText

class HeuristicTextCatalan(HeuristicText):
    def __init__(self) -> None:
        super().__init__()

    def outcome_text_conditional(self,outcome,person_name):
        if outcome.action == self.dmsg.NOTHING:
            text = "Jo no hauria fet res"
        elif outcome.action == self.dmsg.WAIT:
            text = "Jo hauria acabat el que estava fent"
        elif outcome.action == self.dmsg.MAINTAIN:
            raise ValueError
        elif outcome.action == self.dmsg.RECAPTURE:
            raise ValueError
        elif outcome.action == self.dmsg.ELICIT_GENERAL:
            text = "Jo hauria intentat que algú parlés amb mi"
        elif outcome.action == self.dmsg.ELICIT_TARGET:
            text = "Jo hauria intentat que {} parlés amb mi".format(person_name(outcome.target))
        else:
            raise ValueError
        
        return text
    
    def outcome_text_past(self,outcome,person_name):
        if outcome.action == self.dmsg.NOTHING:
            text = "No he fet res"
        elif outcome.action == self.dmsg.WAIT:
            text = "Jo estava esperant per acabar el que estava fent"
        elif outcome.action == self.dmsg.MAINTAIN:
            raise ValueError
        elif outcome.action == self.dmsg.RECAPTURE:
            raise ValueError
        elif outcome.action == self.dmsg.ELICIT_GENERAL:
            text = "He intentat que algú parlés amb mi"
        elif outcome.action == self.dmsg.ELICIT_TARGET:
            text = "He intentat parlar amb {}".format(person_name(outcome.target))
        else:
            raise ValueError
        
        return text
    
    def outcome_text_future(self,outcome,person_name):
        if outcome.action == self.dmsg.NOTHING:
            text = "No faré res"
        elif outcome.action == self.dmsg.WAIT:
            text = "Esperaré a acabar el que estic fent"
        elif outcome.action == self.dmsg.MAINTAIN:
            raise ValueError
        elif outcome.action == self.dmsg.RECAPTURE:
            raise ValueError
        elif outcome.action == self.dmsg.ELICIT_GENERAL:
            text = "Intentaré que algú parli amb mi"
        elif outcome.action == self.dmsg.ELICIT_TARGET:
            text = "Intentaré parlar amb {}".format(person_name(outcome.target))
        else:
            raise ValueError
        
        return text
    
    def confidence_reason_text(self,var_name,subject,threshold,approx_val,thresh_min,approx_thresh):       
        # Threshold
        negation = ""
        magnitude = ""
        if threshold is None:
            if approx_val == 0.00:
                magnitude = "molt in"
            elif approx_val == 0.33:
                negation = "no "
            elif approx_val == 0.66:
                pass
            else:
                magnitude = "molt "
        else:
            if thresh_min:
                # True value is lower than a threshold
                if approx_thresh == 0.33:
                    magnitude = "molt in"
                else:
                    negation = "no "
            else:
                # True value is greater than a threshold
                if approx_thresh == 0.67:
                    magnitude = "molt "
                else:
                    pass

        # Variable type
        if var_name == "Group Confidence":
            raise ValueError
        elif var_name == "Motion Confidence":
            raise ValueError
        elif var_name == "Engagement Level Confidence":
            raise ValueError
        elif var_name == "Pose Estimation Confidence":
            var_string = "de la meva detecció de l'esquelet de {}".format(subject)


        text = "{}estava {}segura".format(negation,magnitude).capitalize()
        return "{} {}".format(text,var_string)
    
    def confidence_counterfactual_texts(self,var,var_name,var_cats,values,subject,min_val,max_val):
        negation = ""
        magnitude = ""
        dif_sent = False
        situation = ""
        if min_val:
            # Only concerns the highest value
            approx_max = round(values[-1],2)

            if approx_max == 0.00:
                magnitude = "molt in"
            elif approx_max == 0.33:
                negation = "no "
            elif approx_max == 0.67:
                negation = "no "
                magnitude = "molt "
            else:
                # Somewhere in between
                dif_sent = True
                situation = "Si estigués molt segura o molt insegura"

        elif max_val:
            # Only conerns the lowest value
            approx_min = round(values[0],2)

            if approx_min == 1.00:
                magnitude = "molt "
            elif approx_min == 0.67:
                pass
            elif approx_min == 0.33:
                situation = "Si estigués almenys una mica segura" # TODO: Double check this one especially
            else:
                # Somewhere in between
                dif_sent = True
                situation = "Si estigués molt segura o molt insegura"
        else:
            # Concerns both
            if len(values) == 1:
                val = round(values[0],2)
                if val == 0.00:
                    magnitude = "molt in"
                elif val == 0.33:
                    negation = "no "
                elif val == 0.66:
                    pass
                else:
                    magnitude = "molt "
            else:
                approx_min = round(values[0],2)
                approx_max = round(values[-1],2)
                if approx_min == 0.33 and approx_max == 0.67:
                    # This is the only valid combination unless another discretisation is introduced
                    dif_sent = True
                    situation = "Si no estigués ni molt insegura ni molt segura"
                    
        
        if var_name == "Group Confidence":
            raise ValueError
        elif var_name == "Motion Confidence":
            raise ValueError
        elif var_name == "Engagement Level Confidence":
            raise ValueError
        elif var_name == "Pose Estimation Confidence":
            var_string = "de la meva detecció de l'esquelet de {}".format(subject)

        if dif_sent:
            return "{} {}".format(situation,var_string)
        return "Si {}estigués {}segura {}".format(negation,magnitude,var_string)
    
    def reason_text(self,var,var_name,var_cats,subject,explanation_values,true_val,true_observation):
        if true_observation.variable_categories[var_name] == "Categorical":
            # Categorical variables, pretty straightforward
            if var_name == "Group":
                raise ValueError
            elif var_name == "Motion":
                raise ValueError
            elif var_name == "Engagement Level":
                raise ValueError
            elif var_name == "Group with Robot":
                raise ValueError
            elif var_name == "Waiting":
                if true_val:
                    return "estava fent una altra cosa."
                else:
                    return "no estava fent res més."
        else:
            # Continuous variables...much trickier
            approx_val = round(true_val,2)
            min_range = min(explanation_values[var])
            max_range = max(explanation_values[var])

            thresh_min = None
            if true_val < min_range:
                # All counterfactuals are higher
                threshold = min_range
                thresh_min = True
                approx_thresh = round(threshold,2)
            elif true_val > max_range:
                # All counterfactuals are lower:
                threshold = max_range
                thresh_min = False
                approx_thresh = round(threshold,2)
            else:
                # True value is somewhere in between, meaning a more complex answer
                threshold = None
                approx_thresh = None

            #
            # Can start comparing var_name
            #
            if var_name in ["Group Confidence","Motion Confidence","Engagement Level Confidence","Pose Estimation Confidence"]:
                return self.confidence_reason_text(var_name,subject,threshold,approx_val,thresh_min,approx_thresh)
            elif var_name == "Mutual Gaze":
                if threshold is None:
                    if approx_val == 0.00:
                        return "{} no em mirava gens.".format(subject)
                    elif approx_val == 0.33:
                        return "{} no em mirava.".format(subject)
                    elif approx_val == 0.67:
                        return "{} em mirava una mica.".format(subject)
                    elif approx_val == 1.00:
                        return "{} i jo ens miràvem directament.".format(subject)
                else:
                    if thresh_min:
                        # True value is lower than a threshold
                        if approx_thresh == 0.33:
                            return "{} no em mirava gens.".format(subject)
                        elif approx_thresh == 0.67:
                            return "{} no em mirava.".format(subject)
                        elif approx_thresh == 1.00:
                            return "{} i jo no ens miràvem directament.".format(subject)
                    else:
                        # True value is higher than a threshold
                        if approx_thresh == 0.67:
                            return "{} i jo ens miràvem directament.".format(subject)
                        elif approx_thresh == 0.33:
                            return "{} em mirava.".format(subject)
                        elif approx_thresh == 0.00:
                            return "{} no mirava lluny de mi.".format(subject) #TODO: This one too
            elif var_name == "Engagement Value":
                if threshold is None:
                    if approx_val == 0.00:
                        return "{} no estava gens interessat en mi.".format(subject)
                    elif approx_val == 0.33:
                        return "{} no estava interessat en mi.".format(subject)
                    elif approx_val == 0.67:
                        return "{} estava interessat en mi.".format(subject)
                    elif approx_val == 1.00:
                        return "{} estava molt interessat en mi.".format(subject)
                else:
                    if thresh_min:
                        # True value is lower than a threshold
                        if approx_thresh == 0.33:
                            return "{} no estava gens interessat en mi.".format(subject)
                        elif approx_thresh == 0.67:
                            return "{} no estava interessat en mi.".format(subject)
                        elif approx_thresh == 1.00:
                            return "{} no estava molt interessat en mi.".format(subject)
                    else:
                        # True value is higher than a threshold
                        if approx_thresh == 0.67:
                            return "{} estava molt interessat en mi.".format(subject)
                        elif approx_thresh == 0.33:
                            return "{} estava interessat en mi.".format(subject)
                        elif approx_thresh == 0.00:
                            return "{} estava una mica interessat en mi.".format(subject)
            elif var_name == "Distance":
                if threshold is None:
                    return "{} estava a uns {} metres de mi.".format(subject,approx_val)
                else:
                    if thresh_min:
                        # True value is lower than a threshold
                        return "{} estava a menys de {} metres de mi.".format(subject,approx_thresh)
                    else:
                        # True value is higher than a threshold
                        return "{} estava a més de {} metres de mi.".format(subject,approx_thresh)
                    
    def construct_reason_text(self,true_outcome,var,var_name,var_cats,subject,explanation_values,true_val,true_observation,person_name):
        return self.outcome_text_past(true_outcome,person_name)[:-1] + " perquè " + self.reason_text(var,var_name,var_cats,subject,explanation_values,true_val,true_observation)
    
    def construct_counterfactual_text(self,foil_text,counterfactual_decision_text):
        return " {}, {}.".format(foil_text,counterfactual_decision_text)
    
    def foil_text(self,var,var_name,var_cats,values,subject,true_values,true_observation,cards):
        val_settings = []
        if true_observation.variable_categories[var_name] == "Categorical":
            if var_name == "Group":
                 raise ValueError
            elif var_name == "Motion":
                 raise ValueError
            elif var_name == "Engagement Level":
                 raise ValueError
            elif var_name == "Group with Robot":
                 raise ValueError
            elif var_name == "Waiting":
                if values[0]:
                    val_settings.append("Si estigués fent una altra cosa")
                else:
                    val_settings.append("Si no estigués fent una altra cosa")

        else:
            if var_name != "Distance":
                min_range = 0.00
                max_range = 1.00
            else:
                max_range = round(max(cards),2)
                min_range = round(min(cards),2)

            sorted_vals = sorted(values)
            approx_max = round(sorted_vals[-1],2)
            approx_min = round(sorted_vals[0],2)

            min_val = approx_min == min_range
            max_val = approx_max == max_range
            
            if var_name in ["Group Confidence","Motion Confidence","Engagement Level Confidence","Pose Estimation Confidence"]:
                val_settings.append(self.confidence_counterfactual_texts(var,var_name,var_cats,sorted_vals,subject,min_val,max_val))
            elif var_name == "Mutual Gaze":
                if len(sorted_vals) == 1:
                    approx_val = round(sorted_vals[0],2)

                    if approx_val == 0.00:
                        val_settings.append("Si {} no em mirés gens".format(subject))
                    elif approx_val == 0.33:
                        val_settings.append("Si {} no em mirés".format(subject))
                    elif approx_val == 0.67:
                        val_settings.append("Si {} em mirés una mica".format(subject))
                    elif approx_val == 1.00:
                        val_settings.append("Si {} i jo ens miréssim directament".format(subject))

                else:
                    if min_val:
                        # Only concerns the highest value
                        

                        if approx_max == 0.33:
                            val_settings.append("Si {} no em mirés".format(subject))
                        elif approx_max == 0.67:
                            val_settings.append("Si {} i jo no ens miréssim directament".format(subject))
                        elif approx_max == 1.00:
                            # Somewhere in between
                            val_settings.append("Si {} i jo ens miréssim directament o si {} no em mirés gens".format(subject,subject))

                    elif max_val:
                        # Only conerns the lowest value
                        

                        if approx_min == 0.67:
                            val_settings.append("Si {} em mirés".format(subject))
                        elif approx_min == 0.33:
                            val_settings.append("Si {} em mirés una mica".format(subject))
                        elif approx_min == 0.00:
                            # Somewhere in between
                            val_settings.append("Si {} i jo ens miréssim directament o si {} no em mirés gens".format(subject,subject))
                    else:
                        if approx_min == 0.33 and approx_max == 0.67:
                            # This is the only valid combination unless another discretisation is introduced
                            val_settings.append("Si {} em mirés una mica però no directament".format(subject))
            elif var_name == "Engagement Value":
                if len(sorted_vals) == 1:
                    approx_val = round(sorted_vals[0],2)

                    if approx_val == 0.00:
                        val_settings.append("Si {} no estigués gens interessat en mi".format(subject))
                    elif approx_val == 0.33:
                        val_settings.append("Si {} no estigués interessat en mi".format(subject))
                    elif approx_val == 0.67:
                        val_settings.append("Si {} estigués una mica interessat en mi".format(subject))
                    elif approx_val == 1.00:
                        val_settings.append("Si {} estigués molt interessat en mi".format(subject))

                else:
                    if min_val:
                        # Only concerns the highest value

                        if approx_max == 0.33:
                            val_settings.append("Si {} no estigués interessat en mi".format(subject))
                        elif approx_max == 0.67:
                            val_settings.append("Si {} no estigués molt interessat en mi".format(subject))
                        elif approx_max == 1.00:
                            # Somewhere in between
                            val_settings.append("Si {} estigués molt interessat en mi o si {} estigués molt desinteressat en mi".format(subject,subject))

                    elif max_val:
                        # Only conerns the lowest value

                        if approx_min == 0.67:
                            val_settings.append("Si {} estigués interessat en mi".format(subject))
                        elif approx_min == 0.33:
                            val_settings.append("Si {} estigués una mica interessat en mi".format(subject))
                    else:
                        if approx_min == 0.33 and approx_max == 0.67:
                            # This is the only valid combination unless another discretisation is introduced
                            val_settings.append("Si {} no estigués molt interessat en mi i si {} no estigués molt desinteressat en mi".format(subject,subject))
            elif var_name == "Distance":
                if len(sorted_vals) == 1:
                    approx_val = round(sorted_vals[0],2)
                    val_settings.append("Si {} estigués a uns {} metres de mi.".format(subject,approx_val))
                else:
                    if min_val:
                        val_settings.append("Si {} estigués a menys de {} metres de mi.".format(subject,approx_max))
                    elif max_val:
                        val_settings.append("Si {} estigués a més de {} metres de mi.".format(subject,approx_min))
                    else:
                        val_settings.append("Si {} estigués entre {} i {} metres de mi".format(subject,approx_min,approx_max))

            

        if len(val_settings) == 0:
            error_message = "No setting for {}:{} (min: {}, max: {})".format(var,values,min_val,max_val)
            raise ValueError(error_message)
        elif len(val_settings) == 1:
            return val_settings[0]
        else:
            foil_text = ""
            for val_set in val_settings:
                foil_text += val_set + ", o "
            return foil_text[:-4]
        
    def statement_text_conditional(self,var_cat,var_name,value,subject,true_observation):
        raise NotImplementedError
        
    def statement_text_past(self,var_cat,var_name,value,subject,true_observation):
        raise NotImplementedError
    
    def question_context(self,context_statement):
        raise NotImplementedError
    
    def question_text(self,question_statement):
        raise NotImplementedError
    
    def question_context_imaginary_person_absolute(self,var_name,new_person):
        raise NotImplementedError
    
    def question_text_imaginary_person_absolute(self,var_name,value,true_observation,person_name):

        raise NotImplementedError