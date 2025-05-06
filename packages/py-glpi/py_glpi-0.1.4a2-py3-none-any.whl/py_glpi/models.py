from py_glpi.connection import GLPISession, ResourceId
from dataclasses import dataclass, field
from warnings import warn

from typing import Literal, TypeVar, Generic, Type, Iterator
from typing_extensions import Self

from arrow import get
from leopards import Q

class ResourceNotFound(Exception):
    """ Raised when a resource get method couldn't find the matching item for the given id. """

class MultipleGetResult(Exception):
    """ Raised when a get operation returns more than one result (a list instance). """

class ItemCreationError(Exception):
    """ Raised if a item creation request fails. """

EXPAND_DROPDOWNS_WARNING = "Usage of expand_dropdowns migth produce unexpected behaviour for the Resource associated model.", RuntimeWarning
""" Message and type for the warning generated when expand dropdowns is used. """


@dataclass(repr=False, kw_only=True)
class GLPIItem:
    """ Basic base class for a GLPI Item, all the defined items that inherit this class should be dataclasses. This class ships the id attribute by default.
    
    IMPORTANT: The defined class name needs to match the GLPI itemtype name.
    """

    id: int
    """ Predefined id attribute, this should always exists in any GLPI Item representation. """
    
    __init_kwargs__: dict = field(default=None, init=False)
    """ All kwargs used as argument on the instanciation method. """

    connection: GLPISession = field(default=None, init=False)
    """ GLPI Connection used for generating this Item. """

    def __dates_to_arrow__(self):
        """ Attempts to transform every date attribute to arrow type. """
        for attr in self.__dict__:
            date = self.__getattribute__(attr)
            self.__setattr__(attr, get(date)) if 'date' in attr and date else None

    def post_initialization(self):
        """ This method will be executed after the GLPI Item is initialized, can be used to transform data types and format the response data, or registering new attributes. """
        ...

    def __post_init__(self):
        """ Dataclass shipped method for post initalization, shouldn't be modified. """
        assert hasattr(self, 'id'), "Every GLPI Item requires to have an ID attribute."
        self.__dates_to_arrow__()
        self.post_initialization()

    def __repr__(self) -> str:
        return f"<GLPI {self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('__') and k not in ('connection', 'resource'))})>"
    
    def as_dict(self):
        """ Used for returning a formatted dict representation of the GLPI item instance. """
        return self.__dict__

    def get_api_object(self):
        """ Returns the GLPI API item used to initialize this class """
        return self.__init_kwargs__

@dataclass(repr=False)
class FilterCriteria:
    
    field_uid: str
    operation: Literal['contains', 'equals', 'notequals', 'lessthan', 'morethan', 'under', 'notunder']
    value: str | int
    
    def __post_init__(self):
        self.link = None
        self.field_uid = self.field_uid.lower()
        self._field_uid = self.field_uid
        self.operation = self.operation.upper()
        self._evaluation: list[Self] = [self]

    def set_link(self, link: Literal['OR', 'AND', 'XOR']) -> None:
        self.link = link
    
    def __and__(self, other: Self) -> Self:
        other.set_link('AND')
        self._evaluation.append(other)
        return self
    
    def __or__(self, other: Self) -> Self:
        other.set_link('OR')
        self._evaluation.append(other)
        return self

    def __xor__(self, other: Self) -> Self:
        other.set_link('XOR')
        self._evaluation.append(other)
        return self
    
    def as_dict(self):
        obj = {
            'field': self.field_uid,
            'searchtype': self.operation,
            'value': self.value
        }
        obj |= {
            'link': self.link 
        } if self.link else {}
        return obj

    def __repr__(self):
        if len(self._evaluation) == 1:
            return f"<GLPI Filter({self._field_uid} {self.operation} {self.value})>"
        else:
            return "".join([f"{obj.link if obj.link else ''}<GLPI Filter({obj._field_uid} {obj.operation} {obj.value})>" for obj in self._evaluation])


GT = TypeVar('GT')
""" GLPI Type Generic Mashup """

