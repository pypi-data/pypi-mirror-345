# Welcome to the Imaging Server Kit's documentation!

The **Imaging Server Kit** is an open-source Python package for deploying image analysis algorithms as web services.

- Run computations remotely, while client applications remain focused on visualization.
- Connect to an algorithm server and run algorithms from [QuPath](https://github.com/Imaging-Server-Kit/qupath-extension-serverkit), [Napari](https://github.com/Imaging-Server-Kit/napari-serverkit), and Python.

## Key Features

- Turn standard Python functions into fully-featured image processing web servers with minimal effort.

```python
@algorithm_server({"image": ImageUI()})
def segmentation_server(image):
    segmentation = # your code here
    return [(segmentation, {}, "mask")]
```

<!-- - Automatically generate UIs in Napari and QuPath to test your tools. -->

## Supported image analysis tasks

| Task              | Examples                        | Napari | QuPath |
|-------------------|---------------------------------| ------ | ------ |
| Segmentation     | [StarDist](https://github.com/Imaging-Server-Kit/serverkit-stardist), [CellPose](https://github.com/Imaging-Server-Kit/serverkit-cellpose), [Rembg](https://github.com/Imaging-Server-Kit/serverkit-rembg), [SAM-2](https://github.com/Imaging-Server-Kit/serverkit-sam2), [InstanSeg](https://github.com/Imaging-Server-Kit/serverkit-instanseg)               | ✅ | ✅ |
| Object detection | [Spotiflow](https://github.com/Imaging-Server-Kit/serverkit-spotiflow), [LoG detector](https://github.com/Imaging-Server-Kit/serverkit-skimage-LoG)    | ✅ | ✅ |
| Vector fields   | [Orientationpy](https://github.com/Imaging-Server-Kit/serverkit-orientationpy)                   | ✅ | ✅ |
| Object tracking  | [Trackastra](https://github.com/Imaging-Server-Kit/serverkit-trackastra), [Trackpy](https://github.com/Imaging-Server-Kit/serverkit-trackpy)         | ✅ |  |
| Image-to-Image  | [SPAM](https://github.com/Imaging-Server-Kit/serverkit-spam), [Noise2Void](https://github.com/Imaging-Server-Kit/serverkit-n2v)         | ✅ |  |
| Text-to-Image   | [Stable Diffusion](https://github.com/Imaging-Server-Kit/serverkit-stable-diffusion)         | ✅ |  |
| Image-to-Text   | [Image captioning](https://github.com/Imaging-Server-Kit/serverkit-blip-captioning)         | ✅ |  |
| Classification   | [ResNet50](https://github.com/Imaging-Server-Kit/serverkit-resnet50)         | ✅ |  |

A gallery of example implementations for commonly used algorithms is available in the [repository](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples).

## Installation

Install the `imaging-server-kit` package with `pip`:

```
pip install imaging-server-kit
```

or clone the project and install the development version:

```
git clone https://github.com/Imaging-Server-Kit/imaging-server-kit.git
cd imaging-server-kit
pip install -e .
```

## License

This software is distributed under the terms of the [BSD-3](http://opensource.org/licenses/BSD-3-Clause) license.