import unittest


class TestMIMETypes(unittest.TestCase):
    def test_lookup(self):
        from commons.media import mimetypes

        assert mimetypes.lookup(".png") == mimetypes.IMAGE_PNG
        assert mimetypes.lookup("jpg") == mimetypes.IMAGE_JPEG
        assert mimetypes.lookup(".PDF") == mimetypes.APPLICATION_PDF
        assert mimetypes.lookup("json") == mimetypes.APPLICATION_JSON
        assert mimetypes.lookup("image.webp") == mimetypes.IMAGE_WEBP
        assert mimetypes.lookup("http://example.com/image.png") == mimetypes.IMAGE_PNG
