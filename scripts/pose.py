import rospy
import argparse
import numpy as np
import cv2
from cv_bridge import CvBridge
import tf

from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import TransformStamped,Vector3,Quaternion
from message_filters import ApproximateTimeSynchronizer, Subscriber

from opendr.engine.data import Image as OpenDRImage
from opendr.perception.pose_estimation import draw
from opendr.perception.pose_estimation import LightweightOpenPoseLearner

from engage.opendr_bridge import ROSBridge
from engage.pose_helper import HRIPoseManager

# This node in part adapts the OpenDR pose estimation node

class PoseEstimationNode:
    def __init__(
            self,
            rgb_image_topic,
            depth_image_topic,
            rgb_info_topic,
            depth_info_topic,
            pose_image_topic=None,
            device="cuda",
            num_refinement_stages=2,
            use_stride=False,
            half_precision=False,
            rate=20,
            smoothing=True,
            smoothing_time=2
        ):
        # Rate
        self.rate = rospy.Rate(rate)


        # OpenDR pose estimator
        self.pose_estimator = LightweightOpenPoseLearner(device=device, num_refinement_stages=num_refinement_stages,
                                                         mobilenet_use_stride=use_stride,
                                                         half_precision=half_precision)
        self.pose_estimator.download(path=".", verbose=True)
        self.pose_estimator.load("openpose_default")

        self.opendr_bridge = ROSBridge()

        # Pose Manager
        self.pose_manager = HRIPoseManager(smoothing=smoothing,smoothing_window=smoothing_time*rate)

        # Subscribers
        self.rgb_image_sub = Subscriber(rgb_image_topic,Image)
        self.rgb_info_sub = Subscriber(rgb_info_topic,CameraInfo)
        self.depth_image_sub = Subscriber(depth_image_topic,Image)
        self.depth_info_sub = Subscriber(depth_info_topic,CameraInfo)

        time_slop = 1
        self.synch_sub = ApproximateTimeSynchronizer(
            [
                self.rgb_image_sub,
                self.rgb_info_sub,
                self.depth_image_sub,
                self.depth_info_sub
            ],
            10,
            time_slop,
        )
        self.synch_sub.registerCallback(self.camera_callback)
        self.im_time = None

        # Publishers
        self.opendr_pose_image_pub = None
        if pose_image_topic is not None:
            self.opendr_pose_image_pub = rospy.Publisher(pose_image_topic,Image,queue_size=1)

        # Camera information for projections
        self.rgb_info = None
        self.depth_info = None

        # OpenCV Bridge
        self.cv_bridge = CvBridge()

        # Transforms
        self.cam_br = tf.TransformBroadcaster()

    def camera_callback(self,rgb_img,rgb_info,depth_img,depth_info):
        # Update time for synching
        self.im_time = rgb_info.header.stamp

        # Camera calibration
        if self.rgb_info is None:
            self.rgb_info = rgb_info
            self.depth_info = depth_info
            self.pose_manager.update_camera_model(rgb_info,depth_info)

        # Broadcast the camera at position 0,0,0 rotation 0,0,0 # TODO replace with the actual thing
        self.cam_world_transform = TransformStamped()
        self.cam_world_transform.header.stamp = self.im_time
        trans = (0,0,0)
        self.cam_world_transform.transform.translation = Vector3()
        self.cam_world_transform.transform.translation.x = trans[0]
        self.cam_world_transform.transform.translation.y = trans[1]
        self.cam_world_transform.transform.translation.z = trans[2]
        self.cam_world_transform.transform.rotation = Quaternion()
        quat = tf.transformations.quaternion_from_euler(0, 0, 0)
        self.cam_world_transform.transform.rotation.x = quat[0]
        self.cam_world_transform.transform.rotation.y = quat[1]
        self.cam_world_transform.transform.rotation.z = quat[2]
        self.cam_world_transform.transform.rotation.w = quat[3]
        self.cam_br.sendTransform(
            trans,
            quat,
            self.im_time,
            "camera",
            "world"
        )
        self.pose_manager.update_camera_transform(self.cam_world_transform)

        

        # OpenCV
        rgb_image = cv2.cvtColor(self.cv_bridge.imgmsg_to_cv2(rgb_img), cv2.COLOR_BGR2RGB)
        depth_image = self.cv_bridge.imgmsg_to_cv2(depth_img, "16UC1")

        # Get poses
        poses = self.opendr_pose_estimation(rgb_img)

        # Process new poses
        self.pose_manager.process_poses(poses,self.im_time,rgb_image,depth_image)

    def opendr_pose_estimation(self,rgb_img):
        # Convert sensor_msgs.msg.Image into OpenDR Image
        image = self.opendr_bridge.from_ros_image(rgb_img, encoding='bgr8')

        # Run pose estimation
        poses = self.pose_estimator.infer(image)

        # Publish pose image
        if self.opendr_pose_image_pub is not None:
            image = image.opencv()
            for pose in poses:
                draw(image, pose)
            self.opendr_pose_image_pub.publish(self.opendr_bridge.to_ros_image(OpenDRImage(image), encoding='bgr8'))
        
        # Return
        return poses


    def run(self):
        rospy.spin()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--rgb_image_topic", help="Topic for rgb image",
                        type=str, default="/camera/color/image_raw")
    parser.add_argument("-d", "--depth_image_topic", help="Topic for depth image",
                        type=str, default="/camera/depth/image_rect_raw")
    parser.add_argument("-ii", "--rgb_info_topic", help="Topic for rgb camera info",
                        type=str, default="/camera/color/camera_info")
    parser.add_argument("-di", "--depth_info_topic", help="Topic for depth camera info",
                        type=str, default="/camera/depth/camera_info")
    parser.add_argument("-p", "--pose_image_topic", help="Topic for publishing annotated pose images",
                        type=str, default=None)
    parser.add_argument("--accelerate", help="Activates some acceleration features (e.g. reducing number of refinement steps)",
                        default=None)
    args = parser.parse_args(rospy.myargv()[1:])

    if args.accelerate:
        use_stride=True
        half_precision=True
        num_refinement_stages=0
    else:
        use_stride=False
        half_precision=False
        num_refinement_stages=2

    rospy.init_node("HRIPose", anonymous=True)
    
    pose_node = PoseEstimationNode(
        rgb_image_topic=args.rgb_image_topic,
        depth_image_topic=args.depth_image_topic,
        rgb_info_topic=args.rgb_info_topic,
        depth_info_topic=args.depth_info_topic,
        pose_image_topic=args.pose_image_topic,
        use_stride=use_stride,
        half_precision=half_precision,
        num_refinement_stages=num_refinement_stages
        )
    pose_node.run()
