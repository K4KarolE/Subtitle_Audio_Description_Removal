<div align="center">
    <img src="https://github.com/user-attachments/assets/2e112dd8-c815-4e1a-a766-5a1842c0dc44">
</div>


### Subtitle Extractor
- Once the video file is added, the available subtitles are displayed in the roll-down menu / combo box, hitting the
"Extract Sub / Open Folder" button extracts the selected subtitle to the same folder as the source video file


### Subtitle Audio Description Removal
- Removes the audio description like [Horns honking in distance], (Indistinct conversations) from the subtitles
- `Select Subtitle - Single Sub`
    - Able to select an `.srt` file
    - Typically ideal for movies
- `Select Directory - Multiple Subs`
    - In the added directory and in the subdirectories all the `.srt` files will be transformed
    - Typically ideal for series, TV shows
- Once the file or folder selected, the transformation and the result listing are triggered automatically
- The new subtitle is saved in the same folder of the original subtitle
- Double clicking in the result list:
    - Opens the directory of the selected subtitle in `File Explorer`


## Requirements
### Python 3 - used: 3.11.5
- https://www.python.org/

### Install dependencies
``` pip install -r requirements.txt ```

#### FFmpeg [(link)](https://ffmpeg.org/) - For subtitle extraction
- WINDOWS
    - If `FFmpeg` is not added to the system path:
        - You are able to add the path of the `ffmpeg.exe` in the `Settings` window
    - [Install FFmpeg on Windows 10/11](https://windowsloop.com/install-ffmpeg-windows-10/)
- LINUX
    - Via `Software Manager`

### OS
- Tested on Windows 11 / Linux Mint 22

## Thank you all who worked on the modules used in this project!
