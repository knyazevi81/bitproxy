FROM alpine:3.19

ARG TARGETARCH=amd64

RUN wget -O /usr/local/bin/vk-turn-proxy \
    https://github.com/cacggghp/vk-turn-proxy/releases/latest/download/server-linux-${TARGETARCH} \
    && chmod +x /usr/local/bin/vk-turn-proxy

ENTRYPOINT ["/usr/local/bin/vk-turn-proxy"]
CMD ["-listen", "0.0.0.0:56000", "-connect", "127.0.0.1:51820"]
