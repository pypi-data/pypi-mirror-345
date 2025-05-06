from urllib.parse import quote_plus

from terminusgps.wialon import constants, flags
from terminusgps.wialon.items.base import WialonBase


class WialonUser(WialonBase):
    def create(self, creator_id: str | int, name: str, password: str) -> int | None:
        """
        Creates a new Wialon user.

        :param creator_id: A Wialon user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the user.
        :type name: :py:obj:`str`
        :param password: A password for the user.
        :type password: :py:obj:`str`
        :raises ValueError: If ``creator_id`` is not a digit.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: The Wialon id for the new user, if it was created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_user(
            **{
                "creatorId": str(creator_id),
                "name": name,
                "password": password,
                "dataFlags": str(flags.DataFlag.UNIT_BASE.value),
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def _get_access_response(self, hw_type: str) -> dict:
        """
        Returns a dict of the Wialon objects the user has access to.

        :param hw_type: A hardware type of Wialon objects to generate a list for.
        :type hw_type: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: The Wialon API response.
        :rtype: :py:obj:`dict`

        """
        return self.session.wialon_api.user_get_items_access(
            **{
                "userId": self.id,
                "directAccess": True,
                "itemSuperclass": hw_type,
                "flags": 0x2,
            }
        )

    @property
    def units(self) -> list[str]:
        """
        The user's units.

        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of unit ids the user has access to.
        :rtype: :py:obj:`list`

        """
        response = self._get_access_response(hw_type="avl_unit")
        return [key for key in response.keys()]

    @property
    def groups(self) -> list[str]:
        """
        The user's unit groups.

        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of group ids the user has access to.
        :rtype: :py:obj:`list`

        """
        response = self._get_access_response(hw_type="avl_unit_group")
        return [key for key in response.keys()]

    def has_access(self, other: WialonBase) -> bool:
        """
        Checks if the user has access to ``other``.

        :param other: A Wialon object.
        :type phone: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: :py:obj:`True` if the user can access ``other``, else :py:obj:`False`.
        :rtype: :py:obj:`bool`

        """
        response: dict = self._get_access_response(hw_type=other.hw_type)
        items: list[str] = [key for key in response.keys()]
        return True if str(other.id) in items else False

    def assign_phone(self, phone: str) -> None:
        """
        Assigns a phone number to the user.

        :param phone: A phone number, including country code.
        :type phone: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.add_cproperty("phone", quote_plus(phone))

    def assign_email(self, email: str) -> None:
        """
        Assigns an email address to the user.

        :param phone: An email address.
        :type phone: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.add_cproperty("email", email)

    def grant_access(
        self, item: WialonBase, access_mask: int = constants.ACCESSMASK_UNIT_BASIC
    ) -> None:
        """
        Grants the user access to ``item``.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :param access_mask: A Wialon access mask integer.
        :type access_mask: :py:obj:`int`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.user_update_item_access(
            **{"userId": self.id, "itemId": item.id, "accessMask": access_mask}
        )

    def set_settings_flags(self, flags: int, flags_mask: int) -> None:
        """
        Sets the user's settings flags.

        :param flags: The new user settings flags.
        :type flags: :py:obj:`int`
        :param flags_mask: A user settings flag mask.
        :type flags_mask: :py:obj:`int`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.user_update_user_flags(
            **{"userId": self.id, "flags": flags, "flagsMask": flags_mask}
        )

    def reset_password(self, username: str, email: str, url: str) -> None:
        """
        Sends a password reset email for a user to ``email``.

        :param username: A Wialon user name.
        :type username: :py:obj:`str`
        :param email: A Wialon user email.
        :type email: :py:obj:`str`
        :param url: A password reset URL for the user.
        :type url: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.core_reset_password_request(
            **{"user": username, "url": url, "email": email}
        )

    def update_password(self, old_password: str, new_password: str) -> None:
        """
        Updates the password of the user.

        :param old_password: The user's original password.
        :type old_password: :py:obj:`str`
        :param new_password: A new password.
        :type new_password: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.user_update_password(
            **{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            }
        )

    def verify_auth(self, destination: str, method: str = "email") -> str:
        """
        Sends an authentication code to ``destination`` via ``method``.

        ``Method`` can be ``"email"`` or ``"sms"``.

        :param destination: The email or phone number to send an auth code to.
        :type destination: :py:obj:`str`
        :param method: Email or sms. Default is ``"email"``.
        :type method: :py:obj:`str`
        :raises ValueError: If the method isn't ``"email"`` or ``"sms"``.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: An auth code.
        :rtype: :py:obj:`str`

        """
        if method != "email" or "sms":
            raise ValueError(f"Invalid method '{method}'.")

        response = self.session.wialon_api.user_verify_auth(
            **{
                "userId": self.id,
                "type": 1 if method == "email" else 0,
                "destination": destination,
            }
        )
        return response.get("code")
