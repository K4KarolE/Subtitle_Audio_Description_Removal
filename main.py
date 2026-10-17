
from pathlib import Path
import os
import shutil
import subprocess
import sys

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget
)

os_linux: bool = (sys.platform == 'linux')
if os_linux: QApplication.setDesktopSettingsAware(False)


class MyMessageBoxError(QMessageBox):
    def __init__(self, tab_title, message):
        super().__init__()
        self.setWindowTitle(f'ERROR - {tab_title}')
        self.setIcon(QMessageBox.Icon.Warning)
        # extra whitespace:
        # position the text more to the middle in the box
        self.setText(message + ' ' * 8)
        self.setStandardButtons(QMessageBox.StandardButton.Close)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Sheet)
        self.exec()


class VarPass:
    def __init__(self):
        self.vid_path = None
        self.vid_title = None
        self.sub_tracks_list = []
        self.audio_tracks_amount = ''
vr = VarPass()


app = QApplication(sys.argv)

window = QWidget()
window_width, window_height = 650, 250
screen = QApplication.screenAt(window.pos())
screen_rect = screen.availableGeometry()
pos_x = screen_rect.x() + int((screen_rect.width() - window_width) / 2)
pos_y = screen_rect.y() + int((screen_rect.height() - window_height) / 2)
window.setGeometry(pos_x, pos_y, window_width, window_height)
window.setWindowIcon(QIcon(str(Path(Path(__file__).parent, 'docs/icon.png'))))
window.setWindowTitle("Subtitle Guru")

listWidget = QListWidget()
sub_dic = {}
CONFIRMATION_TEXT = 'AUDIO DESC. REMOVED'
is_ffmpeg_installed: str = shutil.which("ffmpeg")


""" 
#################################
    AUDIO DESCRIPTION REMOVAL      
#################################
"""
''' SINGLE SUB '''
def button_single_subtitle_clicked():
    dialog_add_subtitle = QFileDialog()
    dialog_add_subtitle.setWindowTitle("Select an SRT file")
    dialog_add_subtitle.setNameFilter("SRT files (*.srt)")
    dialog_add_subtitle.exec()
    if dialog_add_subtitle.result():
        sub_path = dialog_add_subtitle.selectedFiles()[0]
        grouped_actions(sub_path, CONFIRMATION_TEXT)


''' MULTIPLE SUBS - ALL SUBS IN THE GIVEN DIRECTORY AND IT`S SUBDIRECTORIES '''
def button_bulk_subtitle_clicked():
    dialog_add_directory = QFileDialog()
    dialog_add_directory.setFileMode(QFileDialog.FileMode.Directory)
    dialog_add_directory.setWindowTitle("Select a directory")
    dialog_add_directory.exec()
    if dialog_add_directory.result():
        for dir_path, dir_names, file_names in os.walk(dialog_add_directory.selectedFiles()[0]):
            bulk_subs(dir_path, file_names)


def bulk_subs(dir_path, file_names):
    for file in file_names:
        if file[-4:] == '.srt':
            sub_path = Path(dir_path, file)
            grouped_actions(sub_path, CONFIRMATION_TEXT)


''' NAMING / REMOVAL / LISTING '''
def grouped_actions(sub_path, CONFIRMATION_TEXT):
    sub_name = Path(sub_path).stem
    if CONFIRMATION_TEXT in sub_name:
        sub_list_name = f'{sub_name} \u2713'    # \u2713 = check mark
        sub_new_name = f'{sub_name}.srt'
    else:
        sub_list_name = f'{CONFIRMATION_TEXT} - {sub_name} \u2713'
        sub_new_name = f'{CONFIRMATION_TEXT} - {sub_name}.srt'
    try:
        sub_ad_removal(sub_path, sub_list_name, sub_new_name)
        QListWidgetItem(sub_list_name, listWidget)
    except:
        sub_list_name = f'{sub_name} - ERROR \u2573'
        QListWidgetItem(sub_list_name, listWidget)


