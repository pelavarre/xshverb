rm -fr dir/ && mkdir -p dir/ && cd dir/ && pwd

curl -LSsf https'://'raw'.'githubusercontent'.'com''/pelavarre/xshverb/refs/heads/main/bin/xshverb'.'py >xshverb'.'py

wc -l xshverb'.'py  # smaller than 1000 is a download problem

chmod +x xshverb'.'py

for F in a c h i n o p pq r s t u x; do ln -s $PWD/xshverb'.'py $F; done

export PATH="$PWD:$PATH:$PWD"

git show |i  u  s -nr  h  c
