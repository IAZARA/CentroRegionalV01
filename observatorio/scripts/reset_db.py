from app import create_app, db

def reset_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Base de datos reiniciada exitosamente")

if __name__ == '__main__':
    reset_database()
