from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_API")
)

if not client.api_key:
    raise ValueError("API key not found. Make sure it is defined in the .env file.")


# Function to extract start and end times
# def extract_times(json_string):
#     try:
#         # Parse the JSON string
#         data = json.loads(json_string)

#         # Extract start and end times as floats
#         start_time = float(data[0]["start"])
#         end_time = float(data[0]["end"])

#         # Convert to integers
#         start_time_int = int(start_time)
#         end_time_int = int(end_time)
#         return start_time_int, end_time_int
#     except Exception as e:
#         print(f"Error in extract_times: {e}")
#         return 0, 0

def extract_times(json_string):
    try:
        # Parse the JSON string
        data = json.loads(json_string)

        # Ensure data is a list of elements
        if not isinstance(data, list):
            raise ValueError(f"JSON input is not a list {data}")

        # Extract start and end times for all elements
        times = []
        for item in data:
            if "start" in item and "end" in item:
                start_time = float(item["start"])
                end_time = float(item["end"])
                times.append((int(start_time), int(end_time)))
            else:
                print(f"Skipping invalid item: {item}")

        return times
    except Exception as e:
        print(f"Error in extract_times: {e}")
        return []
# {
# start: "Start time of the clip",
# content: "Highlight Text",
# end: "End Time for the highlighted clip"
# }
# Provide continues clips these will then be cut from the video and uploaded as a youtube shorts as a video. 
# Find a minimum of 2 clips per user Transcription.


system = """
You are a social media expert specializing in editing short form, viral content for youtube.

Based on the whole Transcription user provides identify the main most interesting parts off the video that will be the most viral.
The clips must be entertaining interesting engaging. Output the time stamps for the start and end of the clips.

Difference between start and end times is 50 to 59 seconds

Find 1 clip

Do not include any explanations, only provide a  RFC8259 compliant JSON response  following this format without deviation.
[{
title: "SEO optimized Title of the clip ending with ... Emojies",
description: "SEO optimized description of clip",
hashtags: "4 SEO optimized hashtags of clip", 
start: "Start time of clip",
end: "End Time for clip"
}]

"""

TestTranscript = """
0.0 - 22.62:  What do you think of this flying vehicle Morty I built it out of stuff I found in the garage22.62 - 25.220000000000002:  Yeah, Rick. It's it's great. Is this the surprise?25.220000000000002 - 33.08:  Morty, I had to I had to make a bomb Morty. I had to create a bomb. I'm gonna drop it down there33.08 - 39.48:  Get a little fresh dark. Create a whole fresh start. That's absolutely crazy. Come on Morty. Just take it easy. Morty's gonna be good39.879999999999995 - 44.96:  Right now. We're gonna go pick up your little friend Jessica. Jessica from my math class. I'm gonna drop the bomb44.96 - 49.56:  You know, I want you to have somebody, you know, I want you to have the thing49.56 - 52.160000000000004:  I'm gonna make it like a new Adam and Eve and you're gonna be Adam52.96 - 54.96:  Jessica's gonna be Eve54.96 - 56.96:  That's a surprise. No you can't56.96 - 61.36:  Jessica doesn't even know I exist, but forget about that because you can't blow up your hand.61.36 - 62.96:  I get what you're trying to say, Morty.62.96 - 67.36:  Listen, I'm not, you don't got to worry about me trying to fool around with Jessica.67.36 - 71.6:  Let's round with Jessica or anything. I'm not that kind of guy. What are you talking about Rick?71.6 - 74.28:  You have to worry about me getting them Jessica or anything75.84 - 77.84:  She's all for you79.2 - 81.2:  You're a morty, right97.36 - 99.36:  Right right right right right right99.36 - 103.64:  A land a land a land a land a land a thing a thing a tough guy all of a sudden107.6 - 109.6:  Right here right here110.96 - 114.9:  You know what that was all testimony just elaborate114.9 - 119.46000000000001:  elaborate test to make you more assertive it was sure why not I don't know144.9 - 146.9:  I160.74 - 166.26:  See there's a new episode of that singing show tonight. Who do you guys think is gonna be the best singer?166.26 - 170.4:  Oh my god as hot as it is food. I'm going to puke. Goodie. Are you getting sick?170.4 - 175.58:  I told you not to practice kiss the living room pillow with the dog sleeps on it. I wasn't kissing a pillow mom175.58 - 180.42000000000002:  I just I didn't get a lot of sleep last night. Maybe my dreams were just too loud or something180.42000000000002 - 182.82000000000002:  Or maybe you were out on it again with Grandpa Rick.182.82000000000002 - 183.32000000000002:  What?183.32000000000002 - 184.12:  Dad?184.12 - 186.42000000000002:  What, so everyone's supposed to sleep every single night now?186.42000000000002 - 189.02:  You realize that nighttime makes up half of all time?189.02 - 189.62:  What?189.62 - 190.22000000000003:  Jerry!190.22000000000003 - 190.72000000000003:  Beth!190.72 - 192.72:  It's like I'm a bird, just so that I want to die.192.72 - 194.02:  There is no god-somer.194.02 - 196.02:  Gotta rip that band-aid off now, you'll thank me later.196.02 - 198.02:  Okay, with all due respect, Rick.198.02 - 200.18:  What am I talking about? What respect does do?200.18 - 202.66:  How is my son supposed to pass his classes?202.66 - 206.3:  If you keep dragging him off for a high concept sci-fi rigamarole.206.3 - 208.96:  Listen, Jerry, I don't want to overstep my bounds or anything.208.96 - 213.76000000000002:  It's your house. It's your world. You're a real Julius Caesar, but I'll tell you how I feel about school, Jerry
"""


def GetHighlight(Transcription):
    print("Getting Highlight from Transcription ")
    print(Transcription)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": TestTranscript + "\n The JSON response:"},
            ],
        )

        json_string = response.choices[0].message.content
        json_string = json_string.replace("json", "")
        json_string = json_string.replace("```", "")
        print(json_string)
        # input("REVIEW MODEL REPLY")

        # print(json_string)
        times = extract_times(json_string)
        return times
        # if Start == End:
        #     Ask = input("Error - Get Highlights again (y/n) -> ").lower()
        #     if Ask == "y":
        #         Start, End = GetHighlight(Transcription)
        # return Start, End
    except Exception as e:
        print(f"Error in GetHighlight: {e}")
        return 0, 0


if __name__ == "__main__":
    print(GetHighlight(User))
