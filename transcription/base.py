# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence

from moviepy.editor import VideoFileClip

def extract_audio_from_video(input_video, output_audio):
    try:
        video_clip = VideoFileClip(input_video)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio, codec='pcm_s16le')
        audio_clip.close()
        video_clip.close()
        print("Audio extraction successful!")
    except Exception as e:
        print("Error occurred:", str(e))


# create a speech recognition object
r = sr.Recognizer()

# recognize speech in the audio file
def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened)
    return text

# this function splits the audio file into chunks on silence
# and applies speech recognition
def get_large_audio_transcription_on_silence(path):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text += text
    # return the text for all chunks detected
    return whole_text


if __name__ == "__main__":
    input_video_path = "test.mp4"  # Replace with the path to your input MP4 video file
    output_audio_path = "output_audio.wav"  # Replace with the desired path for the output WAV audio file
    extract_audio_from_video(input_video_path, output_audio_path)
    path = output_audio_path
    print("\nFull text:", get_large_audio_transcription_on_silence(path))