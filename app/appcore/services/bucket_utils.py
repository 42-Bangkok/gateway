import os
from uuid import uuid4

from appcore.services.utils import slugify


def gen_fp(filename: str, base_path: str):
    """generate slugified filename

    Args:
        filename (str): filename
        base (str): base path ex. cdn/images/.../
    """
    extension = filename.split(".")[-1]
    filename = slugify(str(uuid4())).replace("_", "")

    return f"{base_path}/{filename}.{extension}"


def gen_url(name: str):
    """generate url from filename

    Args:
        name (str): name

    Returns:
        str: url
    """
    base = os.getenv("AWS_BUCKET_URL")
    bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")

    return f"{base}/{bucket}/{name}"
