"""

"""
import logging
from pamqp import specification

from rmqid import base


LOGGER = logging.getLogger(__name__)


class Channel(base.StatefulObject):
    """The Connection object is responsible for negotiating a connection and
    managing its state.

    """
    def __init__(self, channel_id, connection):
        """Create a new instance of the Channel class

        :param int channel_id: The channel id to use for this instance
        :param rmqid.Connection: The connection to communicate with

        """
        super(Channel, self).__init__()
        self._channel_id = channel_id
        self._connection = connection
        self._open()

    def _build_close_frame(self):
        """Build and return a channel close frame

        :rtype: pamqp.specification.Channel.Close

        """
        return specification.Channel.Close(200, 'Normal Shutdown')

    def _build_open_frame(self):
        """Build and return a channel open frame

        :rtype: pamqp.specification.Channel.Open

        """
        return specification.Channel.Open()

    def _open(self):
        """Open the channel"""
        self._set_state(self.OPENING)
        self._connection.write_frame(self._build_open_frame(),
                                     self._channel_id)
        self._connection.wait_on_frame(specification.Channel.OpenOk,
                                       self._channel_id)
        self._set_state(self.OPEN)
        LOGGER.debug('Channel #%i open', self._channel_id)

    def close(self):
        """Close the channel"""
        self._set_state(self.CLOSING)
        self._connection.write_frame(self._build_close_frame(),
                                     self._channel_id)
        self._connection.wait_on_frame(specification.Channel.CloseOk,
                                       self._channel_id)
        self._set_state(self.CLOSED)
        LOGGER.debug('Channel #%i closed', self._channel_id)

    def rpc(self, frame_type, *args, **kwargs):
        """Send a RPC command to the remote server.

        :param class frame_type: The frame type to send
        :param list *args: Positional args
        :param dict **kwargs: Keyword args
        :rtype: pamqp.specification.Frame or None

        """
        self._connection.write_frame(frame_type(*args, **kwargs))
        if frame_type.synchronous:
            return self._connection.wait_on_frame(frame_type.valid_responses)