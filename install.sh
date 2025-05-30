#!/bin/sh

# shellcheck disable=SC2012  # Use Find instead of Ls to better handle non-alphanum...
# shellcheck disable=SC2026 # This word is outside of quotes. Did you intend...

rm -fr dir/ && mkdir -p dir/ && cd dir/ && pwd

curl -LSsf https'://'raw'.'githubusercontent'.'com''/pelavarre/xshverb/refs/heads/main/bin/xshverb'.'py >xshverb'.'py
wc -l xshverb'.'py  # smaller than 1000 is a download problem
chmod +x xshverb'.'py

for F in a c h i n o p pq r s t u x; do ln -s "$PWD"/xshverb'.'py "$F"; done

export PATH="$PWD:$PATH:$PWD"

ls -l |i  u  s -nr  h  c
