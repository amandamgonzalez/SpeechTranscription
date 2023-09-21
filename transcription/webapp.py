from flask import Flask, render_template, request, redirect, url_for
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from moviepy.editor import VideoFileClip

app = Flask(__name__)

# function to extract audio from video
def extract_audio_from_video(input_video, output_audio):
    try:
        video_clip = VideoFileClip(input_video)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio, codec='pcm_s16le')
        audio_clip.close()
        video_clip.close()
        print("audio extraction successful!")
    except Exception as e:
        print("error occurred:", str(e))

# function to transcribe audio using speech recognition
r = sr.Recognizer()
def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened)
    return text

# function to split audio into chunks on silence and apply speech recognition
# since is hard to procress it all at once, is better to break it down
def get_large_audio_transcription_on_silence(path):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more to get chunks
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
            print("error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text += text
    # return the text for all chunks detected
    return whole_text

# route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # check if a file was uploaded
        if "video_file" in request.files:
            video_file = request.files["video_file"]
            if video_file.filename == "":
                return redirect(request.url)

            # save the uploaded video file temporarily
            temp_video_path = "temp_video.mp4"
            video_file.save(temp_video_path)

            # extract audio from the video and get transcribed text
            output_audio_path = "output_audio.wav"
            extract_audio_from_video(temp_video_path, output_audio_path)
            transcribed_text = get_large_audio_transcription_on_silence(output_audio_path)

            # delete the temporary video and audio files
            os.remove(temp_video_path)
            os.remove(output_audio_path)

            # display the transcribed text to the user
            return render_template("result.html", text=transcribed_text)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)