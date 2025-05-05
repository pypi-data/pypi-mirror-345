from nats.aio.msg import Msg as NatsMsg

from ..application.message_processor import MessageProcessor
from ..domain.models.hai_message import HaiMessage


class NatsMessageAdapter:
    """
    Adapter class to handle incoming NATS messages and process them using
    a message processor.

    The class serves as a bridge between NATS messaging and a domain-specific
    message processor. It listens for incoming messages, converts them into
    the appropriate domain object, processes them with the provided message
    processor, and optionally sends a response if required.

    :ivar processor: Instance of the message processor used to process domain
        messages.
    :type processor: MessageProcessor
    """
    def __init__(self, message_processor: MessageProcessor):
        self.processor = message_processor

    async def handle_nats_message(self, msg: NatsMsg) -> None:
        """Handle incoming NATS message."""
        try:
            domain_message = HaiMessage.from_json(msg.data.decode())

            response = await self.processor.process(domain_message)

            # If there's a reply subject and a response, send it back
            if msg.reply and response:
                await msg.respond(response.to_json().encode())

        except Exception as e:
            print(f"Error processing message: {e}")
