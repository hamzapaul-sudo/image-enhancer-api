from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Use Redis as the message queue
    backend="redis://localhost:6379/0"
)

@celery_app.task
def remove_background_task(input_path: str, output_path: str):
    from rembg import remove
    with open(input_path, "rb") as file:
        input_image = file.read()

    result = remove(input_image)

    with open(output_path, "wb") as out_file:
        out_file.write(result)

    return output_path
