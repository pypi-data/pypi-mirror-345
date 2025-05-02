import json
import time
import rclpy
from rclpy.node import Node


class ROSTopic:
    def __init__(self, discovery_timeout=5.0):
        """
        Initialize the ROS topic discoverer.

        Args:
            discovery_timeout: Time in seconds to wait for topic discovery
        """
        rclpy.init()
        self.topic_node = Node("topic_discoverer")
        self.discovery_timeout = discovery_timeout

    def serialize_topic_list(self):
        """
        Get a complete list of ROS topics and their types, with proper discovery time.

        Returns:
            str: JSON string containing topic names and types
        """
        # Allow time for topic discovery
        start_time = time.time()
        prev_topic_count = 0

        print(f"Starting topic discovery (timeout: {self.discovery_timeout}s)...")

        # Keep spinning and checking topics until discovery stabilizes or timeout
        while True:
            # Spin the node to process discovery messages
            rclpy.spin_once(self.topic_node, timeout_sec=0.1)

            # Get current topic list
            topics = self.topic_node.get_topic_names_and_types()
            current_topic_count = len(topics)

            # Print progress if we find more topics
            if current_topic_count > prev_topic_count:
                print(f"Discovered {current_topic_count} topics so far...")
                prev_topic_count = current_topic_count

            # Check if we've reached our timeout
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.discovery_timeout:
                break

            # Short sleep to prevent CPU overuse
            time.sleep(0.1)

        # Create a dictionary with topic name as key and topic type as value
        topic_dict = {topic_name: topic_type[0] for topic_name, topic_type in topics}

        # Convert to JSON
        serialized_topics = json.dumps(topic_dict, indent=2)

        print(f"Discovery complete! Found {len(topic_dict)} topics.")

        return serialized_topics

    def cleanup(self):
        """Clean up ROS resources"""
        self.topic_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    try:
        # Create the topic discoverer with a 5 second discovery timeout
        topics_discoverer = ROSTopic(discovery_timeout=5.0)

        # Get the topic list with sufficient discovery time
        topic_list = topics_discoverer.serialize_topic_list()

        # Save the results to a file
        with open("ros_topics.json", "w") as f:
            f.write(topic_list)

        print(f"Topics saved to ros_topics.json")

    finally:
        # Ensure proper cleanup
        if "topics_discoverer" in locals():
            topics_discoverer.cleanup()
