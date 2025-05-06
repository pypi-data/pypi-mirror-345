from io import BytesIO
from pathlib import Path
from typing import Optional

from httpx import URL

from commons.media import mimetypes
from commons.models import Resource


class Processor:
    def __init__(self, data: bytes):
        from PIL import Image

        self.data = data
        self.image = Image.open(BytesIO(data))  # Create an Image based on an in-memory image bytestream
        self.buffer = BytesIO()

    def compress(self):
        self.image.save(self.buffer, self.image.format, optimize=True, quality=9)

        return self

    def convert(self, to_type: str = mimetypes.IMAGE_WEBP):
        _type = to_type

        match _type:
            case mimetypes.IMAGE_WEBP:
                self.image.save(self.buffer, "WEBP")
            case mimetypes.APPLICATION_PDF:
                import img2pdf
                self.buffer.write(img2pdf.convert(self.data))
            case _:
                raise ValueError(f'\'{to_type}')

        return self

    def get(self):
        self.buffer.seek(0)  # Move the bytestream pointer to the beginning

        return self.buffer.read()


# noinspection PyUnresolvedReferences
class Image(Resource):
    alt: Optional[str] = None

    def __init__(self, location: Optional[str | Path | URL] = None,
                 alt: Optional[str] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 data: Optional[bytes] = None,
                 media_type: Optional[str] = None):
        if location:
            super().__init__(location=location, data=data)
        else:
            super().__init__(data=data)

        self.alt = alt
        self._width = width if (width and width > 0) else None
        self._height = height if (height and height > 0) else None
        self._media_type = media_type

    def convert(self, to_type: str = mimetypes.IMAGE_WEBP):
        return Image(data=Processor(self.read()).convert(to_type).get())

    @property
    def md5(self) -> str:
        from hashlib import md5
        return md5(self.read()).hexdigest()

    @property
    def _img(self):
        from PIL import Image
        return Image.open(BytesIO(self.read()))

    @property
    def width(self) -> int:
        if not self._width:
            self._width = self._img.width
        return self._width

    @property
    def height(self) -> int:
        if not self._height:
            self._height = self._img.height
        return self._height

    @property
    def media_type(self) -> str:
        """
        Loads an image and checks its format. Be careful on loading remote images
        """
        if not self._media_type:
            self._media_type = mimetypes.lookup(self._img.format)
        return self._media_type

    def compress(self):
        return Image(data=Processor(self.read()).compress().get())

    def save(self):
        if ((self.is_local() and self.scheme() != "memory") and
                (self.path.is_dir() and self.path.exists()) or (self.path.parent.exists())):
            self.path.write_bytes(data=self.read())

    def copy_to(self, destination: Path, optimize: bool = False, preserve_filename: bool = True) -> Path | None:
        """
        Copy an image to a destiny and optionally optimize by converting JPG and PNG to WEBP.
        """
        img: Optional[bytes] = None
        target: Optional[Path] = None

        if self.is_local() and (destination and destination.is_dir() and destination.exists()):
            if optimize and (self.media_type == mimetypes.IMAGE_JPEG or
                             self.media_type == mimetypes.IMAGE_PNG):
                img = Processor(self.read()).convert().get()
            else:
                img = self.read()

            if preserve_filename:
                target = destination / str(self.filename)
            else:
                target = destination / self.md5

            if target:
                target.write_bytes(img)

                return target

    def base64(self) -> str:
        import base64
        return f'data:image/png;base64,{base64.b64encode(self.read()).decode()}'
