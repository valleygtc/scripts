# https://dummyimage.com/{width}x{height}/{background}/{text_color}/{name}.{jpg/png/gif}
# https://dummyimage.com/600x400/000/fff.jpg

# requirements:
# requests
# Pillow
# Click


# 功能：根据现有的图片，生成和它尺寸一样的伪图。
import uuid
from pathlib import Path
import io

import requests
from requests.exceptions import Timeout
import click
from PIL import Image, ImageDraw, ImageFont


def fake_img(width, height):
    """Fake img use https://dummyimage.com/ HTTP API

    Params:
        width [int]
        height [int]
    Return:
        content [bytes]: image binary data.
    Exceptions:
        Exception
    """
    filename = uuid.uuid4()
    try:
        # background: gray, text_color: black
        resp = requests.get(f'https://dummyimage.com/{width}x{height}/eeeeee/000000/foo.jpg', timeout=3)
    except Timeout as e:
        raise Exception(f'network error: {e}')
    except Exception as e:
        raise Exception(f'network error: {e}')

    return resp.content


def fake_img2(width, height):
    """Fake img use Pillow

    Output image has gray background and text {width}x{height} in the center.

    Params:
        width [int]
        height [int]
    Return:
        content [bytes]: image binary data.
    Exceptions:
        Exception
    """
    img = Image.new('RGB', (width, height), color=(0xee, 0xee, 0xee))
     
    d = ImageDraw.Draw(img)
    text = f'{width}x{height}'

    # font size 和 width（pixel） 貌似不是线性的关系。
    # 但是这里还是直接用 10 作为除数，经实践检验，效果还是很好的。
    # 参考：
    # https://stackoverflow.com/questions/4902198/pil-how-to-scale-text-size-in-relation-to-the-size-of-the-image
    # https://github.com/rmax/django-dummyimage/blob/master/dummyimage/models.py#L64
    cnr_font = ImageFont.truetype('instance/cnr.otf', width//10)
    text_w, text_h = d.textsize(text, font=cnr_font)
    d.text(
        ((width - text_w)/2, (height - text_h)/2),
        text,
        fill=(0, 0, 0),
        font=cnr_font,
    )
    output = io.BytesIO()
    img.save(output, format='JPEG')
    return output.getvalue()


def imitate_file(src_path, dest_dir):
    """
    Params:
        src_path [Path]: should be a file.
        dest_dir [Path]: should be a directory.
    Return:
        dest_path [Path]
    Exceptions:
        Exception
    """
    with Image.open(src_path) as img:
        width, height = img.size
    content = fake_img2(width, height)
    fname = uuid.uuid4()
    dest_path = dest_dir.joinpath(f'{fname}.jpg')
    with open(dest_path, 'wb') as fh:
        fh.write(content)
    return dest_path


@click.command('main')
@click.argument('src')
@click.argument('dest')
def main(src, dest):
    """Fake image based on the src image/images' size.

    SRC can be a image file or a directory contain only images.

    DEST should be a directory.
    """
    src_path = Path(src)
    dest_dir = Path(dest)
    if not src_path.exists():
        print(f'Error: {src_path} not exists.')
        return
    if not dest_dir.exists():
        print(f'Error: {dest_dir} not exists.')
        return

    if src_path.is_file():
        try:
            dest_path = imitate_file(src_path, dest_dir)
        except Exception as e:
            print(f'Error: {e}')
        else:
            print(f'Done: {src_path} -> {dest_path}')
    elif src_path.is_dir():
        for fp in src_path.iterdir():
            try:
                dest_path = imitate_file(fp, dest_dir)
            except Exception as e:
                print(f'Error: {e}')
            else:
                print(f'Done: {fp} -> {dest_path}')
    else:
        print(f'Error: {src_path} is not a regular file nor a directory.')
        return


if __name__ == '__main__':
    main()
