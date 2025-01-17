import os
import ffmpeg

def process_video_file(file_path):
    try:
        if not os.path.exists('processed_videos'):
            os.makedirs('processed_videos')

        output_file = os.path.join('processed_videos', f"processed_{os.path.basename(file_path)}")
        if os.path.exists(output_file):
            print("File exists")
            return output_file
        print(f"Processing video: {file_path}")
        stream = ffmpeg.input(file_path)
        stream = ffmpeg.output(stream, output_file, vcodec='libx264', acodec='aac', strict='experimental')
        ffmpeg.run(stream, overwrite_output=True)

        print(f"Processed video saved at: {output_file}")
        return output_file
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e.stderr.decode()}")
        raise

if __name__ == "__main__":
    input_folder = input("Enter the path to the folder containing video files: ")
    
    if not os.path.isdir(input_folder):
        print("Invalid folder path. Please try again.")
        exit(1)

    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]

    if not video_files:
        print("No video files found in the specified folder.")
        exit(1)

    print("Available video files:")
    for i, file in enumerate(video_files):
        print(f"{i}. {file}")

    choice = int(input("Enter the number of the video file to process: "))
    if choice < 0 or choice >= len(video_files):
        print("Invalid choice. Exiting.")
        exit(1)

    selected_file = os.path.join(input_folder, video_files[choice])
    process_video_file(selected_file)
