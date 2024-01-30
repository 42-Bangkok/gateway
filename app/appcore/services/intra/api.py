import httpx
from appcore.services.env_manager import ENVS
from django.core.cache import cache
from pydantic import validate_call


class Intra:
    """
    Wraps the 42 Intra API.
    """

    BASE = "https://api.intra.42.fr/v2"

    def __init__(self):
        ...

    @property
    def access_token(self) -> str:
        """
        Retrieves the access token for the Intra API. If the token is cached, it will be returned.

        Returns:
            str: The access token.

        Raises:
            Exception: If the token cannot be fetched.
        """
        token = cache.get("intraapi:access-token")
        if token is not None:
            return token

        data = {"grant_type": "client_credentials"}
        auth = (ENVS["FORTY_TWO_CLIENT_ID"], ENVS["FORTY_TWO_CLIENT_SECRET"])
        url = f"{self.BASE}/oauth/token"
        with httpx.Client() as client:
            r = client.post(
                url,
                data=data,
                auth=auth,
            )
            r.raise_for_status()

        access_token = r.json()["access_token"]
        ttl = r.json()["expires_in"] - 60
        cache.set(
            "intraapi:access-token",
            access_token,
            ttl,
        )

        return r.json()["access_token"]

    @validate_call
    def user(self, login: str) -> dict:
        """
        Retrieves user information from the API.

        Args:
            login (str): The login of the user.

        Returns:
            dict: A dictionary containing the user information.
        """
        url = f"{self.BASE}/users/{login}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers)
            r.raise_for_status()

        return r.json()

    @validate_call
    def users(self, filter_params: dict, per_page: int = 100) -> list[dict]:
        """
        Filter users from the API.
        Args:
            filter_params: The filter to apply. Example:
            {
                'filter[primary_campus_id]': 33,
                'filter[pool_month]': 'january',
                'filter[pool_year]': 2022,
            }
            :param per_page: The number of users to fetch per page. Default is 100.
        Returns:
            list[dict]: A list of users.

        Raises:
            Exception: If the users cannot be fetched.
        """
        page = 1
        count = 1
        ret = []
        filter_params.update(
            {
                "per_page": per_page,
                "page": page,
            }
        )
        url = f"{self.BASE}/users"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers, params=filter_params)
            r.raise_for_status()
            ret += r.json()

            while count > 0:
                count = len(r.json())
                page += 1
                filter_params.update({"page": page})
                r = client.get(url, headers=headers, params=filter_params)
                r.raise_for_status()
                ret += r.json()

        return ret

    @validate_call
    def cursus_users(
        self,
        cursus_id: int,
        filter_params: dict,
        per_page: int = 100,
    ) -> list:
        page = 1
        count = 1
        ret = []
        filter_params.update(
            {
                "per_page": per_page,
                "page": page,
            }
        )
        url = f"{self.BASE}/cursus/{cursus_id}/users/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers, params=filter_params)
            r.raise_for_status()
            ret += r.json()

            while count > 0:
                count = len(r.json())
                page += 1
                filter_params.update({"page": page})
                r = client.get(url, headers=headers, params=filter_params)
                r.raise_for_status()
                ret += r.json()

        return ret

    @validate_call
    def pools(self, pool_id: int = 73) -> dict:
        """
        The pool of evaluation points.
        [doc](https://api.intra.42.fr/apidoc/2.0/pools/show.html)

        Args:
            pool_id: The id of the pool
        Returns:
            {
            "id": 25,
            "current_points": 0,
            "max_points": 400,
            "cursus_id": 1,
            "campus_id": 12
            }
        Raises:
            Exception: If the pool cannot be fetched.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE}/pools/{pool_id}"
        with httpx.Client() as client:
            r = client.get(url, headers=headers)
            r.raise_for_status()

        return r.json()

    @validate_call
    def pool_add_pts(self, value: int, pool_id: int = 73) -> dict:
        """
        Add point to pool apparently you can add negative point
        [doc](https://api.intra.42.fr/apidoc/2.0/pools/show.html)


        Args:
            value: The number of points to add
            pool_id: The id of the pool
        Returns:
            {
            "id": 25,
            "current_points": 0,
            "max_points": 400,
            "cursus_id": 1,
            "campus_id": 12
            }
        Raises:
            Exception: If failed to add points to pool.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE}/pools/{pool_id}/points/add"
        data = {"points": value}
        with httpx.Client() as client:
            r = client.post(url, headers=headers, data=data)
            r.raise_for_status()

        return r.json()
