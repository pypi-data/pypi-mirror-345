import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import importlib


class RosSystemMsgSubscriber(Node):
    def __init__(self):
        super().__init__("ros_system_msg_subscriber")
        self.get_logger().info("ROS System Message Subscriber Node started.")

    def get_message_class(self, msg_name):
        # Dynamically import the message class from the correct package
        module = importlib.import_module(f"vyom_msg.msg")
        return getattr(module, msg_name)

    def topic_callback(self, msg, topic_name):
        # Handle the received message and log it
        self.get_logger().info(f"Received on '{topic_name}': {msg}")

    def setup_subscription(self, typ):
        # Subscribe to the topic dynamically based on the type
        msg_class = self.get_message_class(typ)
        topic_name = typ.lower()

        self.create_subscription(
            msg_class,
            topic_name,
            lambda msg: self.topic_callback(msg, topic_name),
            10
        )

        self.get_logger().info(f"Subscriber created for topic: '{topic_name}' with message type: '{msg_class}'")


def main(args=None):
    rclpy.init(args=args)

    ros_msg_subscriber = RosSystemMsgSubscriber()

    # Define the message types that you want to subscribe to
    message_types = ["Access", "Accessinfo", "Ack", "Auth", "Dvid"]

    # Set up subscriptions for all the message types
    for msg_type in message_types:
        ros_msg_subscriber.setup_subscription(msg_type)

    rclpy.spin(ros_msg_subscriber)

    ros_msg_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
