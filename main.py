# from Components.YoutubeDownloader import download_youtube_video
import tempfile
import os
from Components.LocalImport import process_video_file
from Components.Edit import extractAudio, crop_video
from Components.Transcription import transcribeAudio
from Components.LanguageTasks import GetHighlight
from Components.FaceCrop import crop_to_vertical, combine_videos, remove_silence, zoom_with_blur

# url = input("Enter YouTube video URL: ")
# Vid= download_youtube_video(url)
Vid = process_video_file("input/Rick and Morty S01E01 Pilot.mkv")
print(Vid)
if Vid:
    Vid = Vid.replace(".webm", ".mp4")
    print(f"Downloaded video and audio files successfully! at {Vid}")

    Audio = extractAudio(Vid)
    if Audio:

        transcriptions = transcribeAudio(Audio)
        if len(transcriptions) > 0:
            TransText = ""

            for text, start, end in transcriptions:
                TransText += (f"{start} - {end}: {text}")
            
            times = GetHighlight(TransText)  # GetHighlight should now return a list of (start, stop) tuples

            if times:
                try: 
                    for i, (start, stop) in enumerate(times):
                        if start != 0 and stop != 0:
                            final_clip = f"Final_{i + 1}.mp4"
                            with tempfile.TemporaryDirectory() as temp_dir:
                                print(f"Processing clip {i + 1}: Start: {start}, End: {stop}")

                                # Generate unique output filenames for each step to avoid overwriting
                                output_clip = os.path.join(temp_dir, f"Out_{i + 1}.mp4")
                                cropped_clip = os.path.join(temp_dir, f"cropped_{i + 1}.mp4")
                                combined_clip = os.path.join(temp_dir, f"combined_{i + 1}.mp4")


                                # Crop the video to the highlight
                                crop_video(Vid, output_clip, start, stop, transcriptions)
                                input("Editing done check")
                                # Crop the video to vertical format with blur and zoom
                                zoom_with_blur(output_clip, cropped_clip)

                                # Combine the original cropped clip with the vertical version
                                combine_videos(output_clip, cropped_clip, combined_clip)

                                # Removed Silence 
                                remove_silence(combined_clip, final_clip)

                                print(f"Finished processing clip {i + 1}: {final_clip}")
                        else:
                            print(f"Skipping invalid time range for clip {i + 1}: Start: {start}, End: {stop}")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print("Error in getting highlights or no valid highlights found.")

            # start , stop = GetHighlight(TransText)
            # if start != 0 and stop != 0:
            #     print(f"Start: {start} , End: {stop}")

            #     Output = "Out.mp4"

            #     crop_video(Vid, Output, start, stop)
            #     croped = "croped.mp4"

            #     crop_to_vertical("Out.mp4", croped)
            #     combine_videos("Out.mp4", croped, "Final.mp4")
            # else:
            #     print("Error in getting highlight")
        else:
            print("No transcriptions found")
    else:
        print("No audio file found")
else:
    print("Unable to Download the video")