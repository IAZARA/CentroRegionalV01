from app.tasks import update_news

if __name__ == '__main__':
    # Ejecutar la tarea de actualización de noticias
    result = update_news.delay()
    print("Tarea de actualización de noticias iniciada. ID de tarea:", result.id)
