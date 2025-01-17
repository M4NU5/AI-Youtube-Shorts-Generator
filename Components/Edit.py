from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
import subprocess

change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick\\magick.exe"})

def extractAudio(video_path):
    try:
        video_clip = VideoFileClip(video_path)
        audio_path = "audio.wav"
        video_clip.audio.write_audiofile(audio_path)
        video_clip.close()
        print(f"Extracted audio to: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"An error occurred while extracting audio: {e}")
        return None


def crop_video(input_file, output_file, start_time, end_time, transcriptions):
    with VideoFileClip(input_file) as video:
        video_duration = video.duration
        if end_time > video_duration:
            end_time = video_duration

        cropped_video = video.subclip(start_time, end_time)

        # Generate subtitle clips
        subtitle_clips = []
        for text, start, end in transcriptions:
            # Skip subtitles outside the crop range
            if start >= end_time or end <= start_time:
                continue
        
        # Adjust subtitle timing relative to the cropped video
        subtitle_start = max(start - start_time, 0)
        subtitle_end = min(end - start_time, end_time - start_time)

        # Create a TextClip for the subtitle
        subtitle_clip = TextClip(
            text,
            fontsize=24,
            color='yellow',
            stroke_color='black',
            stroke_width=2
        ).set_start(subtitle_start).set_end(subtitle_end).set_pos('bottom')

        subtitle_clips.append(subtitle_clip)

        # Combine the cropped video with subtitles
        final_video = CompositeVideoClip([cropped_video] + subtitle_clips)

        final_video.write_videofile(output_file, codec='libx264')

# Example usage:
if __name__ == "__main__":
    input_file = r"processed_videos/processed_Rick and Morty S01E01 Pilot.mkv" ## Test
    print(input_file)
    output_file = "Short.mp4"
    start_time = 0.0
    end_time = 49.2   

    crop_video(input_file, output_file, start_time, end_time)

