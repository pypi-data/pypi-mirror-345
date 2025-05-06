from py_glpi.models import GLPIItem, Resource, ItemList
from dataclasses import dataclass

from py_glpi.resources.tickets import Ticket, Ticket_User, TicketUsers

@dataclass(repr=False)
class UserEmail(GLPIItem):

    users_id: int
    is_dynamic: bool
    is_default: bool
    email: str


@dataclass(repr=False)
class User(GLPIItem):

    name: str
    firstname: str
    realname: str
    is_active: bool
    mobile: str
    auths_id: str
    """ Domain used for Active Directory authentication """
    user_dn: str
    """ User's active directory DN for debugging """

    def post_initialization(self):
        self.emails: Resource[UserEmail] = self.get_subitems_resource(UserEmail, 'users_id')
        self.tickets: TicketUsers = self.get_subitems_resource(Ticket_User, 'users_id')

    def get_observing_tickets(self) -> ItemList[Ticket]:
        """ Returns all the tickets (detailed) where this user is involved as the observer. """
        tickets = self.tickets.all().filter(type=2)
        return ItemList(item.related_ticket for item in tickets)

    def get_requested_tickets(self) -> ItemList[Ticket]:
        """ Returns all the tickets (detailed) where this user is involved as the applicant. """
        tickets = self.tickets.all().filter(type=1)
        return ItemList(item.related_ticket for item in tickets)

    def get_assigned_tickets(self) -> ItemList[Ticket]:
        """ Returns all the tickets (detailed) where this user is involved as the responsible. """
        tickets = self.tickets.all().filter(type=3)
        return ItemList(item.related_ticket for item in tickets)

    def as_dict(self):
        obj = self.__dict__
        obj['emails'] = self.emails.all().to_representation()
        return obj

class Users(Resource[User]):
    resource_type = User


    


