import os
import PIL
import PIL.Image
from dotenv import load_dotenv

from moviepy.config import change_settings
from moviepy.video.tools.subtitles import SubtitlesClip, file_to_subtitles
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.all import crop, resize

load_dotenv()  # take environment variables from .env.

def adjust_subtitle_times(subs, reduction_factor=0.8):
    adjusted_subs = []
    for times, text in subs:
        start, end = times
        new_end = start + (end - start) * reduction_factor
        adjusted_subs.append(([start, new_end], text))
    return adjusted_subs

def __ends_with_punctuation(s):
    return s.endswith(('.', ',', '!', '?'))

def convert_ms_to_sec(milliseconds):
    return float(float(milliseconds) / 1000)

def format_string(string_arr):
    count_char = 0
    output_string = ""
    for foo in string_arr:
        count_char += len(foo)
        if count_char > 9:
            count_char = len(foo)
            output_string = f"{output_string}\n{foo}"
        else:
            output_string = f"{output_string} {foo}"
    return output_string.strip(",.?! ")

def construct_subtitles(mutters, time_slice=700):
    """ For individual mutters in utters, Slice in millisecs"""
    mutters_arr = []
    muttered_sentence_arr = []
    start_time = 0
    for word in mutters:
        muttered_sentence_arr.append(word.text)
        if start_time == 0:
            start_time = word.start
        end_time = word.end
        if (end_time - start_time) > time_slice or __ends_with_punctuation(word.text):
            mutters_arr.append(([convert_ms_to_sec(start_time), convert_ms_to_sec(end_time)], format_string(muttered_sentence_arr)))
            muttered_sentence_arr = [] 
            start_time = 0
            end_time = 0
    return mutters_arr #, mutters.speaker   

def forge_subtitles_to_video(speaker_arr): #subs_file="subs.srt"
    myvideo = (VideoFileClip("Wild_Election_Results.mp4"))
    generator = lambda txt: TextClip(txt, font="Cooper-Black", fontsize=120, color='Yellow', stroke_color='black', stroke_width=7)
    sub = (SubtitlesClip(speaker_arr, generator)
           .set_position(("center", "center")))
    # water_mark = (ImageClip("PATH_TO_IMAGE")
    #               .set_position(("right", "top"))
    #               .set_opacity(0.5))
    subscribe = (ImageClip("subscribe.png")
                 .set_position(("center", "bottom"))
                 .set_start(myvideo.duration-1.5)
                 .set_duration(1.5)
                 .resize(0.25))
    
    # Apply shorts resolution
    (w, h) = myvideo.size
    crop_width = h * 9/16
    # x1,y1 is the top left corner, and x2, y2 is the lower right corner of the cropped area.
    x1, x2 = (w - crop_width)//2, (w+crop_width)//2
    y1, y2 = 0, h
    cropped_clip = crop(myvideo, x1=x1, y1=y1, x2=x2, y2=y2)
    # subscribe_resized = resize(subscribe, 0.5)
    # or you can specify center point and cropped width/height
    # cropped_clip = crop(clip, width=crop_width, height=h, x_center=w/2, y_center=h/2)

    final = CompositeVideoClip([cropped_clip, sub, subscribe]) # Can set position as a % e.g. 
    final.write_videofile("final.mp4", fps=myvideo.fps)

def subtitle_forgery(video_file_path):
    video_file_path=r"C:\Users\William\Documents\GitHub\Mustafar\Wild_Election_Results.mp4"
    words = generate_subtitles(video_file_path)
    stiched_subtitles = construct_subtitles(words)
    # print(stiched_subtitles) 
    # stiched_subtitles = [([0.96, 1.54], 'Wow'), ([4.334, 5.214], 'To be fair'), ([5.294, 6.19], 'the IfB'), ([6.302, 7.714], 'did hold\nstrong'), ([8.094, 9.07], 'They held\nstrong'), ([9.142, 10.064], 'because\nthe ancient')]
    forge_subtitles_to_video(stiched_subtitles)


def main():
    subtitle_forgery(None)

if __name__=='__main__':
    main()