class ItemList(list, Generic[GT]):
    """ List with extended methods. """

    def __getitem__(self, idx: int | slice) -> GT:
        return super().__getitem__(idx)

    def __iter__(self) -> Iterator[GT]:
        return super().__iter__()
    
    def to_representation(self):
        """ Invokes the as_dict method for each GLPI Item. """
        items: ItemList[dict] = ItemList(item.as_dict() for item in self)
        return items

    def filter(self, **kwargs):
        """ Offline filtering for an item list using leopards Q.
        Refence at https://github.com/mkalioby/leopards"""
        items: ItemList[GT] = ItemList(Q(self, **kwargs))
        return items

    def exclude(self, **kwargs):
        """ Reverse Offline filtering (usage of NOT) """
        items: ItemList[GT] = ItemList(Q(self, NOT=kwargs))
        return items

    
class Resource(Generic[GT]):
    
    """ Base class for all GLPI query-able resources, every resource should have a all, search, create, save, update and delete method. """
    
    resource_type: Type[GT] = None
    """ A valid GLPI item type (Ticket, Monitor...) """

    expand_dropdowns: bool = False
    """ Expand relations on get requests (search, get, get_multiple and all), this migth cause unexpected behaviour on the resource's associated model. """
    
    def __init__(
        self, 
        glpi_connection: GLPISession,
        subitem_of: str = None,
        parent_id: int = None,
        related_field: str = None
    ):

        """ Can be instanciated as subitem resource linked to the itemtype specified in subitem_of param."""
        self.is_subitem = bool(subitem_of)
        self.subitem_of = subitem_of
        self.related_field = related_field
        self.parent_id = parent_id

        if self.expand_dropdowns:
            warn(*EXPAND_DROPDOWNS_WARNING)

        assert self.resource_type, "Every resource must specify a resource type."

        if subitem_of:
            assert parent_id, "Parent ID needs to be specified if this resource is a subitem instance."
            assert related_field, "Related field needs to be specified if this resource is a subitem instance."

        self.resource = self.resource_type.__name__
        self.resource = self.resource if not self.is_subitem else self.subitem_of + f'/{parent_id}/{self.resource}'

        self.glpi_connection = glpi_connection
        
    def instance(self, **kwargs) -> GT:
        """ Used method for instanciating the resource type to avoid attribute errors. """
        parsed_kws = {k: v for k, v in kwargs.items() if k in self.resource_type.__annotations__}
        # Ensure id is always present in instanciation
        parsed_kws.update({'id': kwargs.get('id')})

        resource_ins = self.resource_type
        resource_ins.__init_kwargs__ = kwargs
        resource_ins.connection = self.glpi_connection
        resource_ins.resource = self

        try:
            instance = resource_ins(**parsed_kws)
        except TypeError as err:
            raise TypeError(f"Unable to instance {self.resource_type.__name__} using {kwargs.keys()} -> {err}")
        return instance

    def all(self, range_from: int = 0, range_to: int = 999_999_999, **kwargs) -> ItemList[GT]:
        """ Returns all the items available from this resource, a None response means the server responded with HTTP 204. """

        resp = self.glpi_connection.get_all_items(
            self.resource, 
            expand_dropdowns=self.expand_dropdowns,
            range=f"{range_from}-{range_to}",   # Response length range, defaults to infinite
            **kwargs
        )
        
        # In case server returns no content
        if resp.status_code == 204:
            return None

        content = resp.json()

        return ItemList(map(lambda obj: self.instance(**obj), content))
        
    def search(self, criteria: FilterCriteria = None, range_from: int = 0, range_to: int = 999_999_999, **kwargs):
        """ Use the GLPI search engine to find specific instances. """

        resp = self.glpi_connection.search_items(
            self.resource, 
            criteria, 
            range=f"{range_from}-{range_to}",   # Response length range, defaults to infinite
            expand_dropdowns=self.expand_dropdowns,
            **kwargs
        )
        content: dict = resp.json()
        results_ids = [result['2'] for result in content.get('data', [])]
        if not len(results_ids):
            raise ResourceNotFound(f"Couldn't find {self.resource_type.__name__} using {criteria} criteria.") 

        return self.get_multiple(*results_ids, **kwargs)
    
    def get(self, id: ResourceId, get_hateoas=False, **kwargs):
        
        assert id, f"Requested resource id ({id}) is invalid."

        resp = self.glpi_connection.get_item(
            self.resource, 
            id, 
            expand_dropdowns=self.expand_dropdowns, 
            get_hateoas=get_hateoas,
            **kwargs
        )
        if resp.status_code == 404:
            raise ResourceNotFound(f"Couldn't find a {self.resource_type.__name__} with id {id}")

        if isinstance(resp.json(), list):
            raise MultipleGetResult(f"Expected one result for GET operation, got a list result when querying {resp.url} instead.")

        return self.instance(**resp.json())
    
    def get_multiple(self, *ids: int, **kwargs) -> ItemList[GT]:
        """ Fetch multiple items using their IDs. """

        resp = self.glpi_connection.get_multiple_items(
            *[{"itemtype": self.resource_type.__name__, "items_id": id} for id in ids],
            expand_dropdowns=self.expand_dropdowns,
            **kwargs
        )
        content = resp.json()
        return ItemList(map(lambda obj: self.instance(**obj), content))

        
    def create(self, return_instance: bool = True, set_parents_itemtype: bool = False, **kwargs):
        """ If return instance is true, a GET request will be done to get all the details of the created object, else, only the object's id will be returned. 
        
        If set_parents_itemtype is True, when a instance of this resource is created as a subitem, the parent's itemtype will be injected as an argument -> {"itemtype": [parents_itemtype]}.
        """

        if self.is_subitem:
            # Inject relation into creation kwargs
            kwargs.update({self.related_field: self.parent_id})

            # Injects the parent's itemtype as a kwarg if needed
            if set_parents_itemtype:
                kwargs.update({'itemtype': self.resource.split('/')[0]})

        resp = self.glpi_connection.create_item(self.resource, **kwargs)
        if not resp.status_code == 201:
            raise ItemCreationError(f"Failed to create {self.resource} with {kwargs}, server returned {resp.json()} with status {resp.status_code}.")
        
        id: int = resp.json().get('id')
        return self.get(id) if return_instance else id
        
    def create_multiple(self, *args: dict):
        raise NotImplementedError("Create multiple is currently not supported.")

    def __repr__(self) -> str:
        return f"<GLPI Resource({self.resource})>"


