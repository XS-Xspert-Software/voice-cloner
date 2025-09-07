import resemble

client = resemble.Client("YqNHCM01QEFvp9L5J8bp7Qtt")

# Create a new voice
voice = client.create_voice("Voice Name", "path_to_audio.wav")

# Generate speech with the cloned voice
audio = voice.speak("Hello, this is a cloned voice.")

# Save the audio to a file
with open("output.wav", "wb") as f:
    f.write(audio)
