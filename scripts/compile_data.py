import rospy
import argparse
import rosbag
import os
import pandas as pd
import string
from pathlib import Path

from engage.pose_helper import HRIPoseBody

class DataCompiler:
    def __init__(
            self,
            exp,
            bag_dir,
            save_dir,
            exp_name="Test",
            rate=20,
            max_files=100,
    ) -> None:
        self.rate = rospy.Rate(rate)

        # Read data
        self.data,self.statistics = self.read_data(exp,bag_dir,max_files=max_files)

        self.df = pd.DataFrame(self.data,columns=self.datapoint_cols())

        print(self.statistics)
        print(self.df)

        # Save
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        self.df.to_csv("{}{}.csv".format(save_dir,exp_name))

        print("Saved to {}.csv".format(exp_name))


    def read_data(self,exps,bag_dir,max_files=100):
        data = []
        statistics = {
            "num_frames":0,
            "num_frames_person":{i:0 for i in range(20)},
            "segment":-1,
        }
        for exp in exps[0]:
            print("Reading from exp {}".format(exp))
            for i in range(max_files):
                filename = "{}_{}.bag".format(exp,i)
                
                try:
                    # Open file
                    file_path = os.path.join(bag_dir, filename)
                    bag = rosbag.Bag(file_path)
                    new_data,statistics = self.data_from_bag(bag,statistics)
                    data += new_data
                except FileNotFoundError:
                    pass

        return data,statistics

    def data_from_bag(self,bag,statistics):
        data = []
        # Start by reading from decisions
        continues_segment = False
        for _,msg,_ in bag.read_messages(topics=["/hri_engage/decision_states"]):
            statistics["num_frames"] += 1
            statistics["num_frames_person"][len(msg.state.bodies)] += 1

            if len(msg.state.bodies) == 2:
                if not continues_segment:
                    statistics["segment"] += 1
                    continues_segment = True
                datapoint,success = self.construct_datapoint(msg,statistics,bag)
                if success:
                    data.append(datapoint)
            else:
                continues_segment = False
        return data,statistics
    
    def construct_datapoint(self,msg,statistics,bag):
        dp = [statistics["segment"],msg.state.waiting]
        # Pose
        for id in msg.state.bodies:
            pose,found = self.get_pose_for_person(bag,msg.header.stamp,id)
            dp += pose

            if not found:
                return [],False
        # Features
        for i in range(len(msg.state.bodies)):
            dp.append(msg.state.distances[i])
            dp.append(msg.state.mutual_gazes[i])
            dp.append(msg.state.engagement_values[i])
            dp.append(msg.state.pose_estimation_confidences[i])
        dp.append(msg.decision.action)
        # Decision
        if msg.decision.target is not None and msg.decision.target != "":
            dp.append(msg.state.bodies.index(msg.decision.target))
        else:
            dp.append(msg.decision.target)
        return dp,True
    
    def get_pose_for_person(self,bag,time,id):
        topic = "/humans/bodies/{}/poses".format(id)
        pose = []
        found = False
        for _,msg,_ in bag.read_messages(topics=[topic]):
            if msg.header.stamp == time:
                found = True
                for p in msg.poses:
                    pose.append(p.position.x)
                    pose.append(p.position.y)
                    pose.append(p.position.z)
                break
        if not found:
            pose = [0 for i in range(54)]
        return pose,found
            

    def datapoint_cols(self):
        cols =  [
            "Segment",
            "Executing Action",
        ]

        for p in [0,1]:
            for joint in HRIPoseBody.joints:
                for c in ["x","y","z"]:
                    cols.append("P{}_{}.{}".format(p,joint,c))

        cols += [
            "Distance_0",
            "MutualGaze_0",
            "Engagement_0",
            "PoseEstimationConfidence_0",
            "Distance_1",
            "MutualGaze_1",
            "Engagement_1",
            "PoseEstimationConfidence_1",
            "Decision Action",
            "Decision Target",
        ]
        return cols

    def run(self):
        while not rospy.is_shutdown():
            self.rate.sleep()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", help="Name of experiment(s)",
                        action="append", nargs="+")
    parser.add_argument("--bag_dir", help="Directory of bag file", default=os.getenv("HOME")+"/prediction_exp_data/all_logs/")
    parser.add_argument("--save_dir", help="Directory for saving csv", default=os.getenv("HOME")+"/prediction_exp_data/data/")
    parser.add_argument("--name", help="Name for csv", default="PredictionExperiment")
    parser.add_argument("--max_files", help="Maximum number of files to check per exp", default=100)
    args = parser.parse_args(rospy.myargv()[1:])

    rospy.init_node("DataCompiler", anonymous=True)
    
    dc = DataCompiler(
        args.exp,
        args.bag_dir,
        args.save_dir,
        exp_name=args.name,
        max_files=args.max_files,
    )
    dc.run()