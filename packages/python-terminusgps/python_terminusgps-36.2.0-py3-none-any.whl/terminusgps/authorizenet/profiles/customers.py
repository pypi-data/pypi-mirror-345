from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_validation_mode
from terminusgps.authorizenet.controllers import AuthorizenetControllerExecutionError
from terminusgps.authorizenet.profiles.base import AuthorizenetProfileBase


class CustomerProfile(AuthorizenetProfileBase):
    """An Authorizenet customer profile."""

    def __init__(
        self,
        id: int | str | None = None,
        merchant_id: int | str | None = None,
        email: str | None = None,
        desc: str | None = None,
    ) -> None:
        """
        Sets :py:attr:`merchantCustomerId`, :py:attr:`email` and :py:attr:`desc`.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        super().__init__(id=id)
        self._merchantCustomerId = str(merchant_id) if merchant_id else None
        self._email = email
        self._desc = desc

        if not self.id and self.merchantCustomerId or self.email:
            try:
                response = self._authorizenet_get_customer_profile(issuer_info=False)
                self.id = response.profile.customerProfileId
            except AuthorizenetControllerExecutionError:
                self.id = self.create()

    @property
    def validationMode(self) -> str:
        """
        The current Authorizenet validation mode.

        :type: :py:obj:`str`

        """
        return get_validation_mode()

    @property
    def merchantCustomerId(self) -> str | None:
        """
        A merchant designated customer id.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        if self.id and not self._merchantCustomerId:
            response = self._authorizenet_get_customer_profile(issuer_info=False)
            self._merchantCustomerId: str | None = (
                str(response.profile.merchantCustomerId)
                if response is not None
                and hasattr(response.profile, "merchantCustomerId")
                else None
            )
        return self._merchantCustomerId

    @merchantCustomerId.setter
    def merchantCustomerId(self, other: int | str | None) -> None:
        """Sets :py:attr:`merchantCustomerId` to ``other``."""
        updated: bool = other is not None and str(other) != str(
            self._merchantCustomerId
        )
        self._merchantCustomerId = str(other) if other else None
        if updated and self.id is not None:
            self._authorizenet_update_customer_profile()

    @property
    def email(self) -> str | None:
        """
        A customer email address.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        if self.id and self._email is None:
            response = self._authorizenet_get_customer_profile(issuer_info=False)
            self._email: str | None = (
                str(response.profile.email)
                if response is not None and hasattr(response.profile, "email")
                else None
            )
        return self._email

    @email.setter
    def email(self, other: str | None) -> None:
        """Sets :py:attr:`email` to ``other``."""
        updated: bool = other is not None and other != self.email
        self._email = other
        if updated and self.id is not None:
            self._authorizenet_update_customer_profile()

    @property
    def desc(self) -> str | None:
        """
        A customer description.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        if self.id and self._desc is None:
            response = self._authorizenet_get_customer_profile(issuer_info=False)
            self._desc: str | None = (
                str(response.profile.description)
                if response is not None and hasattr(response.profile, "description")
                else None
            )
        return self._desc

    @desc.setter
    def desc(self, other: str | None) -> None:
        """Sets :py:attr:`desc` to ``other``."""
        updated: bool = other is not None and other != self.desc
        self._desc = other
        if updated and self.id is not None:
            self._authorizenet_update_customer_profile()

    def create(self) -> int:
        """
        Creates the customer profile in Authorizenet.

        :raises AssertionError: If neither :py:attr:`merchantCustomerId` nor :py:attr:`email` were set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An id for the new customer profile.
        :rtype: :py:obj:`int`

        """
        assert self.merchantCustomerId or self.email, (
            "Neither 'merchantCustomerId' nor 'email' were set."
        )
        return int(self._authorizenet_create_customer_profile().customerProfileId)

    def update(self) -> None:
        """
        Updates the customer profile in Authorizenet if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_update_customer_profile()

    def delete(self) -> None:
        """
        Deletes the customer profile in Authorizenet and sets :py:attr:`id` to :py:obj:`None` if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_delete_customer_profile()
            self.id = None

    def get_payment_profile_ids(self) -> list[int]:
        """
        Returns a list of payment profile ids assigned to the customer profile.

        :returns: A list of payment profile ids.
        :rtype: :py:obj:`list`

        """
        response = self._authorizenet_get_customer_profile()
        if response is not None and hasattr(response.profile, "paymentProfiles"):
            return [
                int(p.customerPaymentProfileId)
                for p in response.profile.paymentProfiles
            ]
        return []

    def get_address_profile_ids(self) -> list[int]:
        """
        Returns a list of address profile ids assigned to the customer profile.

        :returns: A list of address profile ids.
        :rtype: :py:obj:`list`

        """
        response = self._authorizenet_get_customer_profile()
        if response is not None and hasattr(response.profile, "shipToList"):
            return [int(p.customerAddressId) for p in response.profile.shipToList]
        return []

    def _generate_customer_profile_ex_type(
        self,
    ) -> apicontractsv1.customerProfileExType:
        """
        Generates and returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`.

        :returns: A customer profile object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`

        """
        cprofile = apicontractsv1.customerProfileExType()

        if self.id is not None:
            cprofile.customerProfileId = self.id
        if self.merchantCustomerId is not None:
            cprofile.merchantCustomerId = self.merchantCustomerId
        if self.email is not None:
            cprofile.email = self.email
        if self.desc is not None:
            cprofile.description = self.desc

        return cprofile

    def _generate_customer_profile_type(self) -> apicontractsv1.customerProfileType:
        """
        Generates and returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileType`.

        :returns: A customer profile object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.customerProfileType`

        """
        cprofile = apicontractsv1.customerProfileType()

        if self.merchantCustomerId is not None:
            cprofile.merchantCustomerId = self.merchantCustomerId
        if self.email is not None:
            cprofile.email = self.email
        if self.desc is not None:
            cprofile.description = self.desc

        return cprofile

    def _authorizenet_get_customer_profile(
        self, issuer_info: bool = True
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerProfileRequest` using the Authorizenet API.

        `getCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile>`_

        :param issuer_info: Whether or not to include issuer info in the response. Default is :py:obj:`True`.
        :type issuer_info: :py:obj:`bool`
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.getCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            includeIssuerInfo=str(issuer_info).lower(),
        )

        if self.id:
            request.customerProfileId = self.id
        if self.merchantCustomerId:
            request.merchantCustomerId = self.merchantCustomerId
        if self.email:
            request.email = self.email

        controller = apicontrollers.getCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_create_customer_profile(
        self, validate: bool = False
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerProfileRequest` using the Authorizenet API.

        `createCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-profile>`_

        :param validate: Whether or not to validate the customer profile in Authorizenet.
        :type validate: :py:obj:`bool`
        :raises AssertionError: If neither :py:attr:`merchantCustomerId` nor :py:attr:`email` were set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.merchantCustomerId or self.email, (
            "Neither 'merchantCustomerId' nor 'email' were set."
        )

        request = apicontractsv1.createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=self._generate_customer_profile_type(),
        )
        if validate:
            request.validationMode = self.validationMode

        controller = apicontrollers.createCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_update_customer_profile(
        self, validate: bool = False
    ) -> dict | None:
        """
        Executes an :py:obj:`~authorizenet.apicontractsv1.updateCustomerProfileRequest` using the Authorizenet API.

        `updateCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-profile>`_

        :param validate: Whether or not to validate the customer profile in Authorizenet.
        :type validate: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=self._generate_customer_profile_ex_type(),
        )
        if validate:
            request.validationMode = self.validationMode

        controller = apicontrollers.updateCustomerProfileController(request)
        return self.execute_controller(controller)

    def _authorizenet_delete_customer_profile(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerProfileRequest` using the Authorizenet API.

        `deleteCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
        )

        controller = apicontrollers.deleteCustomerProfileController(request)
        return self.execute_controller(controller)