''' AUDIO DESCRIPTION REMOVAL  '''
def sub_ad_removal(sub_path, sub_list_name, sub_new_name): 
    parent_directory = Path(sub_path).parent
    file = open(sub_path, mode='r', encoding='utf-8', errors='ignore')  # avoiding text encoding errors
    newFile = open(Path(parent_directory, sub_new_name), mode='w', encoding='utf-8')
    sub_dic[sub_list_name] = parent_directory
    
    fileList = list(file)
    slicedList = []
    words_to_remove = []
    rows_to_remove = []
    spec_char_look_for = '( ) [ ]'.split()

    for i in range(len(fileList)):    
        sliced = fileList[i].split()   
        slicedList.append(sliced)

    ''' 
        Removing the whole row/line containing
        audio description like: "(CHAINS RATTLING)"
    '''
    for row in slicedList:
        for word in row:
            if ('(' in word and ')' not in word or
                    '[' in word and ']' not in word):
                rows_to_remove.append(row)
    
    for _ in rows_to_remove:
        slicedList.remove(_)
    rows_to_remove.clear()

              
    ''' 
        Removing one word commentary from line like:
        "(SCOFFS) Don't be ridiculous."
    '''
    for row_index, row in enumerate(slicedList):
        for word in row:
            if (any(spec_char in spec_char_look_for[:2] for spec_char in word) or
                any(spec_char in spec_char_look_for[2:] for spec_char in word)) :     
                words_to_remove.append([row_index, word])

    for _ in words_to_remove:
        row_index, word = _[0], _[1]
        slicedList[row_index].remove(word)

        '''
            5
            00:00:51,079 --> 00:00:54,449
            -
                        to
            5
            00:00:51,079 --> 00:00:54,449

         '''
        if len(slicedList[row_index]) == 1:
            word_or_symbol = slicedList[row_index][0]
            if len(word_or_symbol) == 1 and not word_or_symbol.isdecimal():
                rows_to_remove.append(slicedList[row_index])
    for _ in rows_to_remove:
        slicedList.remove(_)
    

    ''' File compiling '''
    for i in slicedList:             
        newFile.writelines(' '.join(i))
        newFile.write('\n')              
    
    file.close()
    newFile.close()


''' OPEN THE SUB`S DIRECTORY '''
def open_directory(file_path = None):
    """
        Linux Mint 22.3 x86_64, "python-nemo" need to be removed via "Software manager" / ..
        Otherwise, running the app
            - Via source code: error message (below) still opens the folder
            - Via packaged and installed: not opens the folder, no error message

        ImportError: could not import gobject (error was: ModuleNotFoundError("No module named 'gi'"))
        ** (nemo:34862): WARNING **: 18:53:10.122: pygobject initialization failed
        ** (nemo:34862): WARNING **: 18:53:10.122: nemo_python_init_python failed
        """
    if file_path:
        file_dir_path = Path(file_path).parent
    else:
        file_dir_path = sub_dic[listWidget.currentItem().text()]
    if Path(file_dir_path).is_dir():
        if os_linux:
            subprocess.Popen(["xdg-open", file_dir_path])
        else:
            subprocess.Popen(["explorer", file_dir_path])
    else:
        MyMessageBoxError("File path", "Was not able to open file's directory.")

listWidget.itemDoubleClicked.connect(lambda : open_directory())


""" LABEL """
label_desc_removal_section_title = QLabel('Audio Description Removal')
label_desc_removal_section_title.setFont(QFont('Times', 14, 500))
label_desc_removal_section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

''' BUTTONS '''
button_single_subtitle = QPushButton(window, text='Select Subtitle - Single Sub')
button_single_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_single_subtitle.clicked.connect(button_single_subtitle_clicked)
button_single_subtitle.setFont(QFont('Times', 12, 500))

button_bulk_subtitle = QPushButton(window, text='Select Directory - Multiple Subs')
button_bulk_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_bulk_subtitle.clicked.connect(button_bulk_subtitle_clicked)
button_bulk_subtitle.setFont(QFont('Times', 12, 500))




""" 
############################
    SUBTITLE EXTRACTION      
############################
"""
""" COMBO BOX"""
sub_tracks_combo_box = QComboBox()
sub_tracks_combo_box.setFont(QFont('Times', 11, 500))
sub_tracks_combo_box.setEditable(True)
sub_tracks_combo_box.lineEdit().setAlignment(Qt.AlignmentFlag.AlignRight)
sub_tracks_combo_box.lineEdit().setReadOnly(True)
sub_tracks_combo_box.addItem('No video file is selected')

""" LABEL """
label_sub_ext_section_title = QLabel('Subtitle Extraction')
label_sub_ext_section_title.setFont(QFont('Times', 14, 500))
label_sub_ext_section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

label_selected_video = QLabel('File: ')
label_selected_video.setFont(QFont('Times', 12, 500))
label_selected_video.setAlignment(Qt.AlignmentFlag.AlignLeft)
label_selected_video.setStyleSheet('color: #60616C;')


