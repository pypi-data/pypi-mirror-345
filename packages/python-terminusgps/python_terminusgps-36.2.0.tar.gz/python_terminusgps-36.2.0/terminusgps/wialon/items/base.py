from abc import abstractmethod
from typing import Type

from terminusgps.wialon import constants, flags
from terminusgps.wialon.session import WialonSession


class WialonBase:
    def __init__(
        self, id: str | int | None, session: WialonSession, *args, **kwargs
    ) -> None:
        """
        Sets the Wialon session and id for the Wialon object.

        If no id was provided, :py:meth:`create` is executed to get one.

        :param id: An optional Wialon object id.
        :type id: :py:obj:`str` | :py:obj:`int` | :py:obj:`None`
        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises ValueError: If ``id`` was a string that contained non-digit values.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit. Got '{id}'.")

        self._session = session
        self._id = str(id if id else self.create(*args, **kwargs))
        self._name = None
        self._hw_type = None
        self._access_lvl = None

    def __str__(self) -> str:
        """Returns the Wialon object id as a string."""
        return str(self.id)

    def __repr__(self) -> str:
        """Returns the Wialon object type and parameters used to initialize it."""
        return f"{type(self).__name__}(id={self.id}, session={self.session.id})"

    def populate(self) -> None:
        """
        Retrieves and saves the latest data for the item from Wialon.

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.id, "No Wialon object id set."
        response = self.session.wialon_api.core_search_item(
            **{"id": str(self.id), "flags": flags.DataFlag.UNIT_BASE}
        )
        if response is not None:
            item = response.get("item", {})
            self._name = item.get("nm")
            self._hw_type = item.get("cls")
            self._access_lvl = item.get("uacl")

    @property
    def name(self) -> str:
        """Name of the Wialon object."""
        if self._name is None:
            self.populate()
        return str(self._name)

    @property
    def hw_type(self) -> str:
        """Hardware type of the Wialon object."""
        if self._hw_type is None:
            self.populate()
        return str(self._hw_type)

    @property
    def access_lvl(self) -> str:
        """Access level of the Wialon object."""
        if self._access_lvl is None:
            self.populate()
        return str(self._access_lvl)

    @property
    def session(self) -> WialonSession:
        """
        A valid Wialon API session.

        :type: :py:obj:`~terminusgps.wialon.session.WialonSession`

        """

        return self._session

    @property
    def id(self) -> int | None:
        """
        A unique Wialon ID.

        :type: :py:obj:`int` | :py:obj:`None`

        """

        return int(self._id) if self._id else None

    def has_access(self, other: Type["WialonBase"]) -> bool:
        """
        Checks if this Wialon object has access to ``other``.

        :type: :py:obj:`bool`

        """
        response = self.session.wialon_api.core_check_accessors(
            **{"items": [other.id], "flags": False}
        )
        return True if self.id in response.keys() else False

    @abstractmethod
    def create(self, *args, **kwargs) -> int | None:
        """Creates a Wialon object and returns its id."""
        raise NotImplementedError("Subclasses must implement this method.")

    def set_measurement_unit(
        self,
        unit: constants.WialonMeasurementUnit = constants.WialonMeasurementUnit.US,
        convert: bool = False,
    ) -> None:
        """
        Sets the Wialon object's measurement unit to ``unit``.

        :param unit: A Wialon measurement unit.
        :type unit: :py:obj:`~terminusgps.constants.WialonMeasurementUnit`
        :param convert: Whether or not to convert the object's measurements before setting the new unit.
        :type convert: :py:obj:`bool`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.item_update_measure_units(
            **{"itemId": str(self.id), "type": unit, "flags": int(convert)}
        )

    def rename(self, new_name: str) -> None:
        """
        Renames the Wialon object to the new name.

        :param new_name: A new name.
        :type new_name: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.item_update_name(
            **{"itemId": self.id, "name": new_name}
        )
        self._name = new_name

    def delete(self) -> None:
        """
        Deletes the Wialon object.

        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.item_delete_item(**{"itemId": self.id})

    def _get_cfield_id(self, key: str) -> int | None:
        """
        Returns a custom field id by key.

        :param key: A custom field key (name).
        :type key: :py:obj:`str`
        :returns: The custom field's id as an integer, if found.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        cfields = (
            self.session.wialon_api.core_search_item(
                **{"id": str(self.id), "flags": flags.DataFlag.UNIT_CUSTOM_FIELDS}
            )
            .get("item", {})
            .get("flds", {})
            .values()
        )

        for field in cfields:
            if field["n"] == key:
                return int(field["id"])

    def _get_afield_id(self, key: str) -> int | None:
        """
        Returns an admin field id by key.

        :param key: An admin field key (name).
        :type key: :py:obj:`str`
        :returns: The admin field's id as an integer, if found.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        afields = (
            self.session.wialon_api.core_search_item(
                **{"id": str(self.id), "flags": flags.DataFlag.UNIT_ADMIN_FIELDS}
            )
            .get("item", {})
            .get("aflds", {})
            .values()
        )

        for field in afields:
            if field["n"] == key:
                return int(field["id"])

    def update_afield(self, key: str, value: str) -> None:
        """
        Updates an admin field by key.

        :param key: An admin field key (name).
        :type key: :py:obj:`str`
        :param value: A string.
        :type value: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        field_id: int | None = self._get_afield_id(key)

        if field_id is not None:
            self.session.wialon_api.item_update_admin_field(
                **{
                    "itemId": self.id,
                    "id": field_id,
                    "callMode": "update",
                    "n": key,
                    "v": value,
                }
            )
        else:
            self.session.wialon_api.item_update_admin_field(
                **{"itemId": self.id, "callMode": "create", "n": key, "v": value}
            )

    def update_cfield(self, key: str, value: str) -> None:
        """
        Updates a custom field by id.

        :param key: A custom field key (name).
        :type key: :py:obj:`str`
        :param value: A string.
        :type value: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        field_id: int | None = self._get_cfield_id(key)

        if field_id is not None:
            self.session.wialon_api.item_update_custom_field(
                **{
                    "itemId": self.id,
                    "id": field_id,
                    "callMode": "update",
                    "n": key,
                    "v": value,
                }
            )
        else:
            self.session.wialon_api.item_update_custom_field(
                **{"itemId": self.id, "callMode": "create", "n": key, "v": value}
            )

    @property
    def cfields(self) -> dict[str, str]:
        """
        Custom fields for the Wialon object.

        :type: :py:obj:`dict`

        """
        response = self.session.wialon_api.core_search_item(
            **{"id": self.id, "flags": flags.DataFlag.UNIT_CUSTOM_FIELDS}
        )
        fields = response.get("item", {}).get("flds") if response is not None else {}
        return {field["n"]: field["v"] for field in fields.values()} if fields else {}

    @property
    def afields(self) -> dict[str, str]:
        """
        Admin fields for the Wialon object.

        :type: :py:obj:`dict`

        """
        response = self.session.wialon_api.core_search_item(
            **{"id": self.id, "flags": flags.DataFlag.UNIT_ADMIN_FIELDS}
        )
        fields = response.get("item", {}).get("aflds") if response is not None else {}
        return {field["n"]: field["v"] for field in fields.values()} if fields else {}
