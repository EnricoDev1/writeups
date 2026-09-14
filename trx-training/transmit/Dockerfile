FROM ubuntu:25.04

# Update and install packages
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    qemu-system-x86 \
    socat

# Copy challenge entrypoint
COPY bzImage /opt/
COPY initramfs.cpio.gz /opt/
COPY flag /opt/
COPY run.sh /opt/
COPY entrypoint.sh /opt/
RUN chmod +x /opt/run.sh
RUN chmod +x /opt/entrypoint.sh

WORKDIR /opt/

# Socat listening port
EXPOSE 1337

# Change entrypoint to launch challenge
CMD ["./entrypoint.sh"]
