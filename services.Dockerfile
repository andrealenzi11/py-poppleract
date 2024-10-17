FROM andrealenzi/poppleract-base:24.10_5.4.1

COPY poppleract /poppleract
COPY LICENSE /
COPY requirements.txt /
COPY version.json /

RUN pip3 install -U pip setuptools wheel && \
    pip3 install -r /requirements.txt

ENV PYTHONPATH=${PYTHONPATH}:/
ENV SERVICES_HOST=0.0.0.0
ENV SERVICES_PORT=8080
EXPOSE ${SERVICES_PORT}

WORKDIR /poppleract
ENTRYPOINT ["python3", "services.py"]
