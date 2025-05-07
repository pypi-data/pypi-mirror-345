import json
import time
import rclpy
from rclpy.node import Node

from rosidl_runtime_py.convert import message_to_ordereddict

import vyom_msg.msg
from vyomcloudbridge.services.queue_writer_json import QueueWriterJson


class Heartbeat:
    def __init__(self):
        self.topic_node = Node("heartbeat_node")
        self.topic_node.logger.info("Heartbeat node started")

        self.heartbeat = vyom_msg.msg.Heartbeat()
        self.heartbeat.machineid = "301394"
        self.heartbeat.timestamp = int(time.time() * 1000)

        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.control_loop)

    def serialise_msg(self, message):

        msg_type = type(message).__name__

        msg_to_sent = message_to_ordereddict(message)
        return json.dumps(dict(typ=msg_type, msg=msg_to_sent))

    def sent_msg(self, serialised_topic):
        # Sent msg to destination specified till acknowledgement is recieved from the destination
        writer = QueueWriterJson()
        try:
            epoch_ms = int(time.time() * 1000)

            writer.write_message(
                message_data=serialised_topic,  # json or binary data
                filename=f"{epoch_ms}.json",  # 293749834.json, 93484934.jpg
                data_source="machine",  # machine_pose camera1, machine_state
                data_type="json",  # json, binary, ros
                mission_id="301394",  # mission_id
                priority=3,  # 3 for heartbeat
                destination_ids=["s3"],  # ["s3"]
            )
        except Exception as e:
            print(f"Error writing test messages: {e}")
        finally:
            writer.cleanup()

    def update_heartbeat(self):
        self.logger.debug("Updating heartbeat")
        self.heartbeat.timestamp = int(time.time() * 1000)

    def control_loop(self):
        self.logger.info("Sending heartbeat")

        # sent heartbeat
        self.update_heartbeat()
        self.sent_msg(self.serialise_msg(self.heartbeat))


if __name__ == "__main__":
    rclpy.init()
    # Class instance
    heartbeat = Heartbeat()

    rclpy.spin(heartbeat)

    heartbeat.destroy_node()
    rclpy.shutdown()
