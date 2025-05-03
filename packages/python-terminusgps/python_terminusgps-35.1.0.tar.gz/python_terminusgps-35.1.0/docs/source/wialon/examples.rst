Usage Examples
==============

===============================
Create a new user and rename it
===============================

----------------------------------------------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.wialon.session.WialonSession` and :py:obj:`~terminusgps.wialon.items.user.WialonUser`.
----------------------------------------------------------------------------------------------------------------------

Let's also import :py:obj:`~terminusgps.wialon.utils.generate_wialon_password` so we don't have to come up with a valid Wialon password ourselves.

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUser
    from terminusgps.wialon.utils import generate_wialon_password

----------------------------------------------------------------
2. Open the session in a context manager and instantiate a user.
----------------------------------------------------------------

It is recommended to only use keyword arguments when instantiating a :py:obj:`~terminusgps.wialon.items.base.WialonBase` object.

.. code:: python

    with WialonSession(token="my_wialon_api_token") as session:
        user = WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="test_user",
            password=generate_wialon_password(32)
        )
        print(f"{user.name = }") # user.name = "test_user"

-----------------------------------------------------------------------------------------------------------
3. Within the context manager, :py:meth:`~terminusgps.wialon.items.base.WialonBase.rename` can be executed.
-----------------------------------------------------------------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...

        unit.rename("super_test_user")
        print(f"{user.name = }") # user.name = "super_test_user"
        # Session is logged out after exiting scope

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit
    from terminusgps.wialon.utils import generate_wialon_password

    with WialonSession(token="my_secure_wialon_token") as session:
        unit = WialonUnit(
            id=None,
            session=session,
            creator_id="123",
            name="test_user",
            password=generate_wialon_password(32)
        )
        print(f"{unit.name = }") # user.name = "test_user"
        unit.rename("super_test_user")
        print(f"{unit.name = }") # user.name = "super_test_user"


============================================
Create an account and migrate a unit into it
============================================

------------------------------------------------------------------------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.wialon.session.WialonSession`, :py:mod:`~terminusgps.wialon.items`, and :py:mod:`~terminusgps.wialon.constants`.
------------------------------------------------------------------------------------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon import items, constants

--------------------------
2. Create an account user.
--------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        account_user = items.WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="account_user",
            password="super_secure_password1!",
        )

--------------------------------------------
3. Create a resource using the account user.
--------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        account_resource = items.WialonResource(
            id=None,
            session=session,
            creator_id=account_user.id,
            name="account_resource",
        )

------------------------------------------------------------------
4. Retrieve a :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`.
------------------------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        unit = items.WialonUnit(id="12345678", session=session)

------------------------------------------------
5. Grant the account user migration permissions.
------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        account_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION)

--------------------------------------------------------
6. Transform the resource into an account and enable it.
--------------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        account_resource.create_account("terminusgps_ext_hist")
        account_resource.enable()

-------------------------------------
7. Migrate the unit into the account.
-------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        account_resource.migrate_unit(unit)


-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon import items, constants

    with WialonSession(token="my_secure_wialon_token") as session:
        account_user = items.WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="account_user",
            password="super_secure_password1!",
        )
        account_resource = items.WialonResource(
            id=None,
            session=session,
            creator_id=account_user.id,
            name="account_resource",
        )
        unit = items.WialonUnit(id="12345678", session=session)
        account_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION)
        account_resource.create_account("terminusgps_ext_hist")
        account_resource.enable()
        account_resource.migrate_unit(unit)

==========================
Add a driver to a resource
==========================
------------------------------------------------------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.wialon.session.WialonSession` and :py:obj:`~terminusgps.wialon.items.resource.WialonResource`.
------------------------------------------------------------------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonResource

------------------------------------------------------------------------------------
2. Instantiate a :py:obj:`~terminusgps.wialon.items.resource.WialonResource` object.
------------------------------------------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        resource = WialonResource(id="12345678", session=session)

-----------------------------------------------------------------------------------
3. Call :py:meth:`~terminusgps.wialon.items.resource.WialonResource.create_driver`.
-----------------------------------------------------------------------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        resource.create_driver(
            name="test_driver",
            code="1234",
            desc="A test driver.",
            phone="+15555555555",
            mobile_auth_code="1234",
            custom_fields={"my_field_key": "my_field_value"}
        )

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonResource

    with WialonSession(token="my_secure_wialon_token") as session:
        resource = WialonResource(id="12345678", session=session)
        resource.create_driver(
            name="test_driver",
            code="1234",
            desc="A test driver.",
            phone="+15555555555",
            mobile_auth_code="1234",
            custom_fields={"my_field_key": "my_field_value"}
        )

==========================================
Update a unit's ``to_number`` custom field
==========================================

----------------------------------------------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.wialon.session.WialonSession` and :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`.
----------------------------------------------------------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit

---------------------
2. Retrieve the unit.
---------------------

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        unit = WialonUnit(id="12345678", session=session)

---------------------------------------------------------------------------
3. Call :py:meth:`~terminusgps.wialon.items.base.WialonBase.update_cfield`.
---------------------------------------------------------------------------

Assuming you know the ``to_number``'s custom field id, call :py:meth:`~terminusgps.wialon.items.base.WialonBase.update_cfield` using it.

If you don't, call :py:meth:`~terminusgps.wialon.items.base.WialonBase.get_cfield_id` first, then pass the id into :py:meth:`~terminusgps.wialon.items.base.WialonBase.update_cfield`.

.. code:: python

    with WialonSession(token="my_secure_wialon_token") as session:
        ...
        to_number_id: int | None = unit.get_cfield_id("to_number") # May return None if key is invalid.
        unit.update_cfield(id=to_number_id, key="to_number", value="+15555555555")
        unit.cfields["to_number"] # "+15555555555"

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit

    with WialonSession(token="my_secure_wialon_token") as session:
        unit = WialonUnit(id="12345678", session=session)
        to_number_id: int | None = unit.get_cfield_id("to_number") # Will return None if the field isn't found.
        unit.update_cfield(id=to_number_id, key="to_number", value="+15555555555")
        print(unit.cfields["to_number"]) # "+15555555555"
