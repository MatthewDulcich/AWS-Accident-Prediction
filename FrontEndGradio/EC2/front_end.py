import os
import time
import threading
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import gradio as gr
import FrontEndGradio.EC2.track_s3_predictions as tsp
import FrontEndGradio.EC2.get_video_bucket as gbucket
import subprocess
# Paths to watch
CSV_FILE_PATH = "./master.csv"
VIDEO_FOLDER_PATH = "./videos/"
AVI_VIDEO_PATH ="./avi_videos/"

# Queue to store new video files
video_queue = Queue()

#dataframe created from the master file
df = pd.read_csv(CSV_FILE_PATH)

# Watchdog handler for CSV file changes
class CSVChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global df
        if event.src_path.endswith("master.csv"):
            print("master.csv updated. Reloading DataFrame...")
            try:
                # Reload the DataFrame
                updated_df = pd.read_csv(CSV_FILE_PATH)
                df[:] = updated_df  # Update in-place for Gradio sync
            except Exception as e:
                print(f"Error updating DataFrame: {e}")

# Watchdog handler for new video files
class VideoEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.mp4'):
            print(f"New video detected: {event.src_path}")
            video_queue.put(event.src_path)  # Add new video to the queue
    def on_modified(self, event):
        if event.src_path.endswith("new_video.mp4"):
            print("new_video.mp4 updated. Reloading DataFrame...")
            try:
                video_queue.put(event.src_path)
            except Exception as e:
                print(f"Error updating DataFrame: {e}")
# Watchdog handler for new video files
class AVIVideoEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.avi'):
                try:
                    # FFmpeg command to convert AVI to MP4
                    print(event.src_path)
                    print(event.src_path.split('/')[-1])
                    output_path = event.src_path.replace("avi_", "")
                    output_path =output_path.replace("avi", "mp4")
                    print(output_path)
                    command = [
                        'ffmpeg',
                        '-i', event.src_path,  # Input file
                        '-c:v', 'libx264', # Video codec
                        '-preset', 'fast', # Encoding speed
                        '-crf', '23',      # Quality level (lower is better, range: 0-51)
                        '-c:a', 'aac',     # Audio codec
                        '-b:a', '192k',    # Audio bitrate
                        '-movflags', '+faststart',  # Enable progressive playback
                        output_path,
                        "-y"
                    ]

                    # Run the command as a subprocess
                    subprocess.run(command, check=True)
                    print(f"Conversion successful: {output_path}")

                except subprocess.CalledProcessError as e:
                    print(f"Error during conversion: {e}")
                except FileNotFoundError:
                    print("FFmpeg not found. Ensure it is installed and in your PATH.")
# Function to monitor the video queue and play videos in Gradio
def video_player():
    while True:
        # Wait until a video is available in the queue
        video_path = video_queue.get()
        print(video_path)
        if video_path:
            yield video_path  # Gradio will display the video
        time.sleep(1)

#FOLDER WATCHER
# Function to start the watchdog observer
def start_watchdog():
    csv_handler = CSVChangeHandler()
    video_handler = VideoEventHandler()
    avi_video_handler = AVIVideoEventHandler()
    observer = Observer()
    # Watch the CSV file
    observer.schedule(csv_handler, path=os.path.dirname(CSV_FILE_PATH), recursive=False)
    # Watch the video folder
    observer.schedule(video_handler, path=VIDEO_FOLDER_PATH, recursive=False)

    observer.schedule(avi_video_handler, path = AVI_VIDEO_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


### PLOT FUNCTIONS
def update_scatter_plot(x_axis, y_axis):
    #print(dir(dataframe))
    yield gr.ScatterPlot(
        df,
        x = x_axis,
        y = y_axis,
        title = f"{x_axis} vs {y_axis}"
    )

column_options = df.columns.to_list()
# Function to run Gradio interface
with gr.Blocks() as demo:
        #VIDEO ELEMENTS
        video = gr.Video(autoplay=True, interactive = False)
        inter = gr.Interface(fn=video_player, inputs=[], outputs=video, concurrency_limit =None)

        ##DATA ELEMENTS
        dataframe = gr.Dataframe(headers=df.columns.tolist(), visible = False)
        #timer to refresh the dataframe every 5 seconds
        refresh_df_timer = gr.Timer(value = 1)
        refresh_df_timer.tick(fn = lambda: df, outputs = dataframe)
        pred_file_timer = gr.Timer(value = 1)
        pred_file_timer.tick(fn =tsp.main, outputs = None)
        #bucket_timer = gr.Timer(value =1)
        #bucket_timer.tick(fn =gbucket.check_new_files, outputs = None)
        #CSV CHECKER
        x_axis = gr.Dropdown(choices =column_options, label="X axis", value = column_options[0])
        y_axis = gr.Dropdown(choices =column_options, label = "Y axis", value = column_options[0])
        scatter = gr.ScatterPlot(df, x="n_cars", y="score")
        #Update the scatter plot when the dropdown changes
        #update the plots when the dataframe changes
        dataframe.change(fn=update_scatter_plot, inputs = [x_axis, y_axis], outputs = scatter)
        x_axis.change(update_scatter_plot, inputs =[x_axis, y_axis], outputs =scatter, concurrency_limit = None)
        y_axis.change(update_scatter_plot, inputs =[x_axis, y_axis], outputs =scatter, concurrency_limit = None)

# Main function to start the program
def main():
    # Start watchdog in a separate thread
    watchdog_thread = threading.Thread(target=start_watchdog, daemon=True)
    watchdog_thread.start()

    # Run Gradio in the main thread
    demo.launch(server_name = "0.0.0.0")
    #demo.launch()

if __name__ == "__main__":
    main()

