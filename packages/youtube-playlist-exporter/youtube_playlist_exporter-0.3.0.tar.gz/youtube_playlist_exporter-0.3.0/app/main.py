import asyncio
import os

import aiohttp
import typer
from typing_extensions import Annotated

from app.exportmanager import YouTubePlaylistExportManager
from app.options import Options

app = typer.Typer()


@app.command()
def main(playlist_id: Annotated[str, typer.Option(help="The YouTube id of the playlist to export")],
         youtube_auth_key: Annotated[str, typer.Option(
             help="The API key provided by YouTube",
             envvar="AUTH_KEY")],
         output_dir: Annotated[str, typer.Option(
             default_factory=os.getcwd,
             help="The script's output directory (must be an existing directory!) [default: current working directory]")],
         playlist_name: Annotated[str | None, typer.Option(
             help="The name of the playlist to back-up. Only used for generating the names of the output files "
                  "[default: the playlist id]")] = None,
         private_playlist: Annotated[bool | None, typer.Option(
             help="Is the playlist private")] = False,
         secret_file: Annotated[str | None, typer.Option(
             help="Needed only for private playlists: path of client's secret file, see README.md for more details")] = None,
         only_titles: Annotated[bool, typer.Option(
             help="Whether to export just the video titles instead of a full CSV")] = False,
         new_videos_first: Annotated[bool, typer.Option(
             help="Relevant only if --only-titles is specified: whether new videos are added to the beginning of the "
                  "specified playlist "
                  "(in favorites' playlists they are added to the beginning, in other playlists to the end)")] = False,
         ):
    asyncio.run(_run(Options(playlist_id=playlist_id,
                             youtube_auth_key=youtube_auth_key,
                             output_dir=output_dir,
                             playlist_name=playlist_name,
                             are_new_videos_last=not new_videos_first,
                             csv_output=not only_titles,
                             private_playlist=private_playlist,
                             secret_file=secret_file,
                             )))


async def _run(options: Options):
    async with aiohttp.ClientSession() as session:
        await YouTubePlaylistExportManager(session, options).export_playlist()


if __name__ == "__main__":
    app()
