import json
import os
from dataclasses import dataclass
from typing import Any
from typing import Protocol

import nbformat
import requests
from nbformat import NotebookNode


@dataclass
class Response:
    """The expected response object used in this module."""

    status_code: int
    body: dict[str, Any] | None = None


class RequestContext(Protocol):
    """Interface for the context in which a request is sent.

    Implementing classes may handle authentication, sessions, etc.
    """

    async def send_request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> Response:
        """Sends the request to the specified url, optionally with headers and data, and returns the response."""
        ...


class BasicRequestContext:
    """Basic, unauthenticated request context."""

    def __init__(self) -> None:
        """Initializes the basic request context."""
        pass

    async def send_request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> Response:
        """Sends the request to the specified url without any headers."""
        response = requests.post(
            url,
            data=data,
        )

        try:
            body = response.json()
            body = dict(body)
        except Exception:
            body = None

        return Response(
            status_code=response.status_code,
            body=body,
        )


class NotebookSyncer:
    """This class syncs a notebook to a CMS (Content Management System).

    The CMS must have an endpoint that satisfies the following constraints:

    -   It must accept a post request with fields *_id*, *displayName* and *markdown*.
    -   The response body must have a key *_id* whose value should be
        a unique string identifier of the content.

    Creating and updating content is handled in the following way:

    -   On the first request, an empty string is sent as *_id*.
    -   If the request succeeds, the value of *_id* (in the response) is stored in a JSON file
        (created in the same directory as the notebook file).
    -   On subsequent requests, the stored value is sent as *_id*.
    """

    ID_KEY = "_id"

    def __init__(self, post_url: str, request_context: RequestContext) -> None:
        """Creates a notebook syncer instance that connects to the CMS through the post url."""
        self._post_url: str = post_url
        self._context: RequestContext = request_context
        self._notebook_path: str = ""

    @property
    def notebook_path(self) -> str:
        """Returns the path of the notebook file."""
        return self._notebook_path

    @notebook_path.setter
    def notebook_path(self, notebook_path: str) -> None:
        """Sets the path of the notebook file."""
        notebook_path = os.path.abspath(notebook_path)
        if not os.path.exists(notebook_path):
            raise FileNotFoundError(
                f"The notebook file '{notebook_path}' does not exist."
            )
        self._notebook_path = notebook_path

    @property
    def basename(self) -> str:
        """The name of the notebook file without extension."""
        basename = os.path.basename(self.notebook_path)
        return os.path.splitext(basename)[0]

    @property
    def data_path(self) -> str:
        """The absolute path of the file to store the data returned from the CMS."""
        return os.path.splitext(self.notebook_path)[0] + ".json"

    @property
    def display_name(self) -> str:
        """Generate a display name for the content."""
        return self.basename.replace("_", " ").title()

    def _save_content_id(self, content_id: str) -> None:
        """Saves the content id to the data file."""
        filename = self.data_path
        with open(filename, "w") as file:
            json.dump({self.ID_KEY: content_id}, file)

    def _get_content_id(self) -> str:
        """Fetches the content id from the data file if it exists, otherwise an empty string."""
        content_id = ""

        filename = self.data_path
        if os.path.exists(filename):
            with open(filename) as file:
                content_id = json.load(file)[self.ID_KEY]
        return content_id

    def _read_notebook(self) -> NotebookNode:
        """Reads the notebook file and returns its content."""
        return nbformat.read(self._notebook_path, as_version=nbformat.NO_CONVERT)  # type: ignore

    def _get_content_from_notebook(self) -> str:
        """Extracts all markdown cells from the notebook and returns it as a merged string."""
        notebook = self._read_notebook()

        markdown_cells = []
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                markdown_cells.append(cell.source)

        markdown_content = "\n\n".join(markdown_cells)

        return markdown_content

    def _request_data(self) -> dict[str, str]:
        """Prepares the request data to be sent to the CMS endpoint."""
        return {
            "_id": self._get_content_id(),
            "displayName": self.display_name,
            "markdown": self._get_content_from_notebook(),
        }

    async def _send_request(self) -> str:
        """Sends the request to the CMS endpoint and returns the content id from the response."""
        response = await self._context.send_request(
            url=self._post_url, data=self._request_data()
        )

        if response.status_code != 200:
            raise ValueError(
                f"Request to the CMS failed with status code {response.status_code}."
            )
        if response.body is None:
            raise ValueError("Response body from CMS could not be parsed.")
        if self.ID_KEY not in response.body:
            raise ValueError(
                f"Response from the CMS does not contain the expected key '{self.ID_KEY}'."
            )
        result = response.body[self.ID_KEY]
        if not isinstance(result, str):
            raise ValueError(
                f"Response from the CMS does not contain a valid content id: {result}"
            )
        content_id: str = result

        return content_id

    async def sync_content(self) -> str:
        """Sends the notebook content to the CMS endpoint and stores the id from the response."""
        content_id = await self._send_request()
        self._save_content_id(content_id)
        return content_id
