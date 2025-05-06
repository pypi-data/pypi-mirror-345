from py_glpi.models import GLPIItem, Resource, ItemList
from dataclasses import dataclass

from html import unescape

from arrow import arrow
from typing import Literal

from py_glpi.resources.documents import (
    Document_Item, 
    Documents, 
    Document, 
    Path
)

# Constant index starts from 1 for GLPI -> 1 = Muy Baja, 2 = Baja...
URGENCIES = [
    'Muy Baja',
    'Baja',
    'Media',
    'Alta',
    'Muy Alta'
]

IMPACTS = [
    'Muy Bajo',
    'Bajo',
    'Medio',
    'Alto',
    'Muy Alto'
]

PRIORITIES = [
    'Muy Baja',
    'Baja',
    'Media',
    'Alta',
    'Muy Alta',
    'Primordial'
]

STATUSES = [
    'Nuevo',
    'En Curso (Asignado)',
    'En Curso (Planificado)',
    'En Espera',
    'Resuelto',
    'Cerrado', 
]

TICKET_INVOLVED_USER_TYPES = [
    'Solicitante',
    'Encargado',
    'Observador'
]

TICKET_TYPES = [
    "N.A",
    "Incidencia",
    "Solicitud"
]


@dataclass(repr=False)
class ITILCategory(GLPIItem):

    name: str
    itilcategories_id: str | int
    """ Name / ID of the parent category """
    level: int
    """ Hierarchy Level """

    def post_initialization(self):
        try:
            self.itilcategories_id = unescape(self.itilcategories_id)
        except Exception:
            pass

    @property
    def parent_category(self):
        parent: ITILCategory = self.get_related_parent(Categories, 'itilcategories_id')
        return parent if self.itilcategories_id else None


class Categories(Resource[ITILCategory]):
    resource_type = ITILCategory


@dataclass(repr=False)
class RequestType(GLPIItem):

    name: str
    is_active: bool | int


class Origins(Resource[RequestType]):
    resource_type = RequestType


@dataclass(repr=False)
class SLA(GLPIItem):
    
    name: str
    type: int
    """ SLA Type, where:

    0: Time to Solve
    1: Time to Respond
    """
    number_time: int
    """ Time quantity. """
    definition_time: int
    """ Time dimension. """


class TicketSLAs(Resource[SLA]):
    resource_type = SLA


@dataclass(repr=False)
class Ticket_User(GLPIItem):

    tickets_id: int | str
    users_id: int | str
    type: int | str
    """ User's participation type/role in the ticket. """

    @property
    def related_ticket(self):
        ticket: Ticket = self.get_related_parent(Tickets, 'tickets_id')
        return ticket

    @property
    def user_participation_type(self) -> str:
        return TICKET_INVOLVED_USER_TYPES[self.type-1]

    @property
    def related_user(self):
        
        # Import occurs here to avoid circular import
        from py_glpi.resources.auth import Users, User
        
        user: User = self.get_related_parent(Users, 'users_id')
        return user


class TicketUsers(Resource[Ticket_User]):
    resource_type = Ticket_User


@dataclass(repr=False)
class Ticket(GLPIItem):
    """ Data model of a GLPI Ticket, has a set of special methods and properties for easier management. """

    name: str
    """ Title of the ticket """
    content: str
    """ Ticket raw HTML/Text content """
    itilcategories_id: int | str
    """ Ticket full categorization hierarchy """
    date_creation: arrow
    closedate: arrow
    solvedate: arrow
    type: Literal[1, 2]
    status: Literal[1, 2, 3, 4, 5, 6]
    urgency: Literal[1, 2, 3, 4, 5]
    impact: Literal[1, 2, 3, 4, 5]
    priority: Literal[1, 2, 3, 4, 5, 6]
    slas_id_tto: int 
    """ SLA Time to Own Ruleset """
    slas_id_ttr: int 
    """ SLA Time to Resolve Ruleset """
    users_id_recipient: int 
    """ User who created the ticket """
    requesttypes_id: int 
    """ Ticket request origin """
    is_deleted: int

    def post_initialization(self):

        self.ticket_users: Resource[Ticket_User] = self.get_subitems_resource(Ticket_User, 'tickets_id')
        self.linked_documents: Resource[Document_Item] = self.get_subitems_resource(Document_Item, 'tickets_id')

        self.content = unescape(self.content)

    @property
    def status_string(self):
        return STATUSES[self.status-1]

    @property
    def urgency_string(self):
        return URGENCIES[self.status-1]

    @property
    def impact_string(self):
        return IMPACTS[self.status-1]

    @property
    def priority_string(self):
        return PRIORITIES[self.status-1]


    def add_applicant(self, user_id: int):
        """ Add an applicant to this ticket. """
        self.ticket_users.create(users_id=user_id, type=1)
        return True

    def add_observer(self, user_id: int):
        """ Add an observer to this ticket. """
        self.ticket_users.create(users_id=user_id, type=2)
        return True

    def add_responsible(self, user_id: int):
        """ Add a responsible to this ticket. """
        self.ticket_users.create(users_id=user_id, type=3)
        return True

    def get_involved_users(self):
        """ Returns the users involved into this ticket. """
        return self.ticket_users.all()

    def link_document(self, document_id: int):
        """ Link an existing document to this ticket. """
        self.linked_documents.create(
            set_parents_itemtype=True, documents_id=document_id, items_id=self.id
        )
        return True

    def attach_document(self, file_path: Path, file_title: str):
        """ Creates a document and links it to this ticket. """
        document_id = Documents(self.connection).create(file_path, file_title)
        self.link_document(document_id)
        return True

    def get_linked_documents(self) -> ItemList[Document]:
        return ItemList(di.related_document for di in self.linked_documents.all())

    @property
    def category(self) -> ITILCategory | None:
        """ ITIL Category related object. """
        return self.get_related_parent(Categories, 'itilcategories_id') if self.itilcategories_id else None

    @property
    def origin(self) -> RequestType | None:
        """ Request Type related object. """
        return self.get_related_parent(Origins, 'requesttypes_id') if self.requesttypes_id else None

    @property
    def tto_sla(self) -> SLA | None:
        """ TTO SLA related object. """
        return self.get_related_parent(TicketSLAs, 'slas_id_tto') if self.slas_id_tto else None

    @property
    def ttr_sla(self) -> SLA | None:
        """ TTR SLA related object. """
        return self.get_related_parent(TicketSLAs, 'slas_id_ttr') if self.slas_id_ttr else None

    def delete(self) -> None:
        return self.update(is_deleted=1)


class Tickets(Resource[Ticket]):
    resource_type = Ticket

    # Overload parameters for easier creation and assertion.
    def create(
        self,
        name: str,
        content: str,
        itilcategories_id: int,
        type: Literal[1, 2] = 1,
        urgency: Literal[1, 2, 3, 4, 5] = 1,
        impact: Literal[1, 2, 3, 4, 5] = 1,
        priority: Literal[1, 2, 3, 4, 5, 6] = 1,
        slas_id_tto: int = 1,
        slas_id_ttr: int = 1,
        requesttypes_id: int = 1,
        return_instance: bool = True,
        set_parents_itemtype: bool = False,
    ):
        return super().create(
            name = name,
            content = content,
            itilcategories_id = itilcategories_id,
            type = type,
            urgency = urgency,
            impact = impact,
            priority = priority,
            slas_id_tto = slas_id_tto,
            slas_id_ttr = slas_id_ttr,
            requesttypes_id = requesttypes_id,
            return_instance = return_instance,
            set_parents_itemtype = set_parents_itemtype,
        )


