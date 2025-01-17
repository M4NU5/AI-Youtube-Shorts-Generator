import cv2
import numpy as np
from moviepy.editor import *
# from Components.Speaker import detect_faces_and_speakers, Frames
global Fps

from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
import os
import tempfile

import cv2
from moviepy.editor import VideoFileClip, ImageSequenceClip
from moviepy.video.fx.crop import crop
from pydub import AudioSegment, silence
import subprocess


def zoom_with_blur(input_video_path, output_video_path):
    """
    Crops a video to 5:4 aspect ratio, applies a zoom, and overlays it on a blurred 9:16 background.
    
    Parameters:
    - input_video_path: Path to the input video.
    - output_video_path: Path to save the output video.
    - zoom_factor: A float representing the zoom level. 1.0 = no zoom, >1 = zoom in, <1 = zoom out.
    """
    # Load the video using moviepy
    video = VideoFileClip(input_video_path)
    

    zoom_factor = 0.4

    # Apply the zoom factor to the cropped video
    zoomed_width = int(video.size[0] / zoom_factor)
    zoomed_height = int(video.size[1] / zoom_factor)
    zoomed_video = crop(
        video,
        x_center=video.size[0] // 2,
        y_center=video.size[1] // 2,
        width=zoomed_width,
        height=zoomed_height
    ).resize(video.size)  # Resize back to the original cropped size

    # video dimensions
    width, height = zoomed_video.size
    # Calculate 5:4 aspect ratio dimensions
    target_aspect_ratio = 5 / 4
    if width / height > target_aspect_ratio:
        # Video is too wide, crop width
        target_width = int(height * target_aspect_ratio)
        x_center = width // 2
        x1 = x_center - target_width // 2
        x2 = x_center + target_width // 2
        cropped_video = crop(zoomed_video, x1=x1, x2=x2)
    else:
        # Video is too tall, crop height
        target_height = int(width / target_aspect_ratio)
        y_center = height // 2
        y1 = y_center - target_height // 2
        y2 = y_center + target_height // 2
        cropped_video = crop(zoomed_video, y1=y1, y2=y2)
    

    
    # Resize cropped video to fit within 5:4 in the center of a 9:16 canvas
    canvas_width = 1080
    canvas_height = 1920
    # cropped_resized_video = cropped_video_zoomed.resize(height=int(canvas_height * 4 / 5))

    # Extract frames and create a blurred background
    blurred_frames = []
    for frame in cropped_video.iter_frames(fps=cropped_video.fps, dtype="uint8"):
        # Convert frame to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Apply Gaussian blur
        blurred_frame_bgr = cv2.GaussianBlur(frame_bgr, (251, 251), 500)
        # Convert back to RGB
        blurred_frame_rgb = cv2.cvtColor(blurred_frame_bgr, cv2.COLOR_BGR2RGB)
        blurred_frames.append(blurred_frame_rgb)
    
    # Create a blurred video from the frames
    blurred_background = ImageSequenceClip(blurred_frames, fps=cropped_video.fps).resize((canvas_width, canvas_height))

    # Position the cropped and zoomed video in the center of the blurred background
    final_composite = CompositeVideoClip(
        [blurred_background, cropped_video.set_position("center")],
        size=(canvas_width, canvas_height)
    )

    # Write the output video
    final_composite.set_duration(video.duration).write_videofile(output_video_path, codec="libx264", audio_codec="aac")



def remove_silence(input_video_path, output_video_path):
    """
    Removes silence from a video file.

    Args:
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path to save the output video without silence.
    """
    try:
        # Step 1: Extract audio from the video
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")

            # Extract audio using ffmpeg
            os.system(f"ffmpeg -i {input_video_path} -q:a 0 -map a {temp_audio_path}")

            # Step 2: Load the audio file and detect silence
            audio = AudioSegment.from_file(temp_audio_path, format="wav")
            silence_ranges = silence.detect_silence(
                audio, min_silence_len=400, silence_thresh=-44
            )
            silence_ranges_seconds = [(start / 1000, end / 1000) for start, end in silence_ranges]

            # Step 3: Load the video and create subclips
            video = VideoFileClip(input_video_path)
            subclips = []
            start_time = 0
            for silence_start, silence_end in silence_ranges_seconds:
                if start_time < silence_start:
                    subclips.append(video.subclip(start_time, silence_start))
                start_time = silence_end
            if start_time < video.duration:
                subclips.append(video.subclip(start_time, video.duration))

            # Step 4: Concatenate subclips and save the output
            if subclips:
                final_video = concatenate_videoclips(subclips)
                final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
            else:
                print("No non-silent sections found. Saving original video.")
                video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    
    except Exception as e:
        print(f"An error occurred: {e}")




