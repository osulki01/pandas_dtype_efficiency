FROM python:3.7

# Add user with sudo privileges
ARG username=docker_user
RUN adduser --disabled-password --gecos '' $username
RUN adduser $username sudo
RUN ["echo", "%sudo ALL=(ALL) NOPASSWD:ALL", ">>", "/etc/sudoers"]
USER $username

# Ensure current host directory containing python requirements is available and install packages
ARG working_directory=/usr/src/app
WORKDIR $working_directory
COPY requirements-dev.txt .
RUN pip install --user --requirement requirements-dev.txt

# Ensure the local namespace python packages can be imported and used from anywhere
ENV PYTHONPATH="${PYTHONPATH}:${working_directory}"

# Make sure source code and tests are available
COPY pandas_dtype_efficiency.py .
COPY tests tests/

# Keep container running in detached mode, so execute a meaningless command in the foreground
CMD ["tail", "-f", "/dev/null"]
