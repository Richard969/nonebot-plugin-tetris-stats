from base64 import b64encode
from io import BytesIO
from random import choice, randint

from PIL import Image
from PIL.Image import Resampling

from .draw import PIECE_MEMBERS, SkinManager


def get_avatar() -> str:
    skin = (
        SkinManager.get_skin()
        .get_piece(choice(PIECE_MEMBERS))  # noqa: S311
        .rotate(
            randint(-360, 360),  # noqa: S311
            expand=True,
            resample=Resampling.BICUBIC,
        )
    )
    skin = skin.crop(skin.getbbox())
    background = Image.new('RGBA', (2048, 2048), '#e5e5e5')

    skin_ratio = min(1536 / skin.width, 1536 / skin.height)

    new_size = (int(skin.width * skin_ratio), int(skin.height * skin_ratio))
    skin = skin.resize(new_size, Resampling.BICUBIC)

    background.paste(skin, ((background.width - skin.width) // 2, (background.height - skin.height) // 2), mask=skin)
    background = background.resize((512, 512), Resampling.LANCZOS)
    with BytesIO() as output:
        background.save(output, format='PNG')
        return f'data:image/png;base64,{b64encode(output.getvalue()).decode("utf-8")}'