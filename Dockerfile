FROM python:3.9

ENV PYTHONUNBUFFERED=1

RUN apt-get update

RUN apt install -y libx264-dev

RUN apt install ffmpeg libsm6 libxext6  -y

RUN mkdir /src
WORKDIR /src

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

RUN pip install --upgrade pip

COPY src/requirements.txt /src/
RUN pip install -r requirements.txt
RUN pip install -e git+https://github.com/mohamed-challal/pafy.git@develop#egg=pafy

COPY src /src/
RUN pip install -r src/detect_module/Yolov5_StrongSORT_OSNet/requirements.txt