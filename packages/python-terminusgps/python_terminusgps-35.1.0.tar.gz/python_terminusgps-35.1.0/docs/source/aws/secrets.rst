Secrets
=======

.. currentmodule:: terminusgps.aws.secrets

.. py:function:: get_secret(name, [region="us-east-1"]) -> dict[str, str]
   
    Logs into the default AWS CLI session and returns a secret value by name.

    :param name: An AWS `secretsmanager`_ secret name.
    :type name: :py:obj:`str`
    :param region: An AWS region name. Default is ``"us-east-1"``.
    :type region: :py:obj:`str`
    :returns: The secret as a dictionary.
    :rtype: :py:obj:`dict`

    .. _secretsmanager: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
