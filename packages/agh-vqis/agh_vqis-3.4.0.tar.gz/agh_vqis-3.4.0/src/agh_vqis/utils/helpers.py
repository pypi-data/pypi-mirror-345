# Author: Filip Korus <fkorus@student.agh.edu.pl>
# Created: June 1, 2021

import platform
import ffmpeg
import os
import shutil
import uuid
from pathlib import Path
from enum import Enum
from subprocess import PIPE, STDOUT, Popen, run, CalledProcessError


class VQIs:
    blockiness = 'blockiness'
    SA = 'SA'
    letterbox = 'letterbox'
    pillarbox = 'pillarbox'
    blockloss = 'blockloss'
    blur = 'blur'
    TA = 'TA'
    blackout = 'blackout'
    freezing = 'freezing'
    exposure = 'exposure'
    contrast = 'contrast'
    interlace = 'interlace'
    noise = 'noise'
    slice = 'slice'
    flickering = 'flickering'
    colourfulness = 'colourfulness'
    blur_amount = 'blur_amount'
    ugc = 'ugc'


class CastVQI:
    blockiness = 'cast_Blockiness'
    blur = 'cast_Blur'
    contrast = 'cast_Contrast'
    exposure = 'cast_Exposure(bri)'
    interlace = 'cast_Interlace'
    noise = 'cast_Noise'


class DestResolution:
    p240 = 240
    p360 = 360
    p480 = 480
    p720 = 720
    p1080 = 1080
    p1440 = 1440
    p2160 = 2160


class Results(Enum):
    """
    Makes it less error-prone to index a dictionary with objects storing IQIs results
    """
    BLUR_AMOUNT = 1
    COLOURFULNESS = 2
    UGC = 3
    VQIS = 4


def get_executable_filename():
    available_executables = {
        'Windows AMD64': 'agh_vqis_win64_mt.exe',
        'Windows x86_64': 'agh_vqis_win64_mt.exe',

        'Linux aarch64': 'agh_vqis_linux_aarch64_mt',
        'Linux x86_64': 'agh_vqis_linux_x86_64_mt',

        'Darwin arm64': 'agh_vqis_macosx_arm64_mt',
        'Darwin x86_64': 'agh_vqis_macosx_x86_64_mt'
    }

    os_type, machine = platform.system(), platform.machine()

    return available_executables \
        .get(f'{os_type} {machine}', None)


def get_current_file_location() -> Path:
    return Path(
        '/'.join(__file__.split('/')[:-1]) if platform.system() != 'Windows' else '\\'.join(__file__.split('\\')[:-1]),
        '../')


def get_mm_file_properties(video_path: Path):
    """
    Returns multimedia file properties.

    :param video_path: path to a video or image file
    :return: (width, height, nb_frames, frame_rate)
    """
    probe = ffmpeg.probe(str(video_path.resolve()))
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

    if video_stream is None:
        raise Exception('No video stream found')

    width = int(video_stream['width'])
    height = int(video_stream['height'])
    nb_frames = 0
    try:
        nb_frames = int(video_stream['nb_frames'])
    except KeyError:
        pass
    frame_rate = 1 if nb_frames == 0 else eval(video_stream['avg_frame_rate'])

    return width, height, nb_frames, frame_rate


def get_selected_vqis(options: dict) -> int:
    vqis_weights = {
        VQIs.blockiness: 1,
        VQIs.SA: 2,
        VQIs.letterbox: 4,
        VQIs.pillarbox: 8,
        VQIs.blockloss: 16,
        VQIs.blur: 32,
        VQIs.TA: 64,
        VQIs.blackout: 128,
        VQIs.freezing: 256,
        VQIs.exposure: 512,
        VQIs.contrast: 1024,
        VQIs.interlace: 2048,
        VQIs.noise: 4096,
        VQIs.slice: 8192,
        VQIs.flickering: 16384
    }

    selected_vqis = 32767  # select all by default

    for key, value in options.items():
        if not value:
            try:
                selected_vqis -= vqis_weights[key]  # remove vqis
            except KeyError:
                pass

    return selected_vqis


def convert_to_yuv(input_file: Path, output_file: Path):
    ffmpeg.input(str(input_file), loglevel='error').output(str(output_file), pix_fmt='yuv420p').run()


def mkdir(dir_name: Path):
    """
    This function creates a directory
    :param dir_name: Name of the directory to create
    :return: Nothing
    """
    if not os.path.exists(str(dir_name)):
        os.makedirs(str(dir_name))


def rmdir(dir_name: Path):
    """
    This function deletes an entire folder provided by dir_name with all contents with exception handling
    :param dir_name: Folder to be deleted
    :return: Nothing
    """
    try:
        shutil.rmtree(str(dir_name))
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def mv_file(src: Path, dst: Path):
    """
    This function moves a file from src to dst.
    :param src: Source
    :param dst: Destination
    :return: Nothing
    """
    try:
        shutil.move(str(src), str(dst))
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def system_call(sfs_call_elems: list[str], logger):
    if logger is not None:
        logger.debug(' '.join(sfs_call_elems))

    try:
        # completed_sfs_run = run(sfs_call, check=True, shell=True, stdout=PIPE, stderr=STDOUT)
        sfs_popen = Popen(sfs_call_elems, stdout=PIPE, stderr=STDOUT)
        sfs_stdout, sfs_stderr = sfs_popen.communicate()  # wait for the VQIs to finish
    except OSError as e:
        if logger is not None:
            logger.error(f'Calling {sfs_call_elems[0]} failed with the following message: {e}')
        return -1
    if sfs_popen.returncode != 0:
        if logger is not None:
            logger.error(f"Calling {sfs_call_elems[0]} failed with the following return code: "
                         f"{sfs_popen.returncode}")
            logger.error(f"{str(sfs_call_elems[0])}\'s output: {sfs_stdout.decode('ascii')}")
        return -1

    if logger is not None:
        logger.debug(f"{sfs_call_elems[0]} was successfully executed")


def is_ffmpeg_installed():
    try:
        # Check if 'ffmpeg' can be run as a command without raising an exception
        run(['ffmpeg', '-version'], stdout=PIPE, stderr=PIPE, text=True)
        return True
    except FileNotFoundError:
        # The 'ffmpeg' command was not found
        return False
    except CalledProcessError:
        # 'ffmpeg' is installed but returned a non-zero exit code (possible on Linux)
        return True
    except Exception as e:
        # Other exceptions might occur
        return False


def generate_uuid():
    return str(uuid.uuid4())
