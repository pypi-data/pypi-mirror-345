import time
import fpstimer
from playsound import playsound
import cursor
from vid_info import vid_info
from to_ascii import to_ascii
from pydub import AudioSegment
import os
import tempfile

"""ANSI COLOR CODES"""
Red = "\u001b[31m"
Green = "\u001b[32m"
Cyan = "\u001b[36m"
Reset = "\u001b[m"
Reset_cursor = "\u001b[H"

def main(args):

    """Store terminal arguments to variables"""
    scale_num = args.downscale
    colored_frames = args.colored
    play_audio = args.audio
    audio_file_name = "video_audio.mp3"
    chars_list = [args.characters[char] for char in range(len(args.characters))]
    video = args.video_path
    realtime = args.realtime

    try:
        print(f"{Reset_cursor}~~~ Terminal Video Player ~~~\n{Green}Video file detected: {video}.{Reset}")
        video_audio = AudioSegment.from_file(video, "mp4")

    except FileNotFoundError:
        print(f"{Reset_cursor}~~~ Terminal Video Player ~~~\n{Red}Couldn't find video file '{video}'.{Reset}")
        input("Press Enter to Exit")
        exit()

    if play_audio:

        print(f"{Cyan}Generating audio ...{Reset}")
        directory = tempfile.TemporaryDirectory()
        mp3_file_path = os.path.join(directory.name, str(audio_file_name + ".mp3"))
        video_audio.export(mp3_file_path, format="mp3")
        print(f"{Green}Audio Generated!{Reset}")

    cursor.hide()
    frame_info = vid_info(video)
    FPS = frame_info.get_framerate() #Get the video's framerate
    TOTAL_FRAMES = int(frame_info.get_framecount()) #Get the video's total number of frames
    timer = fpstimer.FPSTimer(FPS) #Set the script's framerate to video's framerate
    print("\u001b[2J")

    if realtime:
        input(f"{Reset_cursor}Press Enter to start the playback")
        print("\u001b[2J")

        if play_audio:
            playsound(mp3_file_path, block=False)

        for frame_number in range(TOTAL_FRAMES):
            start = time.perf_counter()

            image = frame_info.get_frame(frame_number)
            frame = to_ascii(image, scale_num, chars_list=chars_list)
                
            if colored_frames:
                frame = frame.asciify_colored()
                
            else:
                frame = frame.asciify()

            print(Reset_cursor + frame + Reset)
            timer.sleep()
            fps = 1 // (time.perf_counter() - start)
            print(f"FPS: {fps}")

    else:

        rendered_result = []
        start = time.time()
        
        for frame_number in range(TOTAL_FRAMES):

            image = frame_info.get_frame(frame_number)
            frame = to_ascii(image, scale_num, chars_list=chars_list)
                
            if colored_frames:
                frame = frame.asciify_colored()
                
            else:
                frame = frame.asciify()

            rendered_result.append(frame)
            print(f"{Reset_cursor}{Cyan}Rendering frames: {frame_number}/{TOTAL_FRAMES} | Elapsed time: {int(time.time() - start)}s{Reset}")

        print(f"{Green}Successfully rendered {TOTAL_FRAMES} frames in {int(time.time() - start)}s.{Reset}")
        input("Press Enter to start the playback")
        print("\u001b[2J")

        if play_audio:
            playsound(mp3_file_path, block=False)

        for frame in rendered_result:
            start = time.perf_counter()
            print(Reset_cursor + frame + Reset)
            timer.sleep()
            fps = 1 // (time.perf_counter() - start)
            print(f"FPS: {fps}")


    cursor.show()
    print(f"{Reset_cursor}{Green}Video Playback finished successfully.{Reset}\u001b[0J")
    input("Press Enter to Exit")
    exit()


"""Make ANSI Escape Codes work on Windows"""
if os.name == "nt":
    os.system("cls")

"""Create terminal arguments"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("video_path", help="The video to asciify <path>")
parser.add_argument("downscale", help="How many times to downscale the frames (integer)", type=int)
parser.add_argument("-a", "--audio", help="Play video audio", action="store_true")
parser.add_argument("-c", "--colored", help="Colored output", action="store_true")
parser.add_argument("-chars", "--characters", help="Custom characters(low density to high)", default=[' ', 's', '#', '$','@'])
parser.add_argument("-rt", "--realtime", help="Play video audio", action="store_true")
args = parser.parse_args()

main(args)