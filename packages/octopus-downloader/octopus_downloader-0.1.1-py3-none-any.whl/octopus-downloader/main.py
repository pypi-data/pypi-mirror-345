import typer
import os
import secrets
import asyncio
from typing import Optional
from pathlib import Path
from rich.console import Console
from models.video_downloader import VideoDownloaderOptions
from providers.video import ProviderFactory


# 加载环境变量
if "RUNNER_TEMP" in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

# 初始化命令行器
app = typer.Typer(
    name="Octopus Downloader",
    help="A command line tool for downloading files from Octopus Deploy.",
    rich_markup_mode="rich",
    add_completion=False
)

console = Console()

@app.command("info")
def info(url: str = typer.Argument(..., help="The URL of the video playback page.")):
    """
    Get video information from the provided URL.
    """
    async def async_info():
        try:
            provider = ProviderFactory.create_provider(url)
            video_info = await provider.get_video_info(url)
            return video_info
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(async_info())

@app.command("download")
def download(
    url: str = typer.Argument(..., help="The URL of the file to download."),
    output_dir: Path = typer.Option(None, "--output-dir", "-d", help="The directory to save the downloaded file."),
    filename: Optional[str] = typer.Option(None, "--filename", "-f", help="The name of the downloaded file.")
):
    """
    Download a file from the provided URL.
    This command will download the file and save it to the specified output directory.
    
    Args:
        url (str): The URL of the file to download.
        output_dir (str): The directory to save the downloaded file.
        filename (str): The name of the downloaded file.
    """
    if not output_dir or not output_dir.exists():
        console.print(f"[red]Output directory does not exist: {output_dir}[/red]")
        raise typer.Exit(code=1)

    if not filename:
        filename = secrets.token_urlsafe(8) + ".mp4"

    options = VideoDownloaderOptions(
        url=url,
        output_dir=output_dir,
        filename=filename
    )

    async def async_download():
        try:
            console.print(f"[green]Starting download from {url}...[/green]")

            provider = ProviderFactory.create_provider(url)

            video_info = await provider.get_video_info(url)
            if not video_info:
                console.print(f"[red]Failed to parse video info from {url}[/red]")
                raise typer.Exit(code=1)
            
            output_file = os.path.join(output_dir, filename)
            
            await provider.download_video(video_info['download_url'], output_file)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(code=1)
    
    asyncio.run(async_download())


if __name__ == "__main__":
    app()