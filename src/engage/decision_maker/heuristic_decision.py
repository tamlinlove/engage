import rospy

from engage.msg import HeuristicDecision as HeuristicDecisionMSG
from engage.decision_maker.decision_maker import Decision

class HeuristicDecision(Decision):
    action_names = ["NOTHING","WAIT","MAINTAIN","RECAPTURE","ELICIT_TARGET","ELICIT_GENERAL"]

    def __init__(self,action:int,target:str):
        self.action = action
        self.target = target

    def message(self,time=None):
        msg = HeuristicDecisionMSG()
        if time is not None:
            msg.header.stamp = time
        else:
            msg.header.stamp = rospy.Time.now()
        msg.action = self.action
        msg.target = self.target if self.target is not None else ""
        return msg
    
    def decision_tuple(self):
        return (self.action,self.target)
    
    def decision_tuple_string(self):
        return (self.action_names[self.action],self.target)
    
    @staticmethod
    def create_publisher(topic="/hri_engage/decisions",queue_size=1):
        return rospy.Publisher(topic,HeuristicDecisionMSG,queue_size=queue_size)



    