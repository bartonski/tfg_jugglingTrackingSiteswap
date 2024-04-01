<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="APP IMAGE" width="80" height="80">
  </a>

  <h3 align="center">Juggling Tracker and Siteswap Extractor</h3>

  <p align="center">
    A project capable of performing ball detection and tracking in juggling videos on one hand, and extracting the executed siteswap on the other.
    <br />
    <br />
    <a href="https://github.com/AlejandroAlonsoG/tfg_jugglingTrackingSiteswap"><strong>Paper (still unpublished, check files)</strong></a>
    <br />
    <br />
    <a href="https://github.com/AlejandroAlonsoG/tfg_jugglingTrackingSiteswap">View Demo</a>
    ·
    <a href="https://github.com/AlejandroAlonsoG/tfg_jugglingTrackingSiteswap/issues">Report Bug</a>
    ·
    <a href="https://github.com/AlejandroAlonsoG/tfg_jugglingTrackingSiteswap/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

The project aims to develop a system capable of extracting juggling siteswaps from videos of jugglers performing their tricks. Siteswap is a widely used notation in juggling to describe patterns. However, there is currently no accessible application that can automatically extract the siteswap from juggling videos. The proposed system will try to address this gap.

The developed system performs well in ideal conditions, successfully identifying the siteswaps in approximately 77.27% of cases. While this level of accuracy may already be sufficient for experienced jugglers, future revisions could focus on improving the system's performance in less ideal video conditions. The ultimate goal is to create an application that can accurately identify complex siteswaps executed by skilled jugglers.

More detailed explanations can be found in the paper referenced at the beginning of this README or by contacting me directly.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

Required dependencies can be found in the requirements.txt file.

### Installation

Not every necessary file is uploaded to the repository.

Once you have cloned it, you will have to prepare the directory as follows for it to work without any modifications:

- tfg_jugglingTrackingSiteswap
  - files
    - (this folder just as it is downloaded)
  - results
    - (this folder just as it is downloaded)
  - dataset
    - here goes all the videos from the dataset. By default, they are expected in a subfolder called tanda2 with the naming convention {ss}\_{color}\_{juggler}.mp4




With that and all dependencies installed, the application should work. If you encounter any problem, feel free to contact me.

<!-- USAGE EXAMPLES -->
## Usage

### `final_system.py`

For the execution of the final system, it is enough to open a terminal in `.../tfg_jugglingTrackingSiteswap` and execute:

```bash
python3 files/final_system.py
```

Any tracking system can be executed on their own in a similar way as if they were main programs. The same thing goes with the `tracking_visualizer`.

### `config_writer.py`

This is a proof-of-concept configuration writer.

```
usage: config_writer.py [-h] [--project_path PROJECT PATH]
                        [--dataset_dir DATASET DIR] [--siteswap SITE SWAP]
                        [--save_dir SAVE DIR] [--output_path SAVE DIR]
                        [--visualize VISUALIZE] [--system TRACKING SYSTEM]
                        [--config_file CONFIG FILE]
                        VIDEO FILE

positional arguments:
  VIDEO FILE            Input video file

options:
  -h, --help            show this help message and exit
  --project_path PROJECT PATH
                        Path to juggle tracking project
  --dataset_dir DATASET DIR
                        Path to juggling data
  --siteswap SITE SWAP  Manually entered site swap
  --save_dir SAVE DIR   Where to save meta-data
  --output_path SAVE DIR
                        Where to save output video
  --visualize VISUALIZE
                        Whether to display results to the screen
  --system TRACKING SYSTEM
                        Tracking System
  --config_file CONFIG FILE
                        Configuration file name

```

If `VIDEO FILE` is in the current directory and `--dataset_dir` is set,
the configuration file will show `VIDEO FILE` as residing in `--dataset_dir`.
Otherwise, `dataset_dir` in the configuration will be the parent directory of
`VIDEO FILE`.

* `--project_path` defaults to `./project`
* `--config_file` defaults to `config.yml` inside `--project_path`
* `--dataset_dir` defaults to unset.
* `--siteswap` is the predicted site swap contained in `VIDEO FILE`.
* `--system` sets the `TRACKING SYSTEM` used to determine the paths of the props
in the juggling pattern.
    * TODO: document the possible values of `TRACKING SYSTEM`

#### Example

```bash
python files/config_writer.py --project_path ~/Videos/juggling/20230806 ~/Videos/juggling/20230806/ss3_blue_barton.mp4
```

Since `--config_file` is not specified, it defaults to config.yml, i.e. ~/Videos/juggling/20230806/config.yml. 

#### Using the GUIe

When you run `config_writer.py`, it will first check the configuration file to
see if any color ranges have been defined. If there are none (such as on the first run, when the configuration file is empty), it will call the color\_extractor module, which reads each frame of the video, makes guesses about objects that might be part of the juggling pattern, and returns an color range that should do a decent job of identifying juggling props.

Config writer will use these ranges as a starting point for color ranges that more accurately identify juggling props and exclude everything else.

When the program starts, video will be playing. Pressing the space bar pauses the video, and allows you to manipulate the color ranges by specifying min and max hue (color, as on a color wheel), value (think of a gray scale image where value of 0 is black and value of 255 is white ), and saturation (the intensity of the color, from 0 (white) to 255 (full intensity).

These are manipulated using sliders. The original image frame shows top/left, the mask (a black and white image where black areas are removed and white areas are kept) shows bottom/left, and the result (which should only show the props themselves) is displayed bottom/right.

Pressing the space bar will re-start the video. You can pause to edit the color range and resume playing as many times as you want.

To quit playing the video and saving the color range, press `<esc>`.

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Alejandro Alonso - [@twitter](https://twitter.com/MelenalexYT) - alexalongarci@gmail.com
TODO: Add my contact information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

The base programs for the main tracking implementations came from

* [Stephen Meschke](https://github.com/smeschke/juggling)
* [Barton Chittenden](https://github.com/bartonski/juggling_detector)

The template of this README came from:
* [othneildrew](https://github.com/othneildrew/Best-README-Template/tree/master)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
