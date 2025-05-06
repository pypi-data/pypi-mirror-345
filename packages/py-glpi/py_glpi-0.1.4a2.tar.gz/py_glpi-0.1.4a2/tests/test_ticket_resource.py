import pytest

from tests.settings import (
    get_connection, 
    FIXED_TICKET_ID_FOR_TESTING, 
    FIXED_USER_ID_FOR_TESTING, 
    FIXED_DOCUMENT_ID_FOR_TESTING, 
    BASE_DIR
)
from py_glpi.resources.tickets import Tickets, TicketUsers, Categories, Origins, TicketSLAs
from py_glpi.models import FilterCriteria

connection = get_connection()

def test_ticket_get():
    ticket = Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING)
    assert ticket
    

def test_ticket_search():
    filter = FilterCriteria("Ticket.TicketValidation.User.name", "contains", "")
    search = Tickets(connection).search(filter)
    assert search


def test_ticket_user_search():
    filter = FilterCriteria("Ticket_User.User.id", "morethan", "1")
    search = TicketUsers(connection).search(filter)
    assert search


def test_ticket_user_parent_get():
    ticket_user = TicketUsers(connection).get(1)
    user = ticket_user.related_user
    ticket = ticket_user.related_ticket
    assert user
    assert ticket


def test_ticket_get_assigned_users():
    ticket = Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING)
    users = ticket.get_involved_users()
    assert users
    

def test_ticket_update():
    ticket = Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING)
    ticket = ticket.update(name="Test Ticket API", priority=2)
    assert ticket


def test_ticket_category_all():
    categories = Categories(connection).all()
    assert categories


def test_ticket_category_filtering():
    categories = Categories(connection).all().filter(level=3)
    assert categories


def test_ticket_origin_all():
    origins = Origins(connection).all()
    assert origins


def test_ticket_sla_all():
    origins = TicketSLAs(connection).all()
    assert origins


def test_ticket_documents():
    documents = Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING).get_linked_documents()
    print(documents)
    assert documents


def test_attach_ticket_document():
    assert Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING).attach_document(
        BASE_DIR / 'files' / 'fox.png', 
        'Firefox Icon'
    )

def test_ticket_get_parents():
    ticket = Tickets(connection).get(FIXED_TICKET_ID_FOR_TESTING)
    category = ticket.category
    origin = ticket.origin
    tto_sla = ticket.tto_sla
    ttr_sla = ticket.ttr_sla
    assert category 
    assert origin 
    assert tto_sla 
    assert ttr_sla


def test_ticket_creation_assignment_and_document_linking():
    resource = Tickets(connection)
    ticket = resource.create(
        name = "PyTest GLPI Ticket",
        content= "<p>Ticket creado por un Test del API Rest</p>",
        itilcategories_id=12
    )
    ticket.add_applicant(FIXED_USER_ID_FOR_TESTING)
    ticket.link_document(FIXED_DOCUMENT_ID_FOR_TESTING)
    ticket.delete()
    assert ticket