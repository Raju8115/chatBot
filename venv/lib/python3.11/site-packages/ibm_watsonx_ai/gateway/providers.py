#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
import datetime
import json
from typing import Literal

import pandas as pd

from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.wml_client_error import WMLClientError
from ibm_watsonx_ai.wml_resource import WMLResource


class Providers(WMLResource):
    def __init__(self, api_client: APIClient):
        WMLResource.__init__(self, __name__, api_client)

    def create(
        self, provider: str, name: str | None = None, data: dict | None = None
    ) -> dict:

        request_json = {}

        if name:
            request_json["name"] = name

        if data is not None:
            request_json["data"] = data

        response = self._client.httpx_client.post(
            self._client._href_definitions.get_gateway_provider_href(provider),
            headers=self._client._get_headers(),
            json=request_json,
        )

        return self._handle_response(201, "provider creation", response)

    def get_details(self, provider_id: str | None = None) -> dict:
        if provider_id:
            response = self._client.httpx_client.get(
                self._client._href_definitions.get_gateway_provider_href(provider_id),
                headers=self._client._get_headers(),
            )

            return self._handle_response(200, "getting provider details", response)
        else:
            response = self._client.httpx_client.get(
                self._client._href_definitions.get_gateway_providers_href(),
                headers=self._client._get_headers(),
            )

            return self._handle_response(200, "getting providers details", response)

    def get_available_models_details(self, provider_id: str) -> dict:
        response = self._client.httpx_client.get(
            self._client._href_definitions.get_gateway_provider_available_models_href(
                provider_id
            ),
            headers=self._client._get_headers(),
        )

        return self._handle_response(
            200, "getting provider available models details", response
        )

    def list(self) -> pd.DataFrame:
        providers_details = self.get_details()["data"]

        providers_values = [
            (
                m["uuid"],
                m["name"],
                m["type"],
            )
            for m in providers_details
        ]

        table = self._list(providers_values, ["ID", "NAME", "TYPE"], limit=None)

        return table

    def list_available_models(self, provider_id: str) -> pd.DataFrame:
        models_details = self.get_available_models_details(provider_id)["data"]

        models_values = [
            (
                m["uuid"],
                m["id"],
                m.get("alias", ""),
                datetime.datetime.fromtimestamp(m["created"]),
                m["owned_by"],
            )
            for m in models_details
        ]

        table = self._list(
            models_values, ["ID", "MODEL_ID", "ALIAS", "CREATED", "TYPE"], limit=None
        )

        return table

    def delete(self, provider_id: str) -> Literal["SUCCESS"]:
        response = self._client.httpx_client.delete(
            self._client._href_definitions.get_gateway_provider_href(provider_id),
            headers=self._client._get_headers(),
        )

        return self._handle_response(
            204, "provider deletion", response, json_response=False
        )

    def update(
        self, provider_id: str, name: str | None = None, data: dict | None = None
    ) -> dict:
        raise WMLClientError(
            "To be supported soon."
        )  # waiting for PATCH method to be added to rest api
        # provider_details = self.get_details(provider_id)
        # request_json = {"name": provider_details["name"], "data": provider_details["data"]}
        #
        # if name:
        #     request_json["name"] = name
        #
        # if data is not None:
        #     request_json["data"].update(data)
        #
        # print(request_json)
        #
        # response = self._client.httpx_client.put(
        #     self._client._href_definitions.get_gateway_update_provider_href(
        #         provider_id, provider_details["type"]
        #     ),
        #     headers=self._client._get_headers(),
        #     json=request_json,
        # )
        #
        # return self._handle_response(200, "provider update", response)

    @staticmethod
    def get_id(provider_details: dict) -> str:
        return provider_details["uuid"]
