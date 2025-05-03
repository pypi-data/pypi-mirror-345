import dataclasses
import datetime
import typing

import wialon.api
from django.conf import settings
from loguru import logger


@dataclasses.dataclass
class WialonAPICall:
    action: str
    timestamp: datetime.datetime
    args: tuple
    kwargs: dict
    result: typing.Any = None
    error: Exception | None = None


class Wialon(wialon.api.Wialon):
    def __init__(
        self,
        debug: bool = False,
        log_level: int = 10,
        log_days: int = 10,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.call_history: list[WialonAPICall] = []
        logger.add(
            f"logs/{self.__class__.__name__}.log",
            level=log_level,
            retention=f"{log_days} days",
            diagnose=debug,
        )

    @property
    def total_calls(self) -> int:
        return len(self.call_history)

    def token_login(self, *args, **kwargs) -> typing.Any:
        kwargs["appName"] = "python-terminusgps"
        return self.call("token_login", *args, **kwargs)

    def call(self, action_name: str, *argc, **kwargs) -> typing.Any:
        logger.debug(f"Executing '{action_name}'...")
        call_record = WialonAPICall(
            action=action_name,
            timestamp=datetime.datetime.now(),
            args=argc,
            kwargs=kwargs,
        )

        try:
            result = super().call(action_name, *argc, **kwargs)
            call_record.result = result
            logger.debug(f"Executed '{action_name}' successfully.")
            return result
        except wialon.api.WialonError as e:
            call_record.error = e
            logger.warning(f"Failed to execute '{action_name}': '{e}'")
            return
        finally:
            self.call_history.append(call_record)


class WialonSession:
    def __init__(
        self,
        token: str | None = None,
        sid: str | None = None,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
        log_level: int = 10,
        log_days: int = 10,
        debug: bool = False,
    ) -> None:
        """
        Starts or continues a Wialon API session.

        :param token: An optional Wialon API token. Default is :confval:`WIALON_TOKEN`.
        :type token: :py:obj:`str` | :py:obj:`None`
        :param sid: An optional Wialon API session id. If provided, the session is continued.
        :type sid: :py:obj:`str` | :py:obj:`None`
        :param scheme: HTTP request scheme to use. Default is ``"https"``.
        :type scheme: :py:obj:`str`
        :param host: Wialon API host url. Default is ``"hst-api.wialon.com"``.
        :type host: :py:obj:`str`
        :param port: Wialon API host port. Default is ``443``.
        :type port: :py:obj:`int`
        :param log_level: Level of emitted logs. Default is ``10``.
        :type log_level: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        logger.add(
            f"logs/{self.__class__.__name__}.log",
            level=log_level,
            retention=f"{log_days} days",
            diagnose=debug or settings.DEBUG if settings.configured else False,
        )
        self._token = token or settings.WIALON_TOKEN if settings.configured else None
        self._username = None
        self._gis_sid = None
        self._hw_gp_ip = None
        self._wsdk_version = None
        self._uid = None
        self.wialon_api = Wialon(
            scheme=scheme,
            host=host,
            port=port,
            sid=sid,
            log_level=log_level,
            log_days=log_days,
            debug=debug,
        )

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        """
        Logs into the Wialon API using :py:meth:`login`.

        :raises AssertionError: If the Wialon API token was not set.
        :returns: A valid Wialon API session.
        :rtype: :py:obj:`~terminusgps.wialon.session.WialonSession`

        """
        assert self.token, "Wialon API token was not set"
        self.login(self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Logs out of the session by calling :py:meth:`logout`.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.logout()

    @property
    def active(self) -> bool:
        """
        Whether or not the session is logged in.

        :type: :py:obj:`bool`
        :value: :py:obj:`False`

        """
        return bool(self.id)

    @property
    def gis_geocode(self) -> str | None:
        """
        Gis geocode URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_geocode

    @property
    def gis_render(self) -> str | None:
        """
        Gis rendering URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_render

    @property
    def gis_routing(self) -> str | None:
        """
        Gis routing URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_routing

    @property
    def gis_search(self) -> str | None:
        """
        Gis search URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_search

    @property
    def gis_sid(self) -> str | None:
        """
        Gis session id.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_sid

    @property
    def host(self) -> str | None:
        """
        IP of the client hosting the Wialon session.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._host

    @property
    def hw_gw_ip(self) -> str | None:
        """
        Hardware gateway IP.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._hw_gw_ip

    @property
    def hw_gw_dns(self) -> str | None:
        """
        Hardware gateway domain name, should evaluate to :py:attr:`hw_gw_ip` if present.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._hw_gw_dns

    @property
    def wsdk_version(self) -> str | None:
        """
        The Wialon Source Developer Kit (WSDK) version number of the session.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._wsdk_version

    @property
    def uid(self) -> str | None:
        """
        A Wialon user ID this session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`
        """
        return self._uid

    @property
    def username(self) -> str | None:
        """
        A Wialon username the session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._username

    @property
    def id(self) -> str | None:
        """
        Shortcut property for :py:attr:`WialonSession.wialon_api.sid`.

        Returns :py:obj:`None` if the session wasn't logged in.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self.wialon_api.sid

    @property
    def token(self) -> str:
        """
        A Wialon API token set during :py:meth:`WialonSession.__init__`.

        Default token value is :confval:`WIALON_TOKEN`.

        :type: :py:obj:`str`
        :value: :confval:`WIALON_TOKEN`

        """
        return str(self._token)

    def login(self, token: str, flags: int = sum([0x1, 0x2, 0x20])) -> str:
        """
        Logs into the Wialon API and starts a new session.

        :param token: An active Wialon API token.
        :type token: :py:obj:`str`
        :param flags: A login response flag integer.
        :type flags: :py:obj:`int`
        :raises WialonError: If the login fails.
        :raises AssertionError: If the login token was not set.
        :returns: The new session id.
        :rtype: :py:obj:`str`

        """
        try:
            logger.debug("Logging into Wialon API session...")
            response = self.wialon_api.token_login(**{"token": token, "fl": flags})
            self._set_login_response(response)
            logger.debug(f"Logged into Wialon API session '{response.get('eid')}'")
            return response.get("eid")
        except (wialon.api.WialonError, AssertionError) as e:
            logger.critical(f"Failed to login to Wialon API: '{e}'")
            raise

    def logout(self) -> None:
        """
        Logs out of the Wialon API session.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        logger.debug("Logging out of Wialon API session...")
        response: dict = self.wialon_api.core_logout({})
        self.wialon_api.sid = None

        if response.get("error") != 0:
            logger.warning(f"Failed to logout of session: '{response.get('message')}'")
        else:
            logger.debug(
                f"Logged out after {self.wialon_api.total_calls} Wialon API calls."
            )

    def _set_login_response(self, login_response: dict) -> None:
        """
        Sets the Wialon API session's attributes based on a login response.

        :param login_response: A response returned from :py:meth:`login` or :py:meth:`duplicate`.
        :type login_response: :py:obj:`dict`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.wialon_api.sid = login_response.get("eid")
        self._gis_geocode = login_response.get("gis_geocode")
        self._gis_render = login_response.get("gis_render")
        self._gis_routing = login_response.get("gis_routing")
        self._gis_search = login_response.get("gis_search")
        self._gis_sid = login_response.get("gis_sid")
        self._host = login_response.get("host")
        self._hw_gw_dns = login_response.get("hw_gw_dns")
        self._hw_gw_ip = login_response.get("hw_gw_ip")
        self._uid = login_response.get("user", {}).get("id")
        self._nm = login_response.get("user", {}).get("nm")
        self._username = login_response.get("au")
        self._video_service_url = login_response.get("video_service_url")
        self._wsdk_version = login_response.get("wsdk_version")