""" BUTTON - VIDEO PATH """
def generate_subtitle_track_title(sub_track):
    """
    QMediaMetaData --> Subtitle track info
    Examples:
        Hungarian - forced
        English - SDH[sub]
    """
    title = sub_track.stringValue(sub_track.Key.Title)
    subtitle_language = sub_track.stringValue(sub_track.Key.Language)
    if title:
        subtitle_track_title = f'{subtitle_language} - [{title}]'
    else:
        subtitle_track_title = f'{subtitle_language}'
    return subtitle_track_title


def button_add_video_path_clicked():
    if is_ffmpeg_installed:
        dialog_add_video_path = QFileDialog()
        dialog_add_video_path.setWindowTitle("Select a video file")
        dialog_add_video_path.setNameFilter("Video files (*.mkv *.mp4)")
        dialog_add_video_path.exec()
        sub_tracks_combo_box.clear()
        if dialog_add_video_path.result():
            vr.sub_tracks_list = []
            vr.vid_path = dialog_add_video_path.selectedFiles()[0]
            vr.vid_title = Path(vr.vid_path).stem
            label_selected_video.setText(f'File: {vr.vid_title}')

            mp = QMediaPlayer()
            mp.setSource(QUrl.fromLocalFile(vr.vid_path))
            # PyQt 6.11.1 - .subtitleTracks() not producing sub list
            if mp.subtitleTracks():
                vr.audio_tracks_amount = len(mp.audioTracks())
                for sub_track in mp.subtitleTracks():
                    subtitle_track_title = generate_subtitle_track_title(sub_track)
                    vr.sub_tracks_list.append(subtitle_track_title)
                sub_tracks_combo_box.addItems(vr.sub_tracks_list)
            else:
                sub_tracks_combo_box.addItem("No subtitles available")
        else:
            label_selected_video.setText(f'File:')
            sub_tracks_combo_box.addItem("No subtitles available")
    else:
        MyMessageBoxError("FFmpeg", "FFmpeg is not installed / added to the system path!")

button_add_video_path = QPushButton(text='Select Video')
button_add_video_path.setCursor(Qt.CursorShape.PointingHandCursor)
button_add_video_path.clicked.connect(button_add_video_path_clicked)
button_add_video_path.setFont(QFont('Times', 12, 500))


""" BUTTON - EXTRACT SUB AND OPEN FOLDER """
def button_extract_action():
    """
    Stream: subtitle channels come after the audio channels >> "stream_index" calculation
    -y: automatically override the existing file
    """
    if vr.vid_path and vr.audio_tracks_amount:
        sub_index = sub_tracks_combo_box.currentIndex()
        stream_index = vr.audio_tracks_amount + 1 + sub_index
        sub_selection = sub_tracks_combo_box.currentText()
        sub_file_title = f'{vr.vid_title} - {sub_selection}.srt'
        sub_path = Path(Path(vr.vid_path).parent, sub_file_title)
        ffmpeg_action = f'ffmpeg -i "{vr.vid_path}" -y -map 0:{stream_index} -c:s copy "{sub_path}"'
        try:
            os.system(ffmpeg_action)
        except:
            MyMessageBoxError("Subtitle extraction", "Was not able to extract the selected subtitle.")
        open_directory(vr.vid_path)

button_extract = QPushButton("Extract Sub / Open Folder")
button_extract.setCursor(Qt.CursorShape.PointingHandCursor)
button_extract.clicked.connect(button_extract_action)
button_extract.setFont(QFont('Times', 12, 500))




"""
##############
    LAYOUT    
##############
"""
layout_base = QVBoxLayout()

""" SUBTITLE EXTRACTION """
layout_base.addWidget(label_sub_ext_section_title)
layout_base.addWidget(label_selected_video)
layout_top = QHBoxLayout()
layout_top.setContentsMargins(0,0,0,20)
layout_top.addWidget(button_add_video_path)
layout_top.addWidget(sub_tracks_combo_box)
layout_top.addWidget(button_extract)


""" AUDIO DESCRIPTION REMOVAL """
layout_bottom_hor = QHBoxLayout()
layout_bottom_vor = QVBoxLayout()
layout_bottom_hor.addWidget(button_single_subtitle)
layout_bottom_hor.addWidget(button_bulk_subtitle)
layout_bottom_vor.addWidget(listWidget)


""" LAYOUT BASE """
layout_base.addLayout(layout_top)
layout_base.addWidget(label_desc_removal_section_title)
layout_base.addLayout(layout_bottom_hor)
layout_base.addLayout(layout_bottom_vor)


window.setLayout(layout_base)

window.show()
sys.exit(app.exec())