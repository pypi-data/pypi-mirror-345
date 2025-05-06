import pytest

from tests.settings import get_connection, FIXED_USER_ID_FOR_TESTING
from py_glpi.resources.auth import Users
from py_glpi.models import FilterCriteria

connection = get_connection()

def test_users_all():
    users = Users(connection).all()
    assert users


def test_users_get():
    user = Users(connection).get(FIXED_USER_ID_FOR_TESTING)
    assert user


def test_users_get_related_tickets():
    user = Users(connection).get(FIXED_USER_ID_FOR_TESTING)
    applicant_tickets = user.get_requested_tickets()
    observer_tickets = user.get_observing_tickets()
    assigned_tickets = user.get_assigned_tickets()
    assert applicant_tickets and observer_tickets and assigned_tickets


def test_users_search():
    filter1 = FilterCriteria("User.name", "contains", "mar")
    filter2 = FilterCriteria("User.name", "contains", "ari")
    filter3 = FilterCriteria("User.name", "contains", "rin")
    filter = filter1 & filter2 | filter3
    result = Users(connection).search(filter)
    assert result


def test_users_update():
    resource = Users(connection).get(FIXED_USER_ID_FOR_TESTING).update(firstname="Rick", mobile="+584242569443")
    assert resource
