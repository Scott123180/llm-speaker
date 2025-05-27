import requests
import concurrent.futures
import os

from rich.progress import Progress, DownloadColumn, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.console import Console
from .overall_speed_column import OverallSpeedColumn

# Create a shared console and progress manager
console = Console()
progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(),
    DownloadColumn(),
    TransferSpeedColumn(),
    OverallSpeedColumn(),
    TimeRemainingColumn(),
    transient=False, # this keeps the progress bars after completion
    console=console,
)

# DO NOT RAISE ABOVE 5 AS IT MIGHT CRASH THE SERVER
max_workers = 3  # Change this to control the number of parallel downloads
output_dir = "/media/biosdaddy/WD Red/archives"


def download_file_with_speed(url, filepath):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192  # 8 KB
        filename = os.path.basename(filepath)

        task_id = progress.add_task("download", filename=filename, total=total_size)


        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))

        console.print(f"downloaded file {url}")

        # remove the task from view
        progress.remove_task(task_id)


    except Exception as e:
        console.print(f"Failed to download {url}: {e}")


def download_task(ref_id):
    url = f"https://media-archive.zmmapple.com/pages/download.php?direct=1&ref={ref_id}&ext=mp3"
    file_name = f"{ref_id}.mp3"
    file_path = os.path.join(output_dir, file_name)

    download_file_with_speed(url, file_path)


def main():
    # This is the absolute path of the current package
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the file with ref values
    file_name = "loori_talks.txt"
    #file_name = "test.txt" # should be in the webscraper directory
    ref_file = os.path.join(base_dir, file_name)

    # Directory to save the files
    os.makedirs(output_dir, exist_ok=True)

    # Read ref values from file
    with open(ref_file, 'r') as f:
        ref_ids = [line.strip() for line in f if line.strip().isdigit()]

    console.print(f"Number of ref values (files to download): {len(ref_ids)}")
    console.print(
    "[bold]Filename         │ Progress │ Downloaded │ Curr Speed │ Avg Speed │ ETA[/bold]"
)

    with progress:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(download_task, ref_ids)


if __name__ == "__main__":
    main()