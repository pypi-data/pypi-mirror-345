import logging
from pathlib import Path

from command_runner import command_runner
from pydantic import BaseModel
from commons.network import IPV4_LOOPBACK


class CertificateFiles(BaseModel):
    domain: str = IPV4_LOOPBACK
    cert: Path
    key: Path


def get_cert(save_to: Path, domains: list[str] | None = None) -> dict[str, CertificateFiles] | CertificateFiles:
    """
    Create an X.509 certificate with key. If no domain is provided, a local certificate is created for 0.0.0.0 (loopback)

    :param save_to: file destination path
    :param domains: list of domains
    :return: location of the certificates
    """

    domains = domains if domains else [IPV4_LOOPBACK]
    generated_certs: dict[str, CertificateFiles] = {}
    # TODO: implement certbot

    if not save_to.exists():
        import os
        os.mkdir(save_to)

    for domain in domains:
        file: CertificateFiles = CertificateFiles(
            cert=Path(f"{save_to / domain}.pem"),
            key=Path(f"{save_to / domain}-key.pem")
        )

        cmd = f"mkcert -cert-file {file.cert.resolve()} -key-file {file.key.resolve()} {domain}"

        logging.getLogger(__file__).debug(f"Full command: '{cmd}'")

        exit_code, output = command_runner(cmd, silent=True)

        if exit_code == 253:
            raise RuntimeError("'mkcert' not found.")

        generated_certs[domain] = file

    return generated_certs if len(generated_certs) > 1 else generated_certs[domains[0]]
