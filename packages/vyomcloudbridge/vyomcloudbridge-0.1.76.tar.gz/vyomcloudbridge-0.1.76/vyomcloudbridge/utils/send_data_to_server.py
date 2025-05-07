#utils/send_data_to_server.py
import time
import json

import rclpy

from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from vyomcloudbridge.services.queue_writer_json import QueueWriterJson
import sensor_msgs.msg
import vyomcloudbridge.utils.converter as converter
from rclpy.node import Node
import importlib


class SendDataToServer(Node):
    """
    SendDataToServer is a ROS2 node responsible for subscribing to various topics, processing the received data,
    and writing the processed data to a queue in JSON format. The node dynamically creates subscribers based on
    a configuration file and handles different message types, including JSON and images.

    Attributes:
        subscriber_cb_group (MutuallyExclusiveCallbackGroup): A callback group to ensure mutually exclusive callbacks.
        extracted_data_list (list): A list to store extracted data.
        subscribers (list): A list to store dynamically created subscribers.
        m_qos (QoSProfile): Quality of Service profile for the subscribers.
        mission_id (int): Identifier for the mission, used in the processed data.
        writer (QueueWriterJson): An instance of QueueWriterJson to handle writing messages to a queue.

    Methods:
        __init__(): Initializes the node, loads topics from a configuration file, and creates subscribers.
        get_subcribed_topics(): Retrieves the list of topics to subscribe to based on the configuration file.
        load_topic_list_from_file(): Loads the topic list from a JSON configuration file.
        create_listener_function(msg_type, f_topic): Creates a listener function for a specific topic and message type.
        import_class_from_string(class_string): Dynamically imports a class from its string representation.
        create_dynamic_subscribers(f_topic): Dynamically creates a subscriber for a given topic.
    """

    def __init__(self):
        super().__init__("senddatatoserver")

        print("SendDataToServer has started.")
        self.subscriber_cb_group = MutuallyExclusiveCallbackGroup()

        # Initialize extracted data list
        self.subscribers = []

        self.m_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            durability=DurabilityPolicy.VOLATILE,
        )

        self.writer = QueueWriterJson()

        self.mission_id = 80

        for topic in self.get_subcribed_topics():
            print(f"Subscribing to topic: {topic}")
            self.create_dynamic_subscribers(topic)

    def get_subcribed_topics(self):
        """
        Retrieve the list of subscribed topics.

        This method loads a list of topics from a file and filters them to return
        only those topics that are marked as subscribed.

        Returns:
            list: A list of dictionaries representing the subscribed topics. Each
            dictionary contains topic details, including an "is_subscribed" key
            indicating subscription status.
        """
        topic_list = self.load_topic_list_from_file()
        return [topics for topics in topic_list if topics["is_subscribed"]]

    def load_topic_list_from_file(self):
        """
        Loads a list of topics from a JSON file.

        This method reads the file located at '/etc/vyomcloudbridge/machine_topics.json',
        deserializes its JSON content, and returns the resulting list of topics.

        Returns:
            list: A list of topics loaded from the JSON file.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        with open("/etc/vyomcloudbridge/machine_topics.json", "r") as f:
            serialised_topic_list = json.load(f)
        return serialised_topic_list

    def create_listener_function(self, msg_type, f_topic):
        """
        Creates a listener function for processing incoming messages of a specific type and topic.

        Args:
            msg_type (type): The type of the message to be processed (e.g., sensor_msgs.msg.Image).
            f_topic (str): The topic associated with the message.

        Returns:
            function: A listener function that processes incoming messages, extracts relevant data,
                      and writes the data to a specified destination.

        The generated listener function performs the following:
            - Converts the incoming message to the desired format using a converter.
            - Extracts a timestamp from the message header if available.
            - Constructs a filename based on the current epoch time and a padding value.
            - Differentiates between image and JSON data types.
            - Prepares the extracted data for writing, including metadata such as timestamp,
              topic, mission ID, and the converted data.
            - Writes the processed data to a destination using the `self.writer.write_message` method.

        Notes:
            - If the message type is `sensor_msgs.msg.Image`, the data is treated as an image and saved
              with a `.jpeg` extension.
            - If the message does not contain a timestamp, a placeholder value of 0 is used for both
              seconds and nanoseconds.
            - The `self.mission_id` attribute is used to associate the data with a specific mission.
            - The `self.writer.write_message` method handles the actual writing of the processed data.
        """

        def f(msg):
            print(f"Processing data for: {f_topic}")

            current_value = converter.convert(msg_type, 1, msg)

            # self.print(f"data: {current_value}")

            epoch_ms = int(time.time() * 1000)
            uuid_padding = 3343

            if msg_type == sensor_msgs.msg.Image:
                filename = f"{epoch_ms}{uuid_padding}.jpeg"
                data_type = "image"
                extracted_data = current_value
            else:
                filename = f"{epoch_ms}{uuid_padding}.json"
                data_type = "json"

                # Extract timestamp from the message
                if hasattr(msg, "header") and hasattr(msg.header, "stamp"):
                    timestamp_sec = msg.header.stamp.sec
                    timestamp_nsec = msg.header.stamp.nanosec
                    print(
                        f"Timestamp: {timestamp_sec} seconds, {timestamp_nsec} nanoseconds"
                    )
                else:
                    timestamp_sec = 0
                    timestamp_nsec = 0
                    print("Timestamp not available, using placeholder.")

                extracted_data = {
                    "timestamp": {
                        "seconds": timestamp_sec,
                        "nanoseconds": timestamp_nsec,
                    },
                    "key": f_topic,
                    "mission_id": self.mission_id,
                    "data": {},
                }
                extracted_data["data"] = current_value

            self.writer.write_message(
                message_data=extracted_data,  # json data
                filename=filename,  # nullable or epoch time
                data_source=f_topic,  # telemetry, mission_summary
                data_type=data_type,  # file, video, image
                mission_id=self.mission_id,  # mission_id
                priority=1,  # 1  for velocity data, battery topic, and ROS data
                destination_ids=["s3"],  # ["s3"]
            )

        return f

    def import_class_from_string(self, class_string):
        """
        Dynamically imports and returns a class from its string representation.

        Args:
            class_string (str): A string representation of the class to import.
                The string can be in the format "<class 'module.submodule.ClassName'>"
                or simply "module.submodule.ClassName".

        Returns:
            type: The class object corresponding to the given string representation.

        Raises:
            ImportError: If the module cannot be imported.
            AttributeError: If the class cannot be found in the module.

        Example:
            >>> obj = import_class_from_string("<class 'collections.defaultdict'>")
            >>> obj
            <class 'collections.defaultdict'>
        """
        class_string = class_string.strip()
        if class_string.startswith("<class '") and class_string.endswith("'>"):
            # Extract the part between the quotes
            class_path = class_string[8:-2]  # Remove "<class '" and "'>"
        else:
            class_path = class_string

        # Split into module path and class name
        parts = class_path.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        # Import the module dynamically
        module = importlib.import_module(module_path)

        # Get the class from the module
        return getattr(module, class_name)

    def create_dynamic_subscribers(self, f_topic):
        """
        Dynamically creates and adds a subscriber to the list of subscribers.

        This method takes a topic configuration, creates a subscription for the
        specified data type and topic path, and appends it to the `subscribers` list.

        Args:
            f_topic (dict): A dictionary containing the topic configuration with the following keys:
                - "data_type" (str): The fully qualified class name of the data type to subscribe to.
                - "path" (str): The topic path to subscribe to.
                - "name" (str): The name of the topic.

        Returns:
            None
        """
        self.subscribers.append(
            self.create_subscription(
                self.import_class_from_string(f_topic["data_type"]),
                f_topic["path"],
                self.create_listener_function(f_topic["data_type"], f_topic["name"]),
                self.m_qos,
                callback_group=self.subscriber_cb_group,
            )
        )


def main(args=None):
    rclpy.init(args=args)
    send_data_to_server = SendDataToServer()
    rclpy.spin(send_data_to_server)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
