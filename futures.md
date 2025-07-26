things to do, futures to build

soon


    grep ~/e, but without the unprintables


    |pq| didn't scrub out the destructive unprintable control codes, from Sh Screen
    |pq expand| didn't either


    fix many bugs of
        $ : tac && fh |pq r |pq 'uniq --keys' |r |grep press |grep -iv PLaVarre


    'dir' could be the 'lsa' of 'ls -dhlAF -rt' and 'ls -hlAF -rt' and 'ls -rt'
        or always just 'lsrt', or both ...


    choose from the same Help Doc for
        bin/xshverb.py
        bin/xshverb.py --help


    trace what pq . chose to mean
        and accept |pq . codereviews
            and so on as explicit, concrete, specific, particular


someday


    struggle vs special tests of Gateway Verbs:  e k v, d, dt, & g

        |g p1 p2 p3
        |g p1 |g p2 |g p3
        |pq 'g p1' 'g p2' 'g p3'

            these input costs are assymetric

        pq 'dt lsa' 'g drwx' 'c '
        pq 'dt echo here' 'pq e' 'dto echo there'

        by placement

            outside of pipe
                e k v, d, dt, & g have clear meanings
                and even 'g' goes as 'pbpaste |g ... |pbcopy'

            left of pipe
                e| k| v| might want identifier args
                d| might want identifier args
                dt| might want identifier args
                g| does want identifier args

            in the pipe
                |e| |k| |v| don't want identifier args
                |d| should become |diff a -|
                |dt| helps lots in sequential pipes
                |g ...| does want identifier args

                except |k ...| and |k ...
                    these with identifier args
                        could be |less and |tee

            right of pipe
                |d should become |diff a -
                |g does want identifier args
                |g wants to end with |cat -

        g = more special when rightmost
        e k v, d = more special when leftmost

        e k v don't need the non-identifier args when in the pipe
        d has no role in the pipe

        |g should imply |g c, because it is last

        maybe -- is some kind of toggle
        g means:  -- g

        pq -- a 1 -- e gateway.txt --
            is explicit for:  pq a 1 e gateway.txt


later


    beyond pq urrlib
        pq . rstrip to drop the k1=v1&k2=v2
            pq . rstrip again to drop the trailing /


    getfqdn = socket.getfqdn()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Google DNS
    getsockname = s.getsockname()  # ('8.8.8.8', 80)
    s.close()


    come reduce confusion over past and future pq, such as wrong host past pq saying

        pq
            could mention '+ pbpaste'
        vs wrong @

            % pq v
            Pq today defines a, c, f, h, n, s, t, u, x
            Pq today doesn't define b, d, e, g, i, j, k, l, m, o, p, q, r, v, w, y, z
            %

    pq python names to call them in order on each iline etc

    p arbitrary python expression on each iline etc


    sync ~/.vimrc ~/.emacs ~/.bashrc etc


    'uptime.py --' for uptime.py --pretty
