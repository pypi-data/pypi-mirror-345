from py_glpi.helpers import get_item_url, parse_kwargs
from typing import TypeAlias, Literal
from requests import Session, Response

GlpiType: TypeAlias = str
ResourceId: TypeAlias = int
Url: TypeAlias = str

class AuthError(Exception):
    """ Raised if there's an error in the GLPI Session authentication process. """
        
class ItemDoesNotExists(Exception):
    """ Raised if the requested GLPI item does not exists. (ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM) """
        
class Unauthorized(Exception):
    """ Raised if a request produces a 401 error. """
        
class _Session(Session):
    """ Modified HTTP Session class to raise exception on forbidden response status code. """
    
    def __init__(self, **request_kwargs):
        super().__init__()
        self.request_kwargs = request_kwargs
    
    def request(self, *args, **kwargs):
        kwargs |= self.request_kwargs
        response = super().request(*args, **kwargs)
        if response.status_code == 403:
            raise Unauthorized
        return response

class URLs:

    """ Specific GLPI API URL Suffixes. """

    LOGIN: Url = 'initSession'
    RESOURCE_SEARCH: Url = 'search'
    SEARCH_OPTIONS: Url = 'listSearchOptions'
    GET_MULTIPLE_ITEMS: Url = 'getMultipleItems'
    DOCUMENTS: Url = 'Document'

