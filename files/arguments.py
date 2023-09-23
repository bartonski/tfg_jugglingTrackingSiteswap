import sys
import argparse

parser = argparse.ArgumentParser(allow_abbrev=True)

parser.add_argument(
    '--project_path',
    metavar='PROJECT PATH', type=str,
    help='Path to juggle tracking project',
    default='./project'
)

parser.add_argument(
    '--dataset_dir',
    metavar='DATASET DIR', type=str,
    help='Path to juggling data'
)

parser.add_argument(
    '--siteswap',
    metavar='SITE SWAP', type=str,
    help='Manually entered site swap',
    default=''
)

parser.add_argument(
    '--system',
    metavar='TRACKING SYSTEM', type=str,
    help='Tracking System',
    default='ColorTrackingMaxBalls'
)

parser.add_argument(
    '--config_file',
    metavar='CONFIG FILE', type=str,
    help='Configuration file name',
    default='config.yml'
)

parser.add_argument(
    'video_file',
    metavar='VIDEO FILE', type=str,
    help='Input video file'
)

