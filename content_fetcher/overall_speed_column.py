from rich.progress import ProgressColumn
from rich.text import Text
import time

class OverallSpeedColumn(ProgressColumn):
    def render(self, task):
        if not task.started or task.finished:
            return Text("— MB/s", style="progress.data.speed")

        elapsed = task.elapsed or 0
        if elapsed == 0:
            return Text("0.00 MB/s", style="progress.data.speed")

        avg_speed = task.completed / elapsed / (1024 * 1024)
        return Text(f"{avg_speed:.2f} MB/s", style="progress.data.speed")
