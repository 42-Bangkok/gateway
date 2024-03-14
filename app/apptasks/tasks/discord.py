from celery import shared_task
from discord_webhook import DiscordWebhook
from apptasks.models.configs import DiscordWebhook as DiscordWebhookModel


@shared_task
def send_simple_message(message: str, webhook_name: str) -> bool:
    """
    Sends a simple message to discord
    """
    q = DiscordWebhookModel.objects.filter(name=webhook_name).first()
    if q is None:
        raise Exception(f"Webhook: {webhook_name} not found")
    webhook_url = q.url
    webhook = DiscordWebhook(
        url=webhook_url,
        username="gateway",
        content=message,
    )
    webhook.execute()
    return True
