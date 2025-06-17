#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
import datetime
from typing import Literal

import pandas as pd

from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.wml_resource import WMLResource


class Models(WMLResource):
    def __init__(self, api_client: APIClient):
        WMLResource.__init__(self, __name__, api_client)

    def create(
        self,
        provider_id: str,
        model: str,
        alias: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        request_json = {"id": model}

        if alias:
            request_json["alias"] = alias

        if metadata is not None:
            request_json["metadata"] = metadata

        response = self._client.httpx_client.post(
            self._client._href_definitions.get_gateway_models_href(provider_id),
            headers=self._client._get_headers(),
            json=request_json,
        )

        return self._handle_response(201, "model creation", response)

    def get_details(
        self, *, model_id: str | None = None, provider_id: str | None = None
    ) -> dict:
        if model_id:
            response = self._client.httpx_client.get(
                self._client._href_definitions.get_gateway_model_href(model_id),
                headers=self._client._get_headers(),
            )

            return self._handle_response(200, "getting model details", response)
        elif provider_id:
            response = self._client.httpx_client.get(
                self._client._href_definitions.get_gateway_models_href(provider_id),
                headers=self._client._get_headers(),
            )

            return self._handle_response(200, "getting models details", response)
        else:
            response = self._client.httpx_client.get(
                self._client._href_definitions.get_gateway_all_tenant_models_href(),
                headers=self._client._get_headers(),
            )

            return self._handle_response(
                200, "getting all tenant models details", response
            )

    def list(self, provider_id: str | None = None) -> pd.DataFrame:
        models_details = self.get_details(provider_id=provider_id)["data"]

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

    def delete(self, model_id: str) -> Literal["SUCCESS"]:
        response = self._client.httpx_client.delete(
            self._client._href_definitions.get_gateway_model_href(model_id),
            headers=self._client._get_headers(),
        )

        return self._handle_response(
            204, "model deletion", response, json_response=False
        )

    def get_id(self, model_details):
        return model_details["uuid"]