def crop_to_vertical(input_video_path, output_video_path):
    detect_faces_and_speakers(input_video_path, "DecOut.mp4")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(input_video_path, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    vertical_height = int(original_height)
    vertical_width = int(vertical_height * 9 / 16)
    print(vertical_height, vertical_width)


    if original_width < vertical_width:
        print("Error: Original video width is less than the desired vertical width.")
        return

    x_start = (original_width - vertical_width) // 2
    x_end = x_start + vertical_width
    print(f"start and end - {x_start} , {x_end}")
    print(x_end-x_start)
    half_width = vertical_width // 2

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (vertical_width, vertical_height))
    global Fps
    Fps = fps
    print(fps)
    count = 0
    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) >-1:
            if len(faces) == 0:
                (x, y, w, h) = Frames[count]

            # (x, y, w, h) = faces[0]  
            try:
                #check if face 1 is active
                (X, Y, W, H) = Frames[count]
            except Exception as e:
                print(e)
                (X, Y, W, H) = Frames[count][0]
                print(Frames[count][0])
            
            for f in faces:
                x1, y1, w1, h1 = f
                center = x1+ w1//2
                if center > X and center < X+W:
                    x = x1
                    y = y1
                    w = w1
                    h = h1
                    break

            # print(faces[0])
            centerX = x+(w//2)
            print(centerX)
            print(x_start - (centerX - half_width))
            if count == 0 or (x_start - (centerX - half_width)) <1 :
                ## IF dif from prev fram is low then no movement is done
                pass #use prev vals
            else:
                x_start = centerX - half_width
                x_end = centerX + half_width


                if int(cropped_frame.shape[1]) != x_end- x_start:
                    if x_end < original_width:
                        x_end += int(cropped_frame.shape[1]) - (x_end-x_start)
                        if x_end > original_width:
                            x_start -= int(cropped_frame.shape[1]) - (x_end-x_start)
                    else:
                        x_start -= int(cropped_frame.shape[1]) - (x_end-x_start)
                        if x_start < 0:
                            x_end += int(cropped_frame.shape[1]) - (x_end-x_start)
                    print("Frame size inconsistant")
                    print(x_end- x_start)

        count += 1
        cropped_frame = frame[:, x_start:x_end]
        if cropped_frame.shape[1] == 0:
            x_start = (original_width - vertical_width) // 2
            x_end = x_start + vertical_width
            cropped_frame = frame[:, x_start:x_end]
        
        print(cropped_frame.shape)

        out.write(cropped_frame)

    cap.release()
    out.release()
    print("Cropping complete. The video has been saved to", output_video_path, count)



def combine_videos(video_with_audio, video_without_audio, output_filename):
    try:
        # Load video clips
        clip_with_audio = VideoFileClip(video_with_audio)
        clip_without_audio = VideoFileClip(video_without_audio)

        audio = clip_with_audio.audio
        
        combined_clip = clip_without_audio.set_audio(audio)

        # global Fps
        combined_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac', fps=30 , preset='medium', bitrate='3000k')
        print(f"Combined video saved successfully as {output_filename}")
    
    except Exception as e:
        print(f"Error combining video and audio: {str(e)}")



if __name__ == "__main__":
    input_video_path = r'short.mp4'
    output_video_path = 'Croped_output_video.mp4'
    combined_video_path = 'combined_video_with_audio.mp4'
    final_video_path = 'final_video_with_audio.mp4'
    # detect_faces_and_speakers(input_video_path, "DecOut.mp4")
    # zoom_with_blur(input_video_path, output_video_path)
    # combine_videos(input_video_path, output_video_path, combined_video_path)
    remove_silence(combined_video_path, final_video_path)



