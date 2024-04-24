# flake8: noqa
"""
For test fetching all cadet data
"""

import io
from celery import shared_task
import pandas as pd
from dateutil.parser import parser
from django.utils import timezone
from discord_webhook import DiscordEmbed, DiscordWebhook

from appdata.models.intras import HistIntraProfileData
from apptasks.models.configs import DiscordWebhook as DiscordWebhookModel


@shared_task
def bh_chaser() -> bool:
    """
    Sends a message to discord with the number of cadets that will be blackholed in the next 45 days
    Requires a webhook named notifications set in DjangoAdmin
    """
    discord_webhook = DiscordWebhookModel.objects.filter(name="notifications").first()
    if discord_webhook is None:
        raise Exception(
            "Discord webhook: notifications not found, add it in DjangoAdmin"
        )

    filters = {
        "profile__cursus_ids__contains": [21],
    }
    qs = (
        HistIntraProfileData.objects.filter(**filters)
        .order_by("profile", "-created")
        .distinct("profile")
    )
    # get users with bh not None
    bh_data = []
    for profile in qs:
        for cursus_user in profile.data["cursus_users"]:
            if cursus_user["cursus_id"] == 21:
                blackholed_at = cursus_user["blackholed_at"]
                level = cursus_user["level"]
        if blackholed_at is not None:
            login = profile.data["login"]
            pool_month = profile.data["pool_month"]
            pool_year = profile.data["pool_year"]
            email = profile.data["email"]
            first_name = profile.data["first_name"]
            last_name = profile.data["last_name"]
            bh_data.append(
                {
                    "login": login,
                    "level": level,
                    "pool_month": pool_month,
                    "pool_year": pool_year,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "blackholed_at": parser().parse(blackholed_at),
                }
            )

    # filter bh_data
    df = pd.DataFrame(bh_data).sort_values("blackholed_at")
    df["bh_in"] = df["blackholed_at"] - timezone.now()
    df["bh_in"] = df["bh_in"].dt.days
    df = df[df["bh_in"] >= -1]
    df_14 = df[df["bh_in"] <= 14]
    df_14_30 = df[(df["bh_in"] > 14) & (df["bh_in"] <= 30)]
    df_45 = df[df["bh_in"] <= 45]

    # instantiate webhook and embed
    webhook = DiscordWebhook(url=discord_webhook.url)
    embed = DiscordEmbed(
        title="BH report v2 testing", description="Every day", color="03b2f8"
    )
    embed.add_embed_field(name="in 14 days", value=f"{len(df_14)}", inline=False)
    embed.add_embed_field(name="in 14-30 days", value=f"{len(df_14_30)}", inline=False)
    embed.add_embed_field(name="in 45 days", value=f"{len(df_45)}", inline=False)
    webhook.add_embed(embed)

    # Build csv payload
    buffer = io.StringIO()
    str_today = str(timezone.now()).split(" ")[0]
    fname = f"blackhole_{str_today}.csv"
    df.to_csv(buffer, index=False)

    webhook.add_file(file=buffer.getvalue(), filename=fname)
    r = webhook.execute()

    return r.status_code == 200
