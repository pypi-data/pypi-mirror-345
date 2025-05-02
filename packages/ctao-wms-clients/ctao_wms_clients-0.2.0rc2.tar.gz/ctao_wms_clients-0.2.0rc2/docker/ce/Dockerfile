FROM almalinux:9

ARG DIRACOS_VERSION="2.52"
ARG CTADIRAC_VERSION="2.2.74"
ARG RUCIO_VERSION="35.4.1"
ARG USERID=1000
ARG GROUPID=1000

ENV DIRAC_DIR="/ctadirac/${CTADIRAC_VERSION}"

RUN dnf install -y \
        procps \
        openssh-server \
        openssh-clients \
        epel-release \
        python3 \
        python-unversioned-command \
        https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest.noarch.rpm \
    && dnf install -y cvmfs apptainer \
    && cvmfs_config setup \
    && systemctl enable autofs \
    && systemctl enable sshd

RUN cd /etc/ssh && ssh-keygen -A

ADD default.local /etc/cvmfs/default.local
ADD ctao.dpps.test.conf /etc/cvmfs/config.d/ctao.dpps.test.conf

RUN mkdir -p /etc/grid-security/certificates
RUN mkdir -p /etc/grid-security/vomsdir/ctao.dpps.test
RUN mkdir -p /etc/grid-security/vomses
RUN touch /etc/grid-security/vomses/ctao.dpps.test

RUN \
  if getent group ${GROUPID}; then \
    groupmod --new-name dirac $(getent group ${GROUPID} | cut -d: -f1); \
  else \
    groupadd --gid ${GROUPID} dirac; \
  fi\
  && adduser --uid ${USERID} --gid dirac -s /bin/bash -d /home/dirac dirac

RUN mkdir -p /home/dirac/.ssh && chown -R dirac:dirac /home/dirac

# Install DIRAC client
RUN mkdir -p ${DIRAC_DIR} \
    && curl -LO https://github.com/DIRACGrid/DIRACOS2/releases/download/${DIRACOS_VERSION}/DIRACOS-Linux-x86_64.sh \
    && bash DIRACOS-Linux-x86_64.sh -p ${DIRAC_DIR}/Linux-x86_64 \
    && rm -f DIRACOS-Linux-x86_64.sh \
    && source ${DIRAC_DIR}/Linux-x86_64/diracosrc \
    && pip install --no-cache-dir \
      CTADIRAC[pilot]==${CTADIRAC_VERSION} rucio-clients==${RUCIO_VERSION} \
      git+https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms-rucio-policy \
    && ln -s ${DIRAC_DIR} /ctadirac/pro \
    && chown -R dirac:dirac /ctadirac

CMD ["/usr/sbin/init"]
