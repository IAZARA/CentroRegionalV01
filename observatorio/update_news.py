from app import create_app
from app.tasks import update_news

app = create_app()
with app.app_context():
    result = update_news()
    print(result)
