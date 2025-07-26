things to do, futures to build

soon

    echo |e
    echo |k
    echo |v

        should take Stdin, not PbPaste


    pq fmt
        should leave the PBuffer untouched, not emptied


    grep ~/e, but without the unprintables


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

    beyond pq urrlib
        pq . rstrip to drop the k1=v1&k2=v2
            pq . rstrip again to drop the trailing /

    sync ~/.vimrc ~/.emacs ~/.bashrc etc

    'uptime.py --' for uptime.py --pretty
