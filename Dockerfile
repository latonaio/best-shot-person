FROM python-library-l4t:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=best-shot-person \
    USER=aion \
    PASSWORD=aion

ARG DEVICE_NAME
ARG NEXT_DEVICE_NAME
ARG NEXT_USER

RUN mkdir /var/lib/aion
WORKDIR /var/lib/aion
# Setup Directoties
RUN mkdir -p \
    ./$POSITION/$SERVICE \
    ./Data/$SERVICE/file/data \
    ./Data/$SERVICE/file/input \
    ./Data/$SERVICE/file/output

WORKDIR /var/lib/aion/$POSITION/$SERVICE/

ADD . .

# Install dependencies
# RUN apt-get update && apt-get install gosu
# RUN pip3 install --upgrade pip && \
#     pip3 install -r ./requirements.txt

# Define next user & next device
RUN sed -i "s/home\/latona\/athena/var\/lib\/aion/" ./main.py \
 && sed -i "s/athena/${NEXT_DEVICE_NAME}/g" ./main.py  


RUN sed -i "s/home\/latona\/zeus\/Runtime/var\/lib\/aion\/Data/g" ./json/C_BestShotPerson.json \
 && sed -i "s/object-detection-from-images\/ObjectDetectionClient/object-detection-from-images-client/g" ./json/C_BestShotPerson.json \
 && sed -i "s/capture-depth-from-depth-sensor/real-time-video-streaming/g" ./json/C_BestShotPerson.json \
 && sed -i "s/zeus/${DEVICE_NAME}/g" ./json/C_BestShotPerson.json

CMD ["./docker-entrypoint-scripts/docker-entrypoint.sh"]
# CMD ["python3", "-u", "main.py"]


