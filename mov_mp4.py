import ffmpeg
input_file = 'Screen_Recording_Hindi_final_video.mov'
output_file = 'Screen_Recording_final_hindi.mp4'

ffmpeg.input(input_file).output(output_file, vcodec='libx264', acodec='aac').run()
