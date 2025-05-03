import os
from contextlib import AsyncExitStack

from aiobotocore.session import AioSession


class AsyncNotificationManager:
    """Asyncronously delivers notifications using `AWS End User Messaging <https://docs.aws.amazon.com/end-user-messaging/>`_."""

    def __init__(
        self,
        origin_pool_arn: str | None = os.getenv("AWS_MESSAGING_ORIGIN_POOL"),
        configuration_set: str | None = os.getenv("AWS_MESSAGING_CONFIGURATION"),
        max_sms_price: str = "0.20",
        max_voice_price: str = "0.20",
        region_name: str = "us-east-1",
        debug_enabled: bool = False,
    ) -> None:
        """
        Sets attributes on the notification manager.

        :param origin_pool_arn: A phone pool ARN for notification dispatch. Default is :envvar:`AWS_MESSAGING_ORIGIN_POOL`.
        :type origin_pool_arn: :py:obj:`str` | :py:obj:`None`
        :param configuration_set: An end-user messaging configuration set ARN. Default is :envvar:`AWS_MESSAGING_CONFIGURATION`.
        :type configuration_set: :py:obj:`str` | :py:obj:`None`
        :param max_sms_price: Max price to spend on a single SMS message.
        :type max_sms_price: :py:obj:`str`
        :param max_voice_price: Max price to spend per minute on a single voice message.
        :type max_voice_price: :py:obj:`str`
        :param region_name: An AWS region name used to open an AWS client.
        :type region_name: :py:obj:`str`
        :param debug_enabled: Whether or not to enable debug mode.
        :type debug_enabled: :py:obj:`None`
        :raises ValueError: If ``origin_pool_arn`` wasn't provided and :envvar:`AWS_MESSAGING_ORIGIN_POOL` wasn't set.
        :raises ValueError: If ``configuration_set`` wasn't provided and :envvar:`AWS_MESSAGING_CONFIGURATION` wasn't set.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if origin_pool_arn is None:
            raise ValueError(f"'origin_pool_arn' is required, got '{origin_pool_arn}'.")
        if configuration_set is None:
            raise ValueError(
                f"'configuration_set' is required, got '{configuration_set}'."
            )

        self._exit_stack = AsyncExitStack()
        self._pinpoint_client = None
        self._region_name = region_name
        self._origin_pool_arn = origin_pool_arn
        self._configuration_set = configuration_set
        self._max_sms_price = max_sms_price
        self._max_voice_price = max_voice_price
        self._debug = debug_enabled

    async def __aenter__(self) -> "AsyncNotificationManager":
        """
        Creates asyncronous clients.

        :returns: The notification manager.
        :rtype: :py:obj:`~terminusgps.aws.notifications.AsyncNotificationManager`

        """
        session = AioSession()
        self._pinpoint_client = await self._exit_stack.enter_async_context(
            session.create_client("pinpoint-sms-voice-v2", region_name=self.region_name)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Destroys asyncronous clients.

        :param exc_type: Exception type.
        :param exc_val: Exception value.
        :param exc_tb: Exception traceback.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def region_name(self) -> str:
        """
        An AWS region name.

        :type: :py:obj:`str`

        """
        return self._region_name

    @property
    def configuration_set(self) -> str:
        return self._configuration_set

    @property
    def origin_pool(self) -> str:
        return self._origin_pool_arn

    @property
    def max_sms_price(self) -> str:
        return self._max_sms_price

    @property
    def max_voice_price(self) -> str:
        return self._max_voice_price

    @property
    def debug(self) -> bool:
        return self._debug

    async def send_sms(
        self,
        phone: str,
        message: str,
        ttl: int = 300,
        dry_run: bool = False,
        feedback: bool = False,
    ) -> dict:
        """
        Texts ``message`` to ``phone`` via sms.

        :param phone: A destination phone number.
        :type phone: :py:obj:`str`
        :param message: A message body.
        :type message: :py:obj:`str`
        :param ttl: Time to live in ms. Default is ``300``.
        :type ttl: :py:obj:`int`
        :param dry_run: Whether or not to execute the voice message as a dry run. Default is :py:obj:`False`.
        :type dry_run: :py:obj:`bool`
        :param feedback: Whether or not to include message feedback in the response. Default is :py:obj:`False`.
        :type feedback: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`_pinpoint_client` wasn't set.
        :returns: A voice message response.
        :rtype: :py:obj:`dict`

        """
        assert self._pinpoint_client, "Asyncronous client wasn't set."
        return await self._pinpoint_client.send_text_message(
            **{
                "DestinationPhoneNumber": phone,
                "OriginationIdentity": self.origin_pool,
                "MessageBody": message,
                "MessageType": "TRANSACTIONAL",
                "ConfigurationSetName": self.configuration_set,
                "MaxPrice": self.max_sms_price,
                "TimeToLive": ttl,
                "DryRun": dry_run or self.debug,
                "MessageFeedbackEnabled": feedback,
            }
        )

    async def send_voice(
        self,
        phone: str,
        message: str,
        ttl: int = 300,
        voice_id: str = "Joanna",
        dry_run: bool = False,
        feedback: bool = False,
    ) -> dict:
        """
        Calls ``phone`` and reads ``message`` aloud.

        :param phone: A destination phone number.
        :type phone: :py:obj:`str`
        :param message: A message body.
        :type message: :py:obj:`str`
        :param ttl: Time to live in ms. Default is ``300``.
        :type ttl: :py:obj:`int`
        :param voice_id: A voice id to use for speech synthesis.
        :type voice_id: :py:obj:`str`
        :param dry_run: Whether or not to execute the voice message as a dry run. Default is :py:obj:`False`.
        :type dry_run: :py:obj:`bool`
        :param feedback: Whether or not to include message feedback in the response. Default is :py:obj:`False`.
        :type feedback: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`_pinpoint_client` wasn't set.
        :returns: A voice message response.
        :rtype: :py:obj:`dict`

        """
        assert self._pinpoint_client, "Asyncronous client wasn't set."
        return await self._pinpoint_client.send_voice_message(
            **{
                "DestinationPhoneNumber": phone,
                "OriginationIdentity": self.origin_pool,
                "MessageBody": message,
                "MessageBodyTextType": "TEXT",
                "VoiceId": voice_id.upper(),
                "ConfigurationSetName": self.configuration_set,
                "MaxPricePerMinute": self.max_voice_price,
                "TimeToLive": ttl,
                "DryRun": dry_run or self.debug,
                "MessageFeedbackEnabled": feedback,
            }
        )
