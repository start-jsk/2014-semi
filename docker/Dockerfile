ARG ROS_DISTRO
ARG UBUNTU_VERSION
FROM osrf/ros:${ROS_DISTRO}-desktop-${UBUNTU_VERSION}
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y curl git wget && \
    rm -rf /var/lib/apt/lists/*

RUN echo "deb http://packages.ros.org/ros-testing/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list

RUN curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -
RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y apt-utils && \
    rm -rf /var/lib/apt/lists/*

# FIXME: https://github.com/start-jsk/jsk_apc/pull/2664
ARG ROS_DISTRO
RUN apt-get update && \
    if [ ${ROS_DISTRO} = "noetic" ]; then \
      apt-get install -y \
        python3-catkin-tools \
        python3-rosdep \
        python3-setuptools \
        python3-wstool \
        python3-pip; \
    else \
      apt-get install -y \
        python-catkin-tools \
        python-rosdep \
        python-setuptools \
        python-wstool \
        python-pip; \
    fi && \
    rm -rf /var/lib/apt/lists/*

ARG ROS_DISTRO
RUN if [ ${ROS_DISTRO} = "indigo" ]; then \
      apt-get update && \
      apt-get install -y software-properties-common && \
      add-apt-repository -y ppa:longsleep/python2.7-backports && \
      apt-get update && \
      apt-get dist-upgrade -y; \
    fi && \
    pip install 'pip==9.0.3' && \
    pip install 'setuptools==44.1.0' && \
    pip install 'dlib==19.21.1' && \
    rm -rf /var/lib/apt/lists/*

# Install python2-compatible packages before rosdep install.
# Related issues:
# - https://github.com/chainer/chainer/issues/8545
# - https://github.com/protocolbuffers/protobuf/issues/8984
ARG ROS_DISTRO
RUN if [ ${ROS_DISTRO} = "indigo" ]; then \
      pip install -U numpy fcn chainercv chainer==6.7.0 gdown==4.4.0 scikit-learn==0.19.1 protobuf==3.17.3; \
    elif [ ${ROS_DISTRO} = "kinetic" ] || [ ${ROS_DISTRO} = "melodic" ]; then \
      pip install fcn chainercv chainer==6.7.0 gdown==4.4.0 protobuf==3.17.3; \
    else \
      apt-get update && \
      apt-get install -y python3-scipy python3-skimage && \
      pip3 install fcn chainercv chainer==6.7.0 gdown==4.4.0 && \
      rm -rf /var/lib/apt/lists/*; \
    fi

ARG ROS_DISTRO
RUN cd ~ && \
    mkdir -p ros/${ROS_DISTRO}/src && \
    cd ros/${ROS_DISTRO}/src && \
    wstool init && \
    wstool set start-jsk/jsk_apc https://github.com/start-jsk/jsk_apc.git -v master --git -y && \
    wstool up -j 2 && \
    wstool merge start-jsk/jsk_apc/.travis.rosinstall && \
    wstool merge start-jsk/jsk_apc/.travis.rosinstall.${ROS_DISTRO} && \
    wstool up -j 2

# Use snapshot of rosdep list on indigo and kinetic
# https://github.com/jsk-ros-pkg/jsk_travis/blob/0.5.26/travis.sh#L295-L300
ARG ROS_DISTRO
RUN if [ ${ROS_DISTRO} = "indigo" ] || [ ${ROS_DISTRO} = "kinetic" ]; then \
      rm /etc/ros/rosdep/sources.list.d/20-default.list && \
      wget https://gist.githubusercontent.com/cottsay/b27a46e53b8f7453bf9ff637d32ea283/raw/476b3714bb90cfbc6b8b9d068162fc6408fa7f76/30-xenial.list -O /etc/ros/rosdep/sources.list.d/30-xenial.list; \
    fi

# /opt/ros/${ROS_DISTRO}/share can be changed after rosdep install, so we run it 3 times.
ARG ROS_DISTRO
RUN apt-get update && rosdep update --include-eol-distros && \
    if [ ${ROS_DISTRO} = "noetic" ]; then \
      export ROS_PYTHON_VERSION=3; \
    fi && \
    for i in $(seq 3); do rosdep install --rosdistro ${ROS_DISTRO} -r -y -i --from-paths /opt/ros/${ROS_DISTRO}/share ~/ros/${ROS_DISTRO}/src; done && \
    rm -rf /var/lib/apt/lists/*

ARG TESTING
ARG ROS_DISTRO
RUN if [ ${TESTING} = "true" ] ; then \
      rm -rf ~/ros; \
    else \
      . /opt/ros/${ROS_DISTRO}/setup.sh && \
      cd ~/ros/${ROS_DISTRO} && \
      if [ ${ROS_DISTRO} = "indigo" ]; then \
        catkin build jsk_apc2015_common jsk_apc2016_common jsk_arc2017_common jsk_2015_05_baxter_apc jsk_2016_01_baxter_apc jsk_arc2017_baxter selective_dualarm_stowing sphand_driver sphand_driver_msgs vl53l0x_mraa_ros baxtergv6_apc2016;\
      elif [ ${ROS_DISTRO} = "kinetic" ]; then \
        catkin config --blacklist test_catkin_virtualenv test_catkin_virtualenv_py3_isolated test_catkin_virtualenv_inherited && \
        catkin build; \
      else \
        catkin build; \
      fi; \
    fi
