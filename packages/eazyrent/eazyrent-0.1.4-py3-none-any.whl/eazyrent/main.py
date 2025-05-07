import importlib
import inspect
import json
import os
import pkgutil
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import jwt
import urllib3
from pydantic import BaseModel, Field

import eazyrent

server = os.environ.get("server", "https://api.v2.eazyrent.fr")

http = urllib3.PoolManager()


class JsonAuthAccess(BaseModel):
    type: str
    key_id: str = Field(alias="keyId")
    key: str = Field()
    expiration_date: datetime = Field(alias="expirationDate")
    user_id: str = Field(alias="userId")


class EazyrentSDK:
    def __init__(self, api_key: str | None = None, bearer: str | None = None):
        self._api_key = api_key
        self._access_token = bearer
        self.auth_server = "https://auth.eazyrent.fr"
        self.token_url = f"{self.auth_server}/oauth/v2/token"
        if not self._api_key and not self._access_token:
            self._authenticate()
        self.apis = self._load_all_apis()

    def _get_client(self, module):
        configuration = getattr(module, "Configuration").get_default()
        configuration.host = f"{server}{configuration.host}"
        if self._access_token:
            configuration.access_token = self._access_token
        elif self._api_key:
            configuration.api_key["Authorization"] = self._api_key
            configuration.api_key_prefix["Authorization"] = "Token"
        return getattr(module, "ApiClient")(configuration=configuration)

    def _generate_jwt_access(self, auth) -> str:
        """Generate JWT for Zitadel JWT Bearer Grant type."""
        payload = {
            "iss": auth.user_id,
            "sub": auth.user_id,
            "aud": self.auth_server,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=300),
            "iat": datetime.now(timezone.utc),
        }
        headers = {"alg": "RS256", "kid": auth.key_id}
        return jwt.encode(payload, auth.key, algorithm="RS256", headers=headers)

    def _jwt_bearer_token(self, json_key: JsonAuthAccess) -> str:
        """POST token"""
        scopes = [
            "urn:zitadel:iam:org:projects:roles",
            "urn:zitadel:iam:user:resourceowner",
            "urn:zitadel:iam:org:project:id:310976816384838665:aud",
        ]
        data = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "scope": " ".join(scopes),
                "assertion": self._generate_jwt_access(json_key),
            }
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = http.request(
            "POST",
            self.token_url,
            body=data,
            headers=headers,
        )
        if response.status != 200:
            raise RuntimeError(
                f"JWT Bearer auth failed: {response.status} - {response.data.decode()}"
            )
        return json.loads(response.data.decode("utf-8"))["access_token"]

    def _client_credentials(self, key: str, secret: str) -> str:
        """Get access token using client credentials."""
        data = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": key,
                "client_secret": secret,
                "scope": "openid profile urn:zitadel:iam:org:project:id:zitadel:aud",
            }
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = http.request(
            "POST",
            self.token_url,
            body=data,
            headers=headers,
        )

        if response.status != 200:
            raise RuntimeError(
                f"Client credentials auth failed: {response.status} - {response.data.decode()}"
            )

        return json.loads(response.data.decode("utf-8"))["access_token"]

    def _load_json_credentials(self):
        if json_key := os.environ.get("EAZ_KEY"):
            key = json.loads(json_key)
            return JsonAuthAccess.model_validate(key)
        try:
            with open(Path().home() / ".eazyrent" / "credentials.json") as f:
                key = json.load(f)
                return JsonAuthAccess.model_validate(key)
        except FileNotFoundError:
            return

    def _load_client_credentials(self):
        key = os.environ.get("EAZ_ACCESS_KEY_ID")
        secret = os.environ.get("EAZ_SECRET_ACCESS_KEY")
        if key and secret:
            return key, secret
        try:
            with open(Path().home() / ".eazyrent" / "credentials.json") as f:
                credentials = json.load(f)
                key, secret = (
                    credentials["access_key_id"],
                    credentials["secret_access_key"],
                )
                return key, secret
        except FileNotFoundError:
            return

    def _authenticate(self):
        if api_key := os.environ.get("EAZ_API_KEY"):
            print("Credentials found. API key is available in the current environment.")
            self._api_key = api_key
            return
        if json_key := self._load_json_credentials():
            print(f"Credentials found. Using JSON key : {json_key.key_id}")
            self._access_token = self._jwt_bearer_token(json_key)
            return
        if credentials := self._load_client_credentials():
            print(f"Credentials found. Using key : {credentials[0]}")
            self._access_token = self._client_credentials(*credentials)
            return
        print("No credentials found.")

    def _load_all_apis(self):
        apis_root = type("Apis", (), {})()
        for finder, namespace, ispkg in pkgutil.iter_modules(
            eazyrent.__path__, prefix="eazyrent."
        ):
            if not ispkg:
                continue
            ns_module = importlib.import_module(namespace)
            ns_obj = type(namespace.title(), (), {})()

            for _, version, is_ver_pkg in pkgutil.iter_modules(
                ns_module.__path__, prefix=f"{namespace}."
            ):
                if not is_ver_pkg:
                    continue

                mod = importlib.import_module(version)
                ver_obj = type(version.title(), (), {})()

                if hasattr(mod, "ApiClient"):
                    client = self._get_client(mod)

                    for name, cls in inspect.getmembers(mod, inspect.isclass):
                        if name.endswith("Api") and cls.__module__.startswith(
                            mod.__name__
                        ):
                            attr_name = self._to_snake_case(name.removesuffix("Api"))
                            setattr(ver_obj, attr_name, cls(client))

                    setattr(ns_obj, version.split(".")[-1], ver_obj)

            setattr(apis_root, namespace.split(".")[-1], ns_obj)

        return apis_root

    def _to_snake_case(self, name):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
