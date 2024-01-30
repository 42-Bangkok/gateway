from discord_webhook import DiscordEmbed, DiscordWebhook


def announce(
    username,
    title,
    description,
    webhook_url,
    image_url=None,
    color="03b2f8",
):
    """
    Sends an announcement to a Discord webhook.

    Args:
        username (str): The username to display for the announcement.
        title (str): The title of the announcement.
        description (str): The description of the announcement.
        webhook_url (str): The URL of the Discord webhook to send the announcement to.
        image_url (str, optional): The URL of an image to include in the announcement. Defaults to None.
        color (str, optional): The color of the announcement. Defaults to "03b2f8".
    Returns:
        bool: True if the announcement was successfully sent.
    Raises:
        Exception: If the announcement could not be sent.
    """
    webhook = DiscordWebhook(url=webhook_url, username=username)
    embed = DiscordEmbed(
        title=title,
        description=description,
        color=color,
    )
    if image_url:
        embed.set_image(url=image_url)
    webhook.add_embed(embed)
    r = webhook.execute()
    if r.status_code not in [i for i in range(200, 300)]:
        raise Exception("Could not send announcement")

    return True
