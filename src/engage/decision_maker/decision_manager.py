from engage.decision_maker.heuristic_decision_maker import HeuristicDecisionMaker
from engage.decision_maker.random_robot_decision_maker import RandomRobotDecisionMaker
from engage.decision_maker.simple_target_decision_maker import SimpleTargetDecisionMaker
from engage.decision_maker.heuristic_ari_controller import HeuristicARIController
from engage.decision_maker.simple_ari_controller import SimpleARIController
from engage.decision_maker.simple_target_ari_controller import SimpleTargetARIController
from engage.decision_maker.gaze_confidence_dm import GazeConfidenceDM
from engage.explanation.heuristic_explainer import HeuristicOutcome,HeuristicQuery
from engage.explanation.explain_test.heuristic_explainability_test import HeuristicExplainabilityTest
from engage.explanation.explain_test.pilot_heuristic_explainability_test import PilotHeuristicExplainabilityTest


from engage.msg import HeuristicStateDecision,RobotStateDecision,DecisionState


class DecisionManager:
    decision_makers = {
        "heuristic":HeuristicDecisionMaker,
        "random_robot":RandomRobotDecisionMaker,
        "simple_target":SimpleTargetDecisionMaker,
        "gaze_confidence":GazeConfidenceDM,
    }

    decision_state_msgs = {
        "heuristic":HeuristicStateDecision,
        "random_robot":RobotStateDecision,
        "simple_target":HeuristicStateDecision,
        "gaze_confidence":HeuristicStateDecision,
    }

    state_msgs = {
        "heuristic":DecisionState,
        "random_robot":DecisionState,
        "simple_target":DecisionState,
        "gaze_confidence":DecisionState,
    }

    robot_controllers = {
        "heuristic_ari_controller":HeuristicARIController,
        "simple_ari_controller":SimpleARIController,
        "simple_target_ari_controller":SimpleTargetARIController,
    }

    decision_outcomes = {
        "heuristic":HeuristicOutcome,
        "simple_target":HeuristicOutcome,
        "gaze_confidence":HeuristicOutcome,
    }

    decision_queries = {
        "heuristic":HeuristicQuery,
        "simple_target":HeuristicQuery,
        "gaze_confidence":HeuristicQuery,
    }

    decision_explainability_tests = {
        "heuristic":HeuristicExplainabilityTest,
        "simple_target":HeuristicExplainabilityTest,
        "gaze_confidence":PilotHeuristicExplainabilityTest,
    }

    def __init__(self) -> None:
        pass