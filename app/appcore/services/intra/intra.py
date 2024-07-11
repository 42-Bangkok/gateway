import threading
from time import sleep
from urllib.parse import urlencode
import httpx
from appcore.services.env_manager import ENVS
from django.core.cache import cache
from pydantic import validate_call
from appcore.services.console import console
from rich.progress import track


class Intra:
    """
    Wraps the 42 Intra API.
    """

    BASE = "https://api.intra.42.fr/v2"

    def __init__(self):
        """
        Initializes the Intra API.
        defaults timeout to 30 because, well, you know :*(
        """
        self.timeout = 30

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
        with httpx.Client(timeout=self.timeout) as client:
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
        with httpx.Client(timeout=self.timeout) as client:
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
        with httpx.Client(timeout=self.timeout) as client:
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
        with httpx.Client(timeout=self.timeout) as client:
            r = client.get(
                url, headers=headers, params=filter_params, timeout=self.timeout
            )
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
        with httpx.Client(timeout=self.timeout) as client:
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
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(url, headers=headers, data=data, timeout=self.timeout)
            r.raise_for_status()

        return r.json()

    def get_users_by_cursus_id(self, cursus_id: int, filter: dict) -> list:
        """
        {{BASE_API}}/cursus/:cursus_id/users?filter[primary_campus_id]=33&filter[pool_month]=january&filter[pool_year]=2022&[page[size]=100
        https://api.intra.42.fr/apidoc/2.0/users/index.html
        C-Piscine's cursus_id is 9
        ex.
        filter = {
            'filter[primary_campus_id]': 33,
            'filter[pool_month]': 'january',
            'filter[pool_year]': 2022,
        }
        """
        ENDPOINT = "cursus"
        params = urlencode(filter)

        def _get_users_at_page(pagenum):
            url = f"{self.BASE}/{ENDPOINT}/{cursus_id}/users/?{params}&page[number]={pagenum}&page[size]=50"
            console.log(f"Getting {url}")
            headers = {"Authorization": f"Bearer {self.access_token}"}
            r = httpx.get(url, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json()

        l_users = []
        pagenum = 1
        while r := _get_users_at_page(pagenum):
            l_users += r
            pagenum += 1

        return l_users

    def get_user_info(self, id) -> dict:
        """
        Get user info by id
        """
        ENDPOINT = "users"

        with httpx.Client(timeout=self.timeout) as client:
            url = f"{self.BASE}/{ENDPOINT}/{id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            r = client.get(url, headers=headers, timeout=self.timeout)
            tries = 10
            while r.status_code != 200 and tries > 0:
                console.log(f"Getting user {id=} Failed! Retrying {tries=}")
                r = client.get(url, headers=headers)
                tries -= 1
                sleep(1)
            if r.status_code != 200:
                raise Exception(f"Failed to get user {id=}")

        return r.json()

    def get_user_infos_thr(self, l_ids, delay=0.5, token=None) -> list:
        """
        Get user info by ids using threading to speed up
        delay more than 0.5 will risk cause 429
        """
        user_infos = []
        thrs = []

        def thr_get_user_info(id):
            user_infos.append(self.get_user_info(id))

        for id in l_ids:
            thr = threading.Thread(target=thr_get_user_info, args=(id,))
            thrs.append(thr)

        for thr in track(thrs, description="Getting user info"):
            thr.start()
            sleep(delay)

        for thr in thrs:
            thr.join()

        return user_infos

    def get_projects_by_cursus(self, cursus_id: int) -> list:
        """
        Get projects by cursus id.
        Useful for getting project infos.
        """

        def _get_projects_at_page(pagenum: int, client: httpx.Client):
            url = f"{self.BASE}/cursus/{cursus_id}/projects"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "page[number]": pagenum,
                "page[size]": 100,
            }
            r = client.get(url, headers=headers, params=params)
            return r.json()

        projects = []
        pagenum = 1
        with httpx.Client(timeout=self.timeout) as client:
            while r := _get_projects_at_page(pagenum, client):
                projects += r
                pagenum += 1

        return projects
