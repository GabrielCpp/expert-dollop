FROM golang:1.15-alpine

RUN apk add git
RUN go get github.com/fullstorydev/emulators/storage/...
RUN go install github.com/fullstorydev/emulators/storage/...

CMD gcsemulator -port 8888 -dir var/bigtable