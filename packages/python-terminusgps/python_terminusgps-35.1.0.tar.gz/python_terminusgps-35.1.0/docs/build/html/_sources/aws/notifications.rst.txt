Notifications
=============

.. autoclass:: terminusgps.aws.notifications.AsyncNotificationManager
    :members:
    :exclude-members: __weakref__
    :autoclasstoc:

=====
Usage
=====

Phone numbers must be in `E.164`_ format to be passed to a :py:obj:`~terminusgps.aws.notifications.AsyncNotificationManager` method, i.e. ``"+17135555555"``.

You can use :py:func:`~terminusgps.django.validators.validate_e164_phone_number` to confirm a ``to_number`` is correctly formatted.

.. _E.164: https://en.wikipedia.org/wiki/E.164

.. code:: python

    import asyncio
    import uuid

    from terminusgps.aws.notifications import AsyncNotificationManager

    async def main() -> None:
        # Manager requires a group_id
        group_id: str = str(uuid.uuid4())
        message: str = "We know where ours are... do you?"
        async with AsyncNotificationManager(group_id) as manager:

            # Send an sms to one phone number
            # Phone numbers must be in E.164 format
            to_number: str = "+17135555555"
            await manager.send_sms(
                to_number=to_number, message=message, message_id=message_id
            )

            # Send an sms to multiple phone numbers
            to_numbers: list[str] = ["+17135555555", "+12815555555", "+18325555555"]
            await manager.send_sms_batch(to_numbers=to_numbers, message=message)

            # Send a push notification to an AWS resource
            target_arn: str = "arn:aws:sns:us-east-1:555555555555:MyAWSResource"
            await manager.send_push(
                target_arn=target_arn, message=message, message_id=message_id
            )

    if __name__ == "__main__":
        asyncio.run(main())
