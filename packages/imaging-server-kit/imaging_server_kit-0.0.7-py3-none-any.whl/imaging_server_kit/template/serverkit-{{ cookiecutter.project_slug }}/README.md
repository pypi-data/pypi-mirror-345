![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# serverkit-{{ cookiecutter.project_slug }}

Implementation of a web server for [{{ cookiecutter.project_name }}]({{ cookiecutter.project_url }}).

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
- http://localhost:8000/version : Version of the `imaging-server-kit` package.
- http://localhost:8000/{{ cookiecutter.project_slug }}/info : Web page displaying project metadata.
- http://localhost:8000/{{ cookiecutter.project_slug }}/parameters : Json Schema representation of algorithm parameters.
- http://localhost:8000/{{ cookiecutter.project_slug }}/sample_images : Byte string representation of the sample images.

**POST endpoints**

- http://localhost:8000/{{ cookiecutter.project_slug }}/process : Endpoint to run the algorithm.

## Running the server with `docker-compose`

To build the docker image and run a container for the algorithm server in a single command, use:

```
docker compose up
```

The server will be running on http://localhost:8000.

<!-- ## Sample images provenance -->

<!-- Fill if necessary. -->
