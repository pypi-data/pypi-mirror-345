import abc
import signal
import sys
from vyomcloudbridge.utils.logger_setup import setup_logger


class AbcListener(abc.ABC):
    """
    Abstract base class for listener services that can receive and process incoming messages.
    All listener implementations should inherit from this class.
    """

    def __init__(self, multi_thread: bool = False):
        # compulsory fields
        self.name = ""
        self.combine_by_target_id = False

        # class specific
        self.is_running = False
        self.multi_thread = multi_thread
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(sig, frame):
            self.logger.info(
                f"Received signal {sig}, shutting down {self.__class__.__name__}..."
            )
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    @abc.abstractmethod
    def start(self):
        """
        Start the listener service to begin receiving incoming messages.
        Must be implemented by subclasses.

        This method should:
        - Start any background processes for listening to incoming messages
        - Set up any required connections
        - Set is_running to True when the service is successfully started
        - Handle any initial setup required for message processing
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Stop the listener service and and call cleanup.
        Must be implemented by subclasses.

        This method should:
        - Stop any background processes for listening to incoming messages
        - is_running to False, and call cleanup
        - Set is_running to False when the service is successfully stopped
        -
        """
        self.cleanup()
        pass

    def is_healthy(self):
        """
        Check if the listener service is healthy.
        Can be overridden by subclasses to implement specific health checks.

        Returns:
            bool: True if the listener is healthy and operational, False otherwise
        """
        return self.is_running

    @abc.abstractmethod
    def cleanup(self):
        """
        Release any resources, connection being used by this service class
        """
        try:
            pass
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """
        Destructor called by garbage collector to ensure resources are cleaned up
        when the object is about to be destroyed.
        """
        try:
            self.stop()
        except Exception as e:
            # Cannot log here as logger might be destroyed already
            pass
