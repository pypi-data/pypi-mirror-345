from pydub import AudioSegment
import tempfile
import os
from yt_dlp import YoutubeDL


class PlaylistDownloader:
    def __init__(self, playlist_url: str):
        self.playlist_link = playlist_url

    def downloadPlaylist(self, output_file: str = "combined.mp3"):
        with tempfile.TemporaryDirectory(prefix="ytp2mp3_") as tmpdir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(tmpdir, '%(playlist_index)03d_%(title).200s.%(ext)s'),
                'quiet': False,
                'noplaylist': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with YoutubeDL(ydl_opts) as ydl:
                print("Downloading playlist...")
                ydl.download([self.playlist_link])

            audio_files = sorted(
                [f for f in os.listdir(tmpdir) if f.endswith('.mp3')]
            )

            if not audio_files:
                raise Exception("No audio files found!")

            print("Combining audio...")
            combined = AudioSegment.empty()
            for fname in audio_files:
                path = os.path.join(tmpdir, fname)
                combined += AudioSegment.from_file(path)

            combined.export(output_file, format="mp3")
            print(f"\nCombined MP3 saved to: {output_file}")

# test usage
if __name__ == "__main__":
    url = "https://youtube.com/playlist?list=PLERI1_ESTKAyaWKpE5I_uVpzbzmm4HkI5&si=DxlpgQkG3dBdNXdL" 
    downloader = PlaylistDownloader(url)
    downloader.downloadPlaylist()


    

