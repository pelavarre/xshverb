things to do, futures to build

soon

    $ k
    + less -FIRX 3878492-xshverb.pbpaste
    3878492-xshverb.pbpaste: No such file or directory
    + exit 1
    $

    getfqdn = socket.getfqdn()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Google DNS
    getsockname = s.getsockname()  # ('8.8.8.8', 80)
    s.close()

    v a
    assert not drained

    % pq |head -1
    BrokenPipeError: [Errno 32] Broken pipe

    v
        should edit pbpaste

    reduce confusion over past and future pq, such as wrong host past pq saying

        pq
            should pbpaste

        wrong @

            % pq v
            Pq today defines a, c, f, h, n, s, t, u, x
            Pq today doesn't define b, d, e, g, i, j, k, l, m, o, p, q, r, v, w, y, z
            %

    pq fmt
        should leave the PBuffer untouched, not emptied

    |g should imply |g c, because it is last
        maybe -- is some kind of toggle
        g means:  -- g

    |pq| didn't scrub out the destructive unprintable control codes, from Sh Screen
    |pq expand| didn't either

    fix many bugs of
        $ : tac && fh |pq r |pq 'uniq --keys' |r |grep press |grep -iv PLaVarre

    choose from the same Help Doc for
        bin/xshverb.py
        bin/xshverb.py --help

later

    trace what pq . chose to mean
        and accept |pq . codereviews
            and so on as explicit, concrete, specific, particular

    pq python names to call them in order on each iline etc

    p arbitrary python expression on each iline etc

    beyond pq urrlib
        pq . rstrip to drop the k1=v1&k2=v2
            pq . rstrip again to drop the trailing /

    sync ~/.vimrc ~/.emacs ~/.bashrc etc

    'uptime.py --' for uptime.py --pretty

    grep ~/e, but without the unprintables
