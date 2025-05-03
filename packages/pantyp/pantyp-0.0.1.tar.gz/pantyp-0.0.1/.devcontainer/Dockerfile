FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu24.04

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    fontconfig \
    fonts-firacode  \
    fonts-noto \
    fonts-noto-cjk \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /tmp/fonts \
  && cd /tmp/fonts \
  && git clone --depth 1 https://github.com/stipub/stixfonts.git \
  && mkdir -p /usr/share/fonts/opentype/stix2 \
  && cp stixfonts/fonts/static_otf/*.otf /usr/share/fonts/opentype/stix2/ \
  && fc-cache -fv \
  && rm -rf /tmp/fonts