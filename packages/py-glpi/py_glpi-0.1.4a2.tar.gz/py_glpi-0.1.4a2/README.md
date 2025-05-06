# GLPI REST API Python SDK v0.1.2

This Python library provides a wrapper for the GLPI REST API. It offers a collection of resources representing various GLPI items built upon generic classes. Install using:

```
pip install py_glpi
```
--------- or ---------
```
pip install py_glpi==[version]
```

## Supported Items

* **Tickets:**
    * CRUD operations
    * User assignment
    * Document attachment
* **Ticket Categories:**
    * CRUD operations
* **Ticket SLAs:**
    * CRUD operations
* **Request Origin:**
    * CRUD operations
* **Ticket Users:**
    * CRUD operations
* **Users:**
    * CRUD operations
    * Related ticket querying
* **User Emails:**
    * CRUD operations
* **Documents:**
    * CRUD operations
    * Downloading
* **Document Items:**
    * CRUD operations

## How it Works

1. **Connection:** The library establishes a connection to the GLPI server using the specified authentication method (basic or user token).
2. **Item Modeling:** GLPI items are modeled using dataclasses and generic parent classes to provide global and specific functionalities for each item.
3. **Resource Creation:** Resources are created for the modeled GLPI items. These resources handle querying, filtering, updating and creating.

**Item Hierarchy:**

Items can have subitems, which will be represented as subitem resources, or parent items, represented as read-only properties (only updatable from the glpi item update method). Here's an example of this hierarchy:

```
Ticket Categories -> Tickets -> Document Items
```
```python
from py_glpi.resources.tickets import Tickets

ticket = Tickets(connection).get(11)
category = ticket.category                  # Get's the ticket category object throught property getter.
documents = ticket.linked_documents.all()   # Get's all the ticket related Document Items using the Subitem resource.
```
```
User -> Ticket Users <- Tickets
```
```python
from py_glpi.resources.auth import Users

user = Users(connection).get(27)
tickets = user.tickets.all()           # Get's all the user Ticket User items using the Subitem resource.
tickets = user.get_requested_tickets() # Directly get the tickets where this user has the "applicant" role, directly returning the Ticket objects, instead of the relation registries (Ticket Users) 
  
```

This hierarchy attributes may be simplified using certain class methods for easier usage, for example, the ticket item has a method called "attach_document", which directly handles the creation of a related subitem.

Either way, all models are extendable inheriting them with dataclasses:

```python
from py_glpi.resources.auth import Users, User
from dataclasses import dataclass

# Generally, Resources classes are called with a plural of the item they represent e.g User -> Modeled Item, Users -> User Resource.

@dataclass(repr=False)  # Set repr to false to avoid overriding the original method, unless you want to make your own
class User(User):       # The modeled item classes need to match the name of the GLPI itemtype they represent.

    other_attribute: str

    def post_initialization(self):     # Need to be cautious when modifying this method, since it migth lead to unexpected behaviour.
        super().post_initialization()  # Make sure to always call the original class post_initialization first
        my_attr = self.my_method()

    def my_method(self):
        ...

    @property
    def etc(self): ...   # Properties are a great way for adding calculated/extended attributes, i recommend this rather than modifying post_initialization method.

```

## Resource Methods

Every resource has at least the following methods:

* `get(id)`: Retrieves an item with the specified ID.
* `all()`: Retrieves all items.
* `get_multiple(*ids)`: Retrieves multiple items with the provided IDs.
* `search(filters[])`: Filters items using GLPI's search engine.
* `instance(**kwargs)`: Instantiates a GLPI item based on API responses and modeled dataclasses.
* `create(**kwargs)`: Create's a resource with the specified data.

## Item Methods

Every GLPI item has at least the following methods:

* `post_initialization()`: Executes after an item is initialized, allowing for adding new attributes.
* `as_dict()`: Represents the item as a dictionary.
* `get_api_object()`: Provides access to all attributes returned by the GLPI API.
* `get_subitems_resource()`: Creates a resource for a subitem related to this item (e.g., a Ticket with its Document Items).
* `get_related_parent()`: Fetches a parent item using the parent's resource and the related field (e.g., accessing the parent Ticket of a Ticket User item using the `tickets_id` field).
* `update()`: Updates the item.
* `delete()`: Deletes the item.

## Usage

**1. Create a GLPI Connection:**

```python
from py_glpi.connection import GLPISession

connection = GLPISession(
    api_url = getenv("GLPI_REST_API_URL"),
    app_token = getenv("GLPI_APP_TOKEN"),
    auth_type = getenv("GLPI_AUTH_HEADER_METHOD"),
    user = getenv("GLPI_USER"),
    password = getenv("GLPI_PASSWORD"),
    user_token = getenv("GLPI_USER_TOKEN")
)
```

**2. Create a Resource Instance:**

```python
from py_glpi.resources.tickets import Tickets

resource = Tickets(connection)
```

**3. Perform Operations:**

* Retrieve all tickets:

```python
resource.all()
```

* Get a specific ticket:

```python
resource.get(11)
```

* Create a new ticket:
  ##### For attribute reference, visit https://github.com/glpi-project/glpi/blob/main/apirest.md

```python
resource.create(
    name="Test",
    content="Test ticket created with REST Api",
    itilcategories_id=12
)
```


**4. Using the GLPI Search Engine:**

By default, GLPI requires complex filtering criteria. This library simplifies it using the `FilterCriteria` class:

```python
from py_glpi.models import FilterCriteria

filter = FilterCriteria(
    field_uid="Ticket.name",  # Searchable field UUID
    operator="Equals",        # Comparison operator
    value="Test"              # Matching value
)

resource.search(filter)

# Specifying a non-existent field_uid will raise an exception that includes a reference of all the searchable field_uids for the sepcified Resource.
```

Filters can be related using logical operators (AND, OR, XOR) defined as follows:

```python
filter1 = filter
filter2 = FilterCriteria(
    field_uid="Ticket.content",
    operator="Contains",
    value="API"
)

filter = filter1 & filter2  # AND operation
filter = filter1 | filter2  # OR operation
filter = filter1 & filter2 | filter3 # Mixed operation

result = resource.search(filter)  # Logical operations between filter criteria will produce a list related by thus operation.
```

**5. ItemList Methods:**

Methods that return multiple items (all, search, get_multiple) use an extended list class named `ItemList`. This class provides the following methods:

* `filter(**kwargs)`: Offline Filters the results using the `leopards` library (refer to https://github.com/mkalioby/leopards for usage).
* `exclude(**kwargs)`: Reverse Offline Filters the results using the `leopards`.
* `to_representation()`: Returns a list with the result of executing to_dict() method of each contained item.

```python
result = resource.filter(priority__gt=2)  # Offline filters the search result, returns only the tickets with a priority higher than 2.
result = result.exclude(urgency__lt=4)  # Returns only the tickets with a urgency higher than 3.
```

For more usage examples, refer to tests in the github repository.

