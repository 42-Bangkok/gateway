from datetime import datetime
import logging
from time import sleep

import dateutil
import httpx
import pytz
from appcore.services.intra.intra import Intra
from dateutil.parser import parse as datetime_parse
from django.utils import timezone
from pydantic import validate_call
import pandas as pd


class IntraUser(Intra):
    """
    Represents a user from the 42 API.
    """

    DISABLED_METHODS = [
        "users",
        "pools",
    ]

    @validate_call
    def __init__(self, login: str, data: dict = None):
        """
        Initialize the user.
        Args:
            login (str): The login of the user.
            data (dict, optional): The data of the user. Defaults to None. If not provided, the data will be fetched from the API.
            pts_gain (int, optional): The evalation points gained by the user calculated by calling calc_eval_pts_gainloss. Defaults to None.
            pts_lost (int, optional): The evalation points lost by the user calculated by calling calc_eval_pts_gainloss. Defaults to None.

        """
        super().__init__()
        self.login = login
        if data:
            self.data = data
        elif data is None:
            self.data = self.user(login)
        self._disable_methods(self.DISABLED_METHODS)

        self.pts_gain: int | None = None
        self.pts_lost: int | None = None

    def _disable_methods(self, methods: list):
        """
        Disable methods from the list.
        """

        def _raise_exception():
            raise Exception("Superclass method disabled")

        for method in methods:
            setattr(self, method, _raise_exception)

    @property
    def id(self) -> int:
        """
        Get the ID of the user.

        Returns:
            int: The ID of the user.
        """
        return self.data["id"]

    @property
    def correction_point(self) -> int:
        """
        Returns the correction point of the user.
        Returns:
            int: The correction point of the user.
        """
        return self.data["correction_point"]

    def level(self, cursus_id: int) -> int:
        """
        Return the level of the user in the given cursus. 0 if not in the cursus.
        :param cursus_id: The cursus id.
        :return: The level of the user in the given cursus.
        """
        for cu in self.data["cursus_users"]:
            if cu["cursus_id"] == cursus_id:
                return cu["level"]

        return 0

    def project_users(self, cursus_id: int) -> list:
        """
        Return the project users of the user in the given cursus. [] if not in the cursus.
        :param cursus_id: The cursus id.
        :return: The project users of the user in the given cursus.
        """
        ret = []
        for pu in self.data["projects_users"]:
            if cursus_id in pu["cursus_ids"]:
                ret.append(pu)

        return ret

    def calc_total_tries(self, cursus_id):
        """
        Returns total number of tries by user in given cursus_id
        """
        project_users = self.project_users(cursus_id)

        if len(project_users) == 0:
            return 0

        df = pd.DataFrame(project_users)
        df["tries"] = df["occurrence"] + 1

        return df["tries"].sum()

    def project_final_mark(self, cursus_id: int, project_slug: str) -> int | None:
        """
        Return the final mark of the user in the given project. None if not in the project.
        :param project_slug: The project slug.
        :param cursus_id: The cursus id.
        :return: The final mark of the user in the given project.
        """
        for project in self.project_users(cursus_id):
            if project["project"]["slug"] == project_slug:
                return project["final_mark"]

        return None

    def project(self, cursus_id: int, project_slug: str) -> dict:
        """
        Return the project of the user in the given cursus. {} if not in the cursus.
        :param cursus_id: The cursus id.
        :return: The project of the user in the given cursus.
        """
        for project in self.project_users(cursus_id):
            if project["project"]["slug"] == project_slug:
                return project

        return {}

    @validate_call
    def set_correction_point(
        self, value: int, reason: str, refresh: bool = True
    ) -> bool:
        """Sets the correction point for the user.

        Args:
            value (int): The new correction point value.
            reason (str): The reason for changing the correction point.
            refresh (bool, optional): Whether to refresh the user data after setting the correction point. Defaults to True.

        Returns:
            bool: True if the correction point was successfully set.

        Raises:
            ValueError: If the value is negative.
            Exception: If the correction point could not be set.
        """
        if value < 0:
            raise ValueError("Correction point cannot be negative")
        if value == self.correction_point:
            return True

        diff = value - self.correction_point
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"reason": reason, "amount": diff}
        url = f"{self.BASE}/users/{self.login}/correction_points/add"
        with httpx.Client() as client:
            r = client.post(url, headers=headers, params=params, timeout=self.timeout)
        if r.status_code not in [i for i in range(200, 300)]:
            raise Exception("Could not set correction point")

        if refresh:
            self.data = self.user(self.login)
        else:
            self.data["correction_point"] = value

        return True

    @validate_call
    def pts_socialism(self, target: int, refresh=True) -> int:
        """
        `OUR` points, comrade.
        If the user has more than the target points, we `DONATE` them
        and add them to `THE PEOPLE's POOL`.
        Args:
            :param target: The target points. If the user has more points than the target, the excess points will be donated.
            :param refresh: A boolean flag indicating whether to refresh the user's data after the points are donated. Default is True.
        Returns:
            :return: The number of points taken from the user and donated to the pool.
        """
        REASON = "Provided points to the pool."

        if self.correction_point <= target:
            return 0
        diff = self.correction_point - target
        self.set_correction_point(target, REASON)
        self.pool_add_pts(diff)

        if refresh:
            self.data = self.user(self.login)
        else:
            self.data["correction_point"] = target

        return diff

    @validate_call
    def blackholed_at(self, cursus_id: int = 21) -> datetime:
        """
        Returns the blackholed_at datetime for the given cursus_id.

        Args:
            cursus_id (int): The ID of the cursus.

        Returns:
            datetime: The blackholed_at datetime if available, None otherwise.

        Raises:
            ValueError: If the user is not in the specified cursus.
        """
        for cursus in self.data["cursus_users"]:
            if cursus["cursus_id"] == cursus_id:
                if cursus["blackholed_at"] is None:
                    return None
                blackholed_at = datetime_parse(cursus["blackholed_at"])
                return blackholed_at

        raise ValueError("User is not in this cursus")

    @validate_call
    def is_blackholed(self, cursus_id: int = 21) -> bool:
        """
        Check if the user is blackholed for the given cursus.

        Args:
            cursus_id (int): The ID of the cursus. Default is 21.

        Returns:
            bool: True if the user is blackholed, False otherwise.
        """
        blackholed_at = self.blackholed_at(cursus_id)
        if blackholed_at is None:
            return False

        return blackholed_at < timezone.now()

    @validate_call
    def change_email(self, email: str) -> bool:
        """Change user's email

        Args:
            email (str): new email

        Returns:
            bool: True if success,
        Exception: if failed
        """
        url = self.api.BASE + f"/users/{self.login}"
        headers = {
            "Authorization": f"Bearer {self.api.access_token}",
            "Content-Type": "application/json",
        }
        r = httpx.patch(
            url,
            headers=headers,
            json={"user": {"email": email}},
        )
        r.raise_for_status()

        return True

    def get_correction_point_hist(self) -> list:
        """
        /users/:user_id/correction_point_historics?filter[reason]=&page[size]=100&page[number]=1
        Returns:
            list: A list of correction point history.
        """

        def _get_at_page(pagenum):
            url = f"{self.BASE}/users/{self.login}/correction_point_historics?page[number]={pagenum}&page[size]=100"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            r = httpx.get(url, headers=headers)
            tries = 10
            while r.status_code != 200:
                if tries == 0:
                    raise Exception(
                        f"Failed to get correction point history for {self.login=}"
                    )
                logging.info(
                    f"get_correction_point_hist {self.login=} Failed! Retrying {tries=}"
                )
                r = httpx.get(url, headers=headers)
                tries -= 1
                sleep(1)
            return r.json()

        l_eval_hists = []
        pagenum = 1
        while r := _get_at_page(pagenum):
            l_eval_hists += r
            pagenum += 1

        return l_eval_hists

    def calc_eval_pts_gainloss(self) -> tuple[int, int]:
        """
        Returns total sum of current points gained/ loss by evaluation
        Sets self.pts_gain and self.pts_lost
        Returns:
            tuple[int, int]: The total points gained and lost by evaluation.
        """
        l_eval_hists = self.get_correction_point_hist()
        df_eval_hist = pd.DataFrame(l_eval_hists)
        self.pts_lost = abs(
            df_eval_hist[df_eval_hist["reason"] == "Defense plannification"][
                "sum"
            ].sum()
        )
        self.pts_gain = df_eval_hist[df_eval_hist["reason"] == "Earning after defense"][
            "sum"
        ].sum()

        return self.pts_gain, self.pts_lost

    def get_last_active_date_by_project_update(self, cursus_id):
        """
        Return the last active date of the user in the given cursus. '1970-01-01T00:00:00Z' if KeyErro
        :param cursus_id: The cursus id.
        :return: The last active date of the user in the given cursus.
        """
        try:
            df = pd.DataFrame(self.project_users(cursus_id=cursus_id))
            dt = df["updated_at"].apply(dateutil.parser.parse).max()
            return dt
        except KeyError:
            return dateutil.parser.parse("1970-01-01T00:00:00Z")

    def get_days_since_last_active_date_by_project_update(self, cursus_id):
        """
        Return the days since the last active date of the user in the given cursus. Returns very big number if ERRORs.
        :param cursus_id: The cursus id.
        :return: The days since the last active date of the user in the given cursus.
        """
        delta = datetime.now(pytz.UTC) - self.get_last_active_date_by_project_update(
            cursus_id=cursus_id
        )

        return delta.days

    def __repr__(self):
        return f"<User {self.login}>"

    def __str__(self):
        return self.login
