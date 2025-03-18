import asyncio

class ProgressManager:
    def __init__(self):
        self.tasks = {}  # Store progress updates for tasks

    async def create_task(self, task_id):
        """Initialize a new task progress queue."""
        self.tasks[task_id] = asyncio.Queue()

    async def update_progress(self, task_id, progress, message):
        """Send progress update to the queue."""
        if task_id in self.tasks:
            await self.tasks[task_id].put({"progress": progress, "message": message})

    async def get_progress_stream(self, task_id):
        """Stream progress updates."""
        if task_id not in self.tasks:
            yield {"progress": 0, "message": "Task not found."}
            return

        while True:
            progress_data = await self.tasks[task_id].get()
            yield progress_data
            if progress_data["progress"] == 100:
                del self.tasks[task_id]  # Remove completed tasks
                break

progress_manager = ProgressManager()
