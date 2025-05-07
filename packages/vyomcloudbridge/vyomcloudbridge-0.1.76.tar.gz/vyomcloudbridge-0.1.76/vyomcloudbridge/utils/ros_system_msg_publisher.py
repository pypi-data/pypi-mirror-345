import rclpy
from rclpy.node import Node
import importlib
import json
from rosidl_runtime_py import set_message_fields


class RosSystemMsgPublisher(Node):
    def __init__(self):
        rclpy.init(args=None)
        super().__init__("ros_system_msg_publisher")
        self.msg_publishers = {}  # { topic_name : (publisher, msg_instance) }
        self.default_msg_package = "vyom_msg"
        self.fallback_msg_package = "vyom_mission_msgs"
        self.get_logger().info("ROS System Message Publisher Node started.")

    def get_message_class(self, msg_name):
        """Try to load message class from default, fall back to secondary package."""
        for package in [self.default_msg_package, self.fallback_msg_package]:
            try:
                module = importlib.import_module(f"{package}.msg")
                msg_class = getattr(module, msg_name)
                self.get_logger().info(f"Loaded message '{msg_name}' from package '{package}'")
                return msg_class
            except (ModuleNotFoundError, AttributeError):
                continue
        raise AttributeError(f"Message '{msg_name}' not found in {self.default_msg_package} or {self.fallback_msg_package}")

    def setup_publisher(self, topic_name=None, typ=None, msg_data=None):
        """Setup the publisher for the provided message type and data."""
        if typ is None or msg_data is None:
            raise ValueError("Message type and data must be provided.")

        if topic_name is None:
            topic_name = typ.lower()

        msg_class = self.get_message_class(typ)
        publisher = self.create_publisher(msg_class, topic_name, 10)
        msg_instance = msg_class()

        # Manually set the fields of the message
        if isinstance(msg_data, dict):
            for field, value in msg_data.items():
                if hasattr(msg_instance, field):
                    setattr(msg_instance, field, value)
                else:
                    self.get_logger().error(f"Field '{field}' not found in message class '{msg_class}'")
        elif hasattr(msg_instance, "data"):
            msg_instance.data = msg_data
        else:
            raise ValueError(f"Provided 'msg' is not valid for message type {typ}")

        self.msg_publishers[topic_name] = (publisher, msg_instance)
        self.get_logger().info(
            f"Publisher created for topic: '{topic_name}' with message type: '{typ}'"
        )

    def publish_all(self):
        """Publish all stored messages to their respective topics."""
        for topic, (publisher, msg_instance) in self.msg_publishers.items():
            try:
                self.get_logger().info(f"Publishing to topic '{topic}': {msg_instance}")
                publisher.publish(msg_instance)
            except Exception as e:
                self.get_logger().error(f"Error publishing on topic '{topic}': {str(e)}")
                
    def cleanup(self):
        rclpy.shutdown()


def main(args=None):
    # rclpy.init(args=args)

    ros_msg_publisher = RosSystemMsgPublisher()


    mission_msg_dict = {
        "mission_id": 42,
        "mission_status": 1,  # e.g., 0: pending, 1: in-progress, 2: complete
        "user_id": 101,
        "bt_id": "navigate_tree",
        "mission_feedback": "Mission is currently in progress."
    }
    
    ros_msg_publisher.setup_publisher("mission_status_topic", "MissionStatus", mission_msg_dict)


    # Publish all messages
    ros_msg_publisher.publish_all()
    
    
    # Spin for a brief moment to allow message publishing
    # rclpy.spin_once(ros_msg_publisher, timeout_sec=0.1)

    ros_msg_publisher.destroy_node()
    ros_msg_publisher.cleanup()


if __name__ == "__main__":
    main()
