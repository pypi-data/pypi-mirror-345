from typing import Union, Dict, Any

from pythonik.models.base import Response
from pythonik.models.search.search_body import SearchBody
from pythonik.models.search.search_response import SearchResponse
from pythonik.specs.base import Spec


SEARCH_PATH = "search/"


class SearchSpec(Spec):
    server = "API/search/"

    def search(
        self,
        search_body: Union[SearchBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs
    ) -> Response:  # Response.data will be SearchResponse
        """
        Search iconik

        Args:
            search_body: Search parameters, either as SearchBody model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with SearchResponse data model
        """
        json_data = self._prepare_model_data(search_body, exclude_defaults=exclude_defaults)
        resp = self._post(
            SEARCH_PATH,
            json=json_data,
            **kwargs
        )
        return self.parse_response(resp, SearchResponse)
