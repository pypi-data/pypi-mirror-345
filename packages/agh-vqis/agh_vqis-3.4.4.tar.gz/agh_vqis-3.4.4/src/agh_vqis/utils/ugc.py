import logging

import pickle
import pandas as pd
import platform
from pathlib import Path

# For content-aware scene detection:
from scenedetect.detectors.content_detector import ContentDetector
from scenedetect.scene_manager import SceneManager
# For caching detection metrics and saving/loading to a stats file
from scenedetect.stats_manager import StatsManager
from scenedetect.video_manager import VideoManager

# Disable scenedetect logging to prevent "VideoManager is deprecated and will be removed." message from showing
logging.getLogger('pyscenedetect').disabled = True


def find_scenes(video_path, threshold=30.0):
    """
    Detects scenes in the provided video file.
    :param video_path: full path to the analysed video
    :param threshold: threshold used by the pyscenedetect. Default 30.
    :return: List of detected scenes in the video
    """
    # type: # (str) -> List[Tuple[FrameTimecode, FrameTimecode]]
    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    # Construct our SceneManager and pass it our StatsManager.
    scene_manager = SceneManager(stats_manager)

    # Add ContentDetector algorithm (each detector's constructor
    # takes detector options, e.g. threshold).
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    # We save our stats file to {VIDEO_PATH}.stats.csv.
    # stats_file_path = '%s.stats.csv' % video_path

    scene_list = []

    try:
        # If stats file exists, load it.
        # if os.path.exists(stats_file_path):
        # Read stats from CSV file opened in read mode:
        # with open(stats_file_path, 'r') as stats_file:
        # stats_manager.load_from_csv(stats_file)

        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(start_in_scene=True)
        # Each scene is a tuple of (start, end) FrameTimecodes.

        # We only write to the stats file if a save is required:
        # if stats_manager.is_save_required():
        # base_timecode = video_manager.get_base_timecode()
        # with open(stats_file_path, 'w') as stats_file:
        # stats_manager.save_to_csv(stats_file, base_timecode)

    finally:
        video_manager.release()

    return scene_list


def get_shots_data(scene_list_out, df):
    """
    This is the main function responsible for extraction of data related to TA and SA per shot.
    :param scene_list_out: List of scenes
    :param df: dataframe with vqis
    :return: A dictionary containing: (1) the shot number (2) frames range in form of a dictionary containing the first
            and the last shot of the frame, (3) Average Temporal Activity for the shot, (4) average spatial activity
            for the shot.
    """
    shot_number = 0
    shots_data = []

    for i, scene in enumerate(scene_list_out):

        ta_sum = 0
        sa_sum = 0
        first_frame_number = scene[0].get_frames() + 1,
        last_frame_number = scene[1].get_frames()

        first_frame_number = int(first_frame_number[0])

        shot_frames_number = last_frame_number - first_frame_number

        # print("TEST: ", last_frame_number)
        # print(
        #    'Scene %2d: Start Frame %d, End Frame %d' % (
        #        i + 1,
        #        scene[0].get_frames() + 1,
        #        scene[1].get_frames()))

        line_count = 0

        # TODO: This part can be optimized!!
        # MITSU_csv = open(MITSU_output_path)
        # csv_reader = csv.reader(MITSU_csv, delimiter=delimiter)
        # for row in csv_reader:

        for j in df.index:
            if first_frame_number <= line_count <= last_frame_number:

                ta_sum += float(df['TA:'][j])
                sa_sum += float(df['SA:'][j])

            line_count += 1

        shot = {
            'shot_number': shot_number,
            'frames_range': "{0}, {1}".format(first_frame_number, last_frame_number),
            'TA': float(ta_sum / shot_frames_number),
            'SA': float(sa_sum / shot_frames_number)
        }

        shots_data.append(shot)
        shot_number += 1

    return shots_data


def video_to_cuts(df, shots_data):
    df = df.astype(float)

    df['Frame:'] += 1

    data = []
    for i in shots_data:
        frame = i['frames_range'].replace(" ", "").split(",")
        data.append(df.iloc[int(frame[0]):int(frame[1]), :].mean())

    cuts = pd.DataFrame(data)
    cuts = cuts[['Blockiness:', 'SA:', 'Blockloss:', 'Blur:', 'TA:',
                 'Exposure(bri):', 'Contrast:', 'Noise:', 'Slice:', 'Flickering:']]
    cuts.columns = ['Blockiness:', 'SA:', 'Blockloss:', 'Blur:', 'TA:',
                    'Exposure(bri):', 'Contrast:', 'Noise:', 'Slice:', 'Flickering:']
    return cuts, shots_data


def ugc(df, shots_data):
    cuts, shots_data = video_to_cuts(df, shots_data)

    model_path = Path(
        '/'.join(
            __file__.split('/')[:-1]) if platform.system() != 'Windows' else '\\'.join(__file__.split('\\')[:-1]),
            '../models/ugc/',
            '12k_all_set.json'
    )

    xgb_cl = pickle.load(open(str(model_path), 'rb'))

    for count, value in enumerate(shots_data):
        preds = xgb_cl.predict(cuts[count:count+1])

        value['ugc'] = 0 if int(preds[0]) == 1 else 1
    return shots_data  # 0 => not UGC, 1 => UGC
