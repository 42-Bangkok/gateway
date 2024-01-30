from datetime import datetime

import httpx
from appcore.services.intra.api import Intra
from dateutil.parser import parse as datetime_parse
from django.utils import timezone
from pydantic import validate_call


class User(Intra):
    """
    Represents a user from the 42 API.
    """

    DISABLED_METHODS = [
        "users",
        "pools",
    ]

    @validate_call
    def __init__(self, login: str):
        super().__init__()
        self.login = login
        self.data = self.user(login)
        self._disable_methods(self.DISABLED_METHODS)

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
            r = client.post(url, headers=headers, params=params)
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
        REASON = "Evaluation point socialism."

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

    def __repr__(self):
        return f"<User {self.login}>"

    def __str__(self):
        return self.login
