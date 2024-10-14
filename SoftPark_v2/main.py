from application import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # Przed wystawieniem apki na PROD - zmienić "debug=True" na "debug=False".