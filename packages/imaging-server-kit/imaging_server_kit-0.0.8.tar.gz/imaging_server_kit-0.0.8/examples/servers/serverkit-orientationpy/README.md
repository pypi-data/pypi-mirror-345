![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# serverkit-orientationpy

Implementation of a web server for [Orientationpy](https://gitlab.com/epfl-center-for-imaging/orientationpy).

## Installation

Install dependencies:

```
pip install -r requirements.txt
```

Run the server:

```
python main.py
```

The server will be running on http://localhost:8000.

## Endpoints

A documentation of the endpoints is automatically generated at http://localhost:8000/docs.

**GET endpoints**

- http://localhost:8000/ : Running algorithm message.
- http://localhost:8000/version: Version of the `imaging-server-kit` package.
- http://localhost:8000/orientationpy/info: Web page displaying project metadata.
- http://localhost:8000/orientationpy/parameters: Json Schema representation of algorithm parameters.
- http://localhost:8000/orientationpy/sample_images: Byte string representation of the sample images.

**POST endpoints**

- http://localhost:8000/orientationpy/process: Processing endpoint to run the algorithm.

## Running the server with `docker-compose`

To build the docker image and run a container for the algorithm server in a single command, use:

```
docker compose up
```

The server will be running on http://localhost:8000.

## Sample images provenance

- `image1_from_OrientationJ.tif`: Example image from [OrientationJ](https://bigwww.epfl.ch/demo/orientationj/).