class GLPISession:
    
    """ A Class that wraps a GLPI connection with all it's API endpoints, instanciating this class will create an authenticated GLPI HTTP Session using the specified authentication type."""
    
    def __init__(
        self, 
        api_url: Url = None,
        app_token: str = None, 
        auth_type: Literal["basic", "user_auth"] = "basic", 
        user: str = None, 
        password: str = None, 
        user_token: str = None,
        verify_ssl: bool = True,
        **session_request_kwargs
    ):
        
        # First session is produced to make the necessary login.
        self.session = _Session(**(session_request_kwargs | {"verify": verify_ssl}))

        assert api_url, "API URL is required for GLPI Session."
        self.api_url: Url = api_url

        assert app_token, "App token is required for GLPI Session."

        assert auth_type in ["basic", "user_token"], f"Invalid auth type {auth_type}."

        if auth_type == "basic":
            assert user and password, "A user and a password are required when using basic authentication."

        elif auth_type == "user_token":
            assert user_token, "A user token is required when using user_token authentication."

        self.auth_type = auth_type
        self.user = user
        self.__pasword = password
        self.__app_token = app_token
        self.user_token = user_token
        
        # Then, request headers are built using the necessary obtained tokens.
        self.session.headers = self.__get_request_headers()
        
    def __get_authorization(self):
        
        auth_type = self.auth_type
        if auth_type == 'user_token':
            return f"user_token {self.user_token}"
        elif auth_type == 'basic':
            from base64 import b64encode
            b64_bytes = b64encode(bytes(f"{self.user}:{self.__pasword}", encoding='utf8'))
            return f"basic {b64_bytes.decode('ascii')}"
        
    def __get_session_token(self):
        
        url = get_item_url(self.api_url, URLs.LOGIN)
        authorization_string = self.__get_authorization()
        rq = self.session.get(
            url, 
            headers = {
                'Content-Type': 'application/json',
                'App-Token': self.__app_token,
                'Authorization': authorization_string,
            }
        )
            
        if rq.status_code == 401:
            raise AuthError(f"Provided credentials are invalid. {rq.json()}")

        elif rq.status_code == 400:
            raise AuthError(f"Failed to obtain session token for GLPI Session, server response was {rq.json()} with status {rq.status_code}.")
        
        token = rq.json().get('session_token')
            
        return token
        
    def __get_request_headers(self):
        session_token = self.__get_session_token()
        return {
            "Accept": "application/json",
            "App-Token": self.__app_token,
            "Session-Token": session_token
        }
        
    def request(func):
        """ Decorator used for parsing endpoint responses. """
        
        def inner(self, *args, **kwargs) -> Response:
            try:
                call = func(self, *args, **kwargs)
                if call.status_code == 400 and call.json()[0] == 'ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM':
                    raise ItemDoesNotExists(
                        f'Requested item type on {func.__name__} call with ({args}, {kwargs}) to {call.url} does not exists.'
                    )
                return call
            except Unauthorized:
                self.session.headers = self.__get_request_headers()
                return func(self, *args, **kwargs)
            
        return inner
    
    @request
    def get_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        url = get_item_url(self.api_url, item_type) + f'/{id}'
        kwargs = parse_kwargs(kwargs)
        rq = self.session.get(url, params=kwargs)
        return rq

    @request
    def get_multiple_items(self, *item_keys: dict, **kwargs):
        """ Fetch multiple items using a key composition of {"itemtype":..., "items_id":...}. """
        url = get_item_url(self.api_url, URLs.GET_MULTIPLE_ITEMS) + '?'
        url += "&".join([f"items[{i}][itemtype]={item['itemtype']}&items[{i}][items_id]={item['items_id']}" for i, item in enumerate(item_keys)])
        kwargs = parse_kwargs(kwargs)
        rq = self.session.get(url, params=kwargs)
        return rq
    
    @request
    def get_all_items(self, item_type: GlpiType, **kwargs):
        url = get_item_url(self.api_url, item_type)
        kwargs = parse_kwargs(kwargs)
        rq = self.session.get(url, params=kwargs)
        return rq
    
    @request
    def create_item(self, item_type: GlpiType, **kwargs):
        url = get_item_url(self.api_url, item_type)
        body = {"input": kwargs}
        rq = self.session.post(url, json=body)
        return rq

    @request
    def update_item(self, item_type: GlpiType, id: ResourceId, **kwargs):
        url = get_item_url(self.api_url, item_type) + f'/{id}'
        body = {"input": kwargs}
        rq = self.session.put(url, json=body)
        return rq

    @request
    def delete_item(self, item_type: GlpiType, id: ResourceId):
        url = get_item_url(self.api_url, item_type) + f'/{id}'
        rq = self.session.delete(url)
        return rq
    
    @request
    def create_items(self, item_type: GlpiType, *args: dict):
        url = get_item_url(self.api_url, item_type)
        body = {"input": list(args)}
        rq = self.session.post(url, data=body)
        return rq
    
    @request
    def get_item_search_options(self, item_type: GlpiType):
        url = get_item_url(self.api_url, URLs.SEARCH_OPTIONS) + f'/{item_type}'
        return self.session.get(url)
    
    @request
    def search_items(self, item_type: GlpiType, criteria, **kwargs):

        search_opts: dict = self.get_item_search_options(item_type).json()
        criterias: list[dict] = [ev.as_dict() for ev in criteria._evaluation]

        # Find the specified field's id from it's name.
        for eval in criterias:
            id = [k for k, v in search_opts.items() if isinstance(v, dict) and v.get('uid', '').lower() == eval['field']]
            if not len(id):
                valid_opts = {v.get('uid'): v.get('name') for k, v in search_opts.items() if k != 'common' and isinstance(v, dict)}
                raise ValueError(f"Couldn't find a valid filtering field with uid '{eval['field']}' for itemtype '{item_type}'. Valid filtering field reference shown below:\n\n{valid_opts}")
            eval['field'] = id[0]

        url = get_item_url(self.api_url, URLs.RESOURCE_SEARCH) + item_type + '/?'
        criteria_kwargs = [[f"criteria[{i}][{k}]={v}" for k, v in criteria.items()] for i, criteria in enumerate(criterias)]
        if len(criteria_kwargs) > 0:
            kwargs = parse_kwargs(kwargs)
            url += "&".join(criteria_kwargs[0] + [f"{k}={v}" for k, v in kwargs.items()])

        url += "&forcedisplay[0]=2"
        
        return self.session.get(url)

    @request
    def download_document(self, document_id: int, **kwargs):
        url = get_item_url(self.api_url, URLs.DOCUMENTS) + f'/{document_id}?alt=media'
        return self.session.get(url, params=kwargs)
            
            
        
            
        

    
    
        