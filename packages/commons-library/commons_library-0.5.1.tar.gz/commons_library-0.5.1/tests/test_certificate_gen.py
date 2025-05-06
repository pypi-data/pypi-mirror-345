import tempfile
import unittest
from pathlib import Path


class TestSSL(unittest.TestCase):
    def test_local_cert_gen(self):
        from commons.network.http import certs

        files = certs.get_cert(Path(tempfile.mkdtemp()))

        assert files.cert.exists()
        assert files.key.exists()