# Inherited for adding subitem method and other resource related stuff
@dataclass(repr=False, kw_only=True)
class GLPIItem(GLPIItem):

    resource: Resource = field(default=None, init=False)
    """ The resource used for generating this item. """

    def get_subitems_resource(self, subitem_type: GLPIItem, subitem_related_field: str) -> Resource[GT]:
        """ Fabric a subitem resource class for the requested subitem_type. """

        class SubitemResource(Resource):
            """ Same as a normal resource, but type-specific to avoid attribute overwriting. """
            resource_type = subitem_type

        resource: SubitemResource[GT] = SubitemResource(self.connection, self.__class__.__name__, self.id, subitem_related_field)
        return resource

    def get_related_parent(self, parent_resource: Resource, id_field: str):
        """ Query the related parent using the parent's resource class and the related id_field to this parent. """
        assert isinstance(getattr(self, id_field), int), f"Can't make a reverse lookup of the related {parent_resource.__name__} resource if the parent attribute id is expressed as a string, try disabling expand_dropdowns."
        resource: Resource = parent_resource(self.connection)
        return resource.get(getattr(self, id_field))

    def update(self, **kwargs) -> Self:
        """ Update this instance with the specified kwargs, returns the updated GLPI Item. """
        self.connection.update_item(self.__class__.__name__, self.id, **kwargs)
        return self.resource.get(self.id)

    def delete(self) -> None:
        """ Logically Deletes the GLPI item. """
        self.connection.delete_item(self.__class__.__name__, self.id)


        
