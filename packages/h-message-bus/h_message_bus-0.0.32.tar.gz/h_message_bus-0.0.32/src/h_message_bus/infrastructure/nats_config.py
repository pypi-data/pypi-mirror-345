from dataclasses import dataclass


@dataclass
class NatsConfig:
    """
    Configuration class for NATS client.

    This class encapsulates the configuration options required for connecting and
    interacting with a NATS (NATS.io) server. It includes options for setting
    server details, reconnection behavior, timeouts, and ping settings.

    :ivar server: The address of the NATS server to connect to.
    :type server: str
    :ivar max_reconnect_attempts: The maximum number of reconnection attempts allowed.
    :type max_reconnect_attempts: int
    :ivar reconnect_time_wait: The time duration to wait between reconnection attempts, in seconds.
    :type reconnect_time_wait: int
    :ivar connection_timeout: The timeout duration for establishing a connection, in seconds.
    :type connection_timeout: int
    :ivar ping_interval: The interval for sending ping frames to the server, in seconds.
    :type ping_interval: int
    :ivar max_outstanding_pings: The maximum number of ping requests allowed without receiving a response.
    :type max_outstanding_pings: int
    """
    server: str
    max_reconnect_attempts: int = 10
    reconnect_time_wait: int = 2
    connection_timeout: int = 2
    ping_interval: int = 20
    max_outstanding_pings: int = 5
