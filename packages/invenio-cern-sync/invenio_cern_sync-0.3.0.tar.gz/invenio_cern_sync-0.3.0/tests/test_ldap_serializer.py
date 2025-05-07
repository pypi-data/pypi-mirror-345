# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-CERN-sync is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests users serializers."""

from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest

from invenio_cern_sync.errors import InvalidLdapUser
from invenio_cern_sync.ldap.serializer import serialize_ldap_users


def test_serialize_ldap_users(app, ldap_users):
    """Test serialization of existing LDAP user."""
    invenio_users = serialize_ldap_users(ldap_users)
    first_user = next(invenio_users)

    assert first_user["email"] == "john.doe0@cern.ch"
    assert first_user["username"] == "jdoe0"
    assert first_user["user_identity_id"] == "12340"
    assert first_user["preferences"]["locale"] == "en"

    profile = first_user["user_profile"]
    assert profile["affiliations"] == "CERN"
    assert profile["department"] == "IT"
    assert profile["group"] == "CA"
    assert profile["section"] == "IR"
    assert profile["family_name"] == "Doe 0"
    assert profile["full_name"] == "John Doe 0"
    assert profile["given_name"] == "John"
    assert profile["mailbox"] == "M123ABC0"
    assert profile["person_id"] == "12340"

    extra_data = first_user["remote_account_extra_data"]
    assert extra_data["identity_id"] == "12340"
    assert extra_data["uidNumber"] == "222220"
    assert extra_data["username"] == "jdoe0"


def test_serialize_alternative_mappers(app, monkeypatch, ldap_users):
    """Test serialization of existing LDAP user."""
    # Temporarily change config variables for custom mappers
    monkeypatch.setitem(
        app.config,
        "CERN_SYNC_LDAP_USERPROFILE_MAPPER",
        lambda _: dict(fake_key="fake_profile_value"),
    )
    monkeypatch.setitem(
        app.config,
        "CERN_SYNC_LDAP_USER_EXTRADATA_MAPPER",
        lambda _: dict(fake_key="fake_extra_data_value"),
    )

    invenio_users = serialize_ldap_users(ldap_users)
    first_user = next(invenio_users)

    assert first_user["email"] == "john.doe0@cern.ch"
    assert first_user["username"] == "jdoe0"
    assert first_user["user_identity_id"] == "12340"
    assert first_user["preferences"]["locale"] == "en"

    profile = first_user["user_profile"]
    assert len(profile.keys()) == 1
    assert profile["fake_key"] == "fake_profile_value"

    extra_data = first_user["remote_account_extra_data"]
    assert len(extra_data.keys()) == 1
    assert extra_data["fake_key"] == "fake_extra_data_value"


@pytest.mark.parametrize(
    "missing_field",
    [
        "employeeID",
        "mail",
        "cn",
    ],
)
@patch("invenio_cern_sync.ldap.serializer.current_app")
def test_serialize_invalid_ldap_users(mock_app, app, missing_field):
    """Test serialization of invalid LDAP user."""
    mock_logger = MagicMock()
    mock_app.logger = mock_logger

    required_fields = {
        "employeeID": [b"12340"],
        "mail": [b"john.doe0@cern.ch"],
        "cn": [b"jdoe0"],
    }
    employee_id = "12340" if missing_field != "employeeID" else "unknown"
    excp = InvalidLdapUser(missing_field, employee_id)

    without_missing_field = deepcopy(required_fields)
    del without_missing_field[missing_field]
    list(serialize_ldap_users([without_missing_field]))
    mock_logger.warning.assert_any_call(f"{str(excp)} Skipping this account...")


def test_serialize_ldap_users_missing_optional_fields(app):
    """Test serialization of LDAP user with missing fields."""
    ldap_users = [
        {
            "employeeID": [b"12340"],
            "mail": [b"john.doe0@cern.ch"],
            "cn": [b"jdoe0"],
            "uidNumber": [b"222220"],
        }
    ]

    invenio_users = serialize_ldap_users(ldap_users)
    first_user = next(invenio_users)

    assert first_user["email"] == "john.doe0@cern.ch"
    assert first_user["username"] == "jdoe0"
    assert first_user["user_identity_id"] == "12340"
    assert first_user["preferences"]["locale"] == "en"

    profile = first_user["user_profile"]
    assert profile["affiliations"] == ""
    assert profile["department"] == ""
    assert profile["family_name"] == ""
    assert profile["full_name"] == ""
    assert profile["given_name"] == ""
    assert profile["group"] == ""
    assert profile["mailbox"] == ""
    assert profile["person_id"] == "12340"
    assert profile["section"] == ""

    extra_data = first_user["remote_account_extra_data"]
    assert extra_data["identity_id"] == "12340"
    assert extra_data["uidNumber"] == "222220"
    assert extra_data["username"] == "jdoe0"
