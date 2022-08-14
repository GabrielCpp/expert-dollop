FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

WORKDIR /opt/workdir

RUN apt-get update -y && apt-get install -y openjdk-11-jre-headless google-cloud-sdk-firestore-emulator google-cloud-sdk

CMD [ "gcloud", "beta", "emulators", "firestore", "start", "--host-port=0.0.0.0:8806" ]