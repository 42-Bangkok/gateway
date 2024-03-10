"""
Eval Pts Socialism manual script
"""

import pandas as pd
from appcore.services.console import console
from appcore.services.intra.intra import Intra
from appcore.services.intra.user import IntraUser
from apptasks.models.configs import DiscordWebhook
from apptasks.services.discohook import announce


def announce_socialism(target, webhook_url):
    """
    Announce the start of socialism
    """
    username = "Announcement"
    title = "The purge has begun"
    description = f"The purge has begun. Evaluation points exceeding {target} will be confiscated."
    image_url = "https://firebasestorage.googleapis.com/v0/b/ft-bangkok-general.appspot.com/o/alexis-montero-aGT9ofWZ9NA-unsplash.jpg?alt=media"
    announce(username, title, description, webhook_url, image_url)


def broadcast_socialism(description, webhook_url):
    """
    Broadcast the status of socialism
    """
    username = "Announcement"
    title = "The purge is ongoing..."
    announce(username, title, description, webhook_url)


def conclude_socialism(description, webhook_url):
    """
    Announce the end of socialism, plus conclusion
    """
    username = "Announcement"
    title = "The purge has ended"
    image_url = "https://firebasestorage.googleapis.com/v0/b/ft-bangkok-general.appspot.com/o/tim-mossholder-8R-mXppeakM-unsplash.jpg?alt=media"
    announce(username, title, description, webhook_url, image_url)


def socialism(target=10, dry_run=False):
    """
    Socialism
    :param target: take away pts greater than
    :param dry_run: dry run
    """
    match dry_run:
        case True:
            webhook = DiscordWebhook.objects.filter(name="testhook").first()
        case False:
            webhook = DiscordWebhook.objects.filter(name="socialism").first()
    if webhook is None:
        raise Exception("No webhook URL fo socialism found. Set one using Django Admin")
    webhook_url = webhook.url
    api = Intra()
    filter_params = {
        "filter[primary_campus_id]": 33,
    }
    users = api.cursus_users(cursus_id=21, filter_params=filter_params)
    df_users = pd.DataFrame(users)
    df_users = df_users[
        (df_users["correction_point"] > target) & (df_users["staff?"] == False)
    ]
    df_users.sort_values(by="correction_point", ascending=False, inplace=True)
    logins = df_users["login"].tolist()

    announce_socialism(target=target, webhook_url=webhook_url)

    pool_fill = 0
    for login in logins:
        user = IntraUser(login)
        is_blackholed = user.is_blackholed(cursus_id=21)
        correction_point = user.correction_point

        # Socialism if not blackholed
        if not is_blackholed:
            console.log(f"{login} gave {correction_point - target}")
            description = (
                f"{login} has given {correction_point - target} points to the pool."
            )
            broadcast_socialism(description=description, webhook_url=webhook_url)
            if not dry_run:
                point_taken = user.pts_socialism(target=target, refresh=False)
                console.log(f"{login} {point_taken} points")
            pool_fill += correction_point - target

    description = f"The pool has been filled with {pool_fill} points.\nThank you for your kind cooperation.\nSee you soon!"
    conclude_socialism(description, webhook_url)
