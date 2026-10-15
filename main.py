import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    host = os.environ.get("MDM_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    cert_file = os.environ.get("SSL_CERT_FILE")
    key_file = os.environ.get("SSL_KEY_FILE")

    ssl_context = None
    if cert_file and key_file:
        if not os.path.isfile(cert_file) or not os.path.isfile(key_file):
            raise RuntimeError("SSL_CERT_FILE and SSL_KEY_FILE must point to existing files")
        ssl_context = (cert_file, key_file)

    app.run(host=host, port=port, ssl_context=ssl_context)
