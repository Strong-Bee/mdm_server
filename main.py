from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(ssl_context=('cert/cert.pem', 'cert/key.pem'), host='0.0.0.0', port=443)
