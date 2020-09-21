import ffmpeg

input = ffmpeg.input('in.mp4')
out = ffmpeg.output(stream1=input.audio, filename='out.wav', format='wav')