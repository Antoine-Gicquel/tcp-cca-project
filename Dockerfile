FROM debian:latest


RUN apt update
RUN apt install -y traceroute iproute2 dnsutils iputils-ping tcpdump iperf3 inotify-tools python3 python3-pip

COPY requirements.txt .
RUN pip3 install -r requirements.txt

CMD ["/app/start.sh"]
# CMD ["python3", "/app/app.py"]