import logging
import tempfile
import unittest
from pathlib import Path

from commons.database import DatabaseAdapter

TEMP_DIR: Path = Path(tempfile.mkdtemp())
logging.getLogger(__file__).warning(f"Temporary directory: {TEMP_DIR.resolve()}")


class TestModels(unittest.TestCase):
    @staticmethod
    def _get_db() -> DatabaseAdapter:
        return DatabaseAdapter(
            scheme="sqlite",
            database=tempfile.mktemp()
        )

    def test_generic_resource(self):
        from commons.models import Resource
        from sqlmodel import SQLModel, Field, select

        def uuid_factory():
            import uuid
            return str(uuid.uuid4())

        class ChildResource(Resource, table=True):
            id: str = Field(primary_key=True, nullable=False, default_factory=uuid_factory)

        db = self._get_db()
        resource = ChildResource()

        assert resource and resource.is_local() and resource.scheme() == "memory"
        assert not resource.read()

        SQLModel.metadata.create_all(db.engine())
        with db.session() as session:
            session.add(resource)
            assert session.exec(select(ChildResource)).first()
            session.commit()
            session.close()

    def test_pix(self):
        from commons.currencies.payments import Pix
        from commons.media import Image

        pix: Pix = Pix(
            receiver_name="Sample Person",
            key="pix@mail.com",
            amount=0.01
        )

        assert pix.brcode()
        image: Image = pix.qrcode()
        assert image
        assert image.base64()

    def test_image(self):
        from PIL import Image as PILImage
        from commons.media import Image
        from commons.media import mimetypes
        from io import BytesIO

        # Create a 1x1 pixel image with a transparent background
        png_img = PILImage.new("RGBA", (1, 1), (0, 0, 0, 0))  # RGBA mode for transparency
        buffer = BytesIO()
        img: Image = Image()

        png_img.save(buffer, "png")
        img.data=buffer.getvalue()

        assert img.media_type == mimetypes.IMAGE_PNG
        assert img.width == 1
        assert img.height == 1
        assert img.is_local()
        assert img.base64()

        _d = img.model_dump(exclude={"url", "path"})
        _d["location"] = tempfile.mktemp()
        img2 = Image(**_d)
        img2.save()
        assert img2.path.exists()
