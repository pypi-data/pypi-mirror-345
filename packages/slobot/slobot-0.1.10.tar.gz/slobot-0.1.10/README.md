# LeRobot SO-ARM-100 6 DOF robotic arm manipulation with Genesis simulator and Feetech motors

There are 2 main use cases
1. sim to real, where genesis controls the physical robot
2. real to sim, where the physical robot moves will refresh the robot rendering in genesis

## Acknowledgements

### The Robot Studio

[SO-ARM-100](https://github.com/TheRobotStudio/SO-ARM100) provides CAD & [STL model](https://github.com/TheRobotStudio/SO-ARM100/blob/main/stl_files_for_3dprinting/Follower/Print_Follower_SO_ARM100_08k_Ender.STL) of the robotic arm links. After 3D-printing them and ordering the remaining parts, the robot can be assembled for prototyping.

### Feetech

[Feetech STS3115](https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear.html) is the servo inserted in each joint of the robot.

- It's *motor* rotates the connected link.
- It's *magnetic encoder* measures the absolute angular position of the joint.

### LeRobot

[LeRobot](https://github.com/huggingface/lerobot) provides a SOTA library to perform *Imitation Learning* and *Reinforcement Learning* for robotics tasks.

Curate a new dataset: have the follower arm perform a task of interest, by replicating the motion of the leader arm held a human operator.

Then fine-tune a model on the training dataset.

Finally evaluate it on the eval dataset to see how well it performs.

```
@misc{cadene2024lerobot,
    author = {Cadene, Remi and Alibert, Simon and Soare, Alexander and Gallouedec, Quentin and Zouitine, Adil and Wolf, Thomas},
    title = {LeRobot: State-of-the-art Machine Learning for Real-World Robotics in Pytorch},
    howpublished = "\url{https://github.com/huggingface/lerobot}",
    year = {2024}
}
```

### Genesis

[Genesis](https://github.com/Genesis-Embodied-AI/Genesis) is the physics engine running the simulation.

```
@software{Genesis,
  author = {Genesis Authors},
  title = {Genesis: A Universal and Generative Physics Engine for Robotics and Beyond},
  month = {December},
  year = {2024},
  url = {https://github.com/Genesis-Embodied-AI/Genesis}
}
```

## Setup the environment

### Python

Python version should match [OMPL library](https://github.com/ompl/ompl/releases/tag/prerelease) compatible version.

Following installs Python `3.12.9` with *pyenv*


```
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl https://pyenv.run | bash
alias pyenv=~/.pyenv/bin/pyenv
python_version=3.12.9
pyenv install $python_version
export PATH="$HOME/.pyenv/versions/$python_version/bin:$PATH"
```

Create a virtual environment with *venv*

```
python -m venv .venv
. .venv/bin/activate
```


### slobot

```
pip install slobot
```

#### Other dependencies

Install following dependencies

1. genesis

```
pip install git+https://github.com/Genesis-Embodied-AI/Genesis.git
```

2. lerobot

```
pip install git+https://github.com/huggingface/lerobot.git
```

3. ompl

```
pip install https://github.com/ompl/ompl/releases/download/prerelease/ompl-1.7.0-cp312-cp312-manylinux_2_28_x86_64.whl
```

## Robot configuration

The example loads the [Mujoco XML configuration](https://github.com/google-deepmind/mujoco_menagerie/tree/main/trs_so_arm100).

Ensure the robot configuration directory in available in the current directory.

```
git clone -b main https://github.com/google-deepmind/mujoco_menagerie ../mujoco_menagerie
cp -r ../mujoco_menagerie/trs_so_arm100 .
```

## Validation & Calibration

A series of scripts are provided to help with calibration.

LeRobot suggests 3 keys positions
1. zero
2. rotated
3. rest

### 0. Validate the preset qpos in sim

This validates that the robot is in the targetted position preset in sim.

```
PYOPENGL_PLATFORM=glx python scripts/validation/0_validate_sim_qpos.py [zero|rotated|rest]
```

| zero | rotated | rest |
|----------|-------------|-------|
| ![zero](doc/SimZero.png) | ![rotated](doc/SimRotated.png) | ![rotated](doc/SimRest.png) |


### 1. Calibrate the preset pos

Position the arm manually into the targetted position preset as displayed above. Refer to [LeRobot calibration section](https://github.com/huggingface/lerobot/blob/main/examples/10_use_so100.md#a-manual-calibration-of-follower-arm) and [manual calibration script](https://github.com/huggingface/lerobot/blob/main/lerobot/common/robot_devices/robots/feetech_calibration.py#L401).

```
python scripts/validation/1_calibrate_motor_pos.py [zero|rotated|rest]
```

### 2. Validate the preset *pos to qpos* conversion in sim

Same as script 0, but using the calibrated motor step positions instead of angular joint positions.

```
PYOPENGL_PLATFORM=glx python scripts/validation/2_validate_sim_pos.py [zero|rotated|rest]
```

### 3. Validate the preset pos in real

Similar than 2 which is in sim but now in real. It validates the robot is positioned correctly to the target pos.

```
python scripts/validation/3_validate_real_pos.py [zero|rotated|rest]
```

### 4. Validate real to sim

This validates that moving the real robot also updates the rendered robot in sim.

```
PYOPENGL_PLATFORM=glx python scripts/validation/4_validate_real_to_sim.py [zero|rotated|rest]
```

### 5. Validate sim to real

This validates the robot simulation also controls the physical robot.

```
PYOPENGL_PLATFORM=glx python scripts/validation/4_validate_real_to_sim.py [zero|rotated|rest]
```


## Examples

### Real

This example moves the robot to the 3 preset positions, waiting 1 sec in between each one.

```
python scripts/real.py
```

<video controls src="https://github.com/user-attachments/assets/857dd958-2e4c-4221-abef-563f9617385a"></video>


### Sim To Real

This example performs the 3 elemental rotations in sim and real.
The simulation generates steps, propagating the joint positions to the Feetech motors.

```
PYOPENGL_PLATFORM=glx python scripts/sim_to_real.py
```


| sim | real |
|----------|-------------|
| <video controls src="https://github.com/user-attachments/assets/eab20130-a21d-4811-bca8-07502012b8da"></video> | <video controls src="https://github.com/user-attachments/assets/a429d559-58e4-4328-a7f0-17f7477125ff"></video> |


### Image stream

Genesis camera provides access to each frames rendered by the rasterizer. Multiple types of image are provided:
- RGB
- Depth
- Segmentation
- Surface

The following script iterates through all the frames, calculating the FPS metric every second.

```
PYOPENGL_PLATFORM=glx python scripts/sim_fps.py
...
FPS= FpsMetric(1743573645.3103304, 0.10412893176772242)
FPS= FpsMetric(1743573646.3160942, 59.656155690238116)
FPS= FpsMetric(1743573647.321373, 59.68493363485116)
FPS= FpsMetric(1743573649.8052156, 12.078059963768446)
FPS= FpsMetric(1743573650.8105915, 59.67917299445178)
FPS= FpsMetric(1743573651.8152244, 59.723304924655935)
...
```


### Gradio apps

Gradio app is a UI web framework to demo ML applications.

Navigate to the [local URL](http://127.0.0.1:7860) in the browser. Then click *Run* button.

#### Image

The [`Image` component](https://www.gradio.app/docs/gradio/image) can sample the frames of the simulation at a small FPS rate.
The frontend receives backend events via a Server Side Event stream. For each new *frame generated* event, it downloads the image from the webserver and displays it to the user.

```
PYOPENGL_PLATFORM=egl python scripts/sim_gradio_image.py
```

![Genesis frame types](./doc/GenesisImageFrameTypes.png)

#### Video

The [`Video` component](https://www.gradio.app/docs/gradio/video) can play a full mp4 encoded in h264 or a stream of smaller TS files.

```
PYOPENGL_PLATFORM=egl python scripts/sim_gradio_video.py
```

![Genesis frame types](./doc/GenesisVideoFrameTypes.png)


#### Qpos

The qpos app displays the joint angular position numbers.

![Genesis qpos](./doc/GenesisQpos.png)

```
python scripts/sim_gradio_qpos.py

2025-04-02 00:45:17,551 - INFO - Sending qpos [1.4888898134231567, -1.8273500204086304, 2.3961710929870605, -0.5487295389175415, 1.5706498622894287, -2.59892603935441e-05]
```

A client connects to the server to receive the qpos updates.

It can then dispatch them to the robot at a predefined `fps` rate to control its position.

```
python scripts/sim_to_real_client.py

2025-04-02 00:45:17,764 - INFO - Received qpos (1.49, -1.83, 2.4, -0.55, 1.57, -0.0)
```

#### Plot

The [Plot component](https://www.gradio.app/docs/gradio/plot) can display a chart. Dashboard monitors key metrics in dedicated [Tab](https://www.gradio.app/docs/gradio/tab)s.
- **qpos**, in *rad*
- **velocity**, in *rad/sec*
- **control force**, in *N.m*


```
python scripts/sim_gradio_dashboard.py
```

![Gradio dashboard](./doc/GradioTabPlots.png)

#### Docker

Build docker image:

```
docker build -t slobot-genesis .
```

Run docker container. Make sure to enable **DRI** for hardware graphics acceleration.

```
docker run -it --security-opt no-new-privileges=true -p 7860:7860 --device=/dev/dri -v $PWD:/home/user/app slobot-genesis-image
```