from py_glpi.models import GLPIItem, Resource
from py_glpi.helpers import get_item_url
from dataclasses import dataclass
from arrow import arrow
from mimetypes import guess_type

from pathlib import Path
from json import dumps

class FileUploadError(Exception):
    """ Raised when the file uploading process fails. """


@dataclass(repr=False)
class Document(GLPIItem):

    name: str
    filename: str
    filepath: str
    """ GLPI internal filepath """
    mime: str
    """ Document MimeType """
    is_deleted: bool
    users_id: str | int
    """ User who created the document """
    sha1sum: str
    date_creation: arrow

    def download(self, target_path: Path, **kwargs):

        resp = self.connection.download_document(self.id, **kwargs)
        with open(target_path, 'wb+') as file:
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)

        return target_path


class Documents(Resource[Document]):
    resource_type = Document

    # Override method to access required POST files attribute.

    def create(self, file: Path, file_title: str, return_instance: bool = False):
        """ Uploads a file to GLPI

        -file: The File path we want to upload.
        -file_title: The File Title that will be displayed on GLPI.
        """

        url = get_item_url(self.glpi_connection.api_url, self.resource)

        upload_manifest = {
            'input': {
                'name': file_title,
                '_filename': [file.name]
            }
        }

        file_payload = {
            'filename[0]': (file.name, open(file, 'rb'), guess_type(file)),
            'uploadManifest': (None, dumps(upload_manifest), 'application/json')
        }

        resp = self.glpi_connection.session.post(
            url,
            files=file_payload,
            data=upload_manifest
        )

        content = resp.json()

        if resp.status_code != 201:
            raise FileUploadError(f"Failed to upload {file.name}, server response was {content} with status {resp.status_code}.")

        file_id: int = content.get('id')
        return self.get(file_id) if return_instance else file_id


@dataclass(repr=False)
class Document_Item(GLPIItem):

    items_id: int
    itemtype: str
    documents_id: int

    @property
    def related_document(self) -> Document:
        """ Document related object """
        return self.get_related_parent(Documents, 'documents_id')


class DocumentRelatedItems(Resource[Document_Item]):
    resource_type = Document_Item