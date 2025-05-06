import pytest

from tests.settings import get_connection, FIXED_DOCUMENT_ID_FOR_TESTING, BASE_DIR
from py_glpi.resources.documents import Documents, DocumentRelatedItems, GLPIItem
from py_glpi.resources.tickets import Tickets

connection = get_connection()

def test_document_all():
    document = Documents(connection).all()
    assert document


def test_document_download():
    document = Documents(connection).get(FIXED_DOCUMENT_ID_FOR_TESTING).download(BASE_DIR / 'files' / 'downloaded' / 'test.png')
    assert document


def test_document_create():
    document = Documents(connection).create(BASE_DIR / 'files' / 'fox.png', 'Firefox Icon', True)
    assert document
    

def test_document_item_parent():
    document_items: GLPIItem = DocumentRelatedItems(connection).get(FIXED_DOCUMENT_ID_FOR_TESTING)
    tickets = document_items.get_related_parent(Tickets, 'items_id')
    assert tickets
    
    
def test_document_item_all():
    document_items: GLPIItem = DocumentRelatedItems(connection).all()
    assert document_items


def test_document_item_parent():
    document_item: GLPIItem = DocumentRelatedItems(connection).get(FIXED_DOCUMENT_ID_FOR_TESTING)
    tickets = document_item.get_related_parent(Tickets, 'items_id')
    assert tickets
