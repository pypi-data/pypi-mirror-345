import argparse
from .PlaylistDownloader import PlaylistDownloader

def main():
    parser = argparse.ArgumentParser(
        description="Convert a YouTube playlist into a single combined MP3 file."
    )
    parser.add_argument("url", help="YouTube playlist URL to download")
    parser.add_argument(
        "-o", "--output",
        default="combined.mp3",
        help="Output MP3 filename (default: combined.mp3)"
    )
    args = parser.parse_args()

    downloader = PlaylistDownloader(args.url)
    try:
        downloader.downloadPlaylist(output_file=args.output)
    except Exception as e:
        print(f"❌ Error: {e}")