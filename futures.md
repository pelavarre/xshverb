things to do, futures to build

3/Oct

    Smooth the production of:  ~/Desktop/Pastebuffer 2025-10-03 at 17:04.txt

30/Sep

    Vim !!
        |a 1

16/Sep

    |pq yaml should pretty-print it

    |pq watch should work to show a date/time-stamp'ed log of changes

6/Sep

    pq dedent should imply expandtab

    ??

        % cd bin/
        % python3 -c 'import plus; print(plus.__file__)'
        /Users/plavarre/Public/xshverb/bin/plus.py
        % p
        >>> import plus
        Traceback (most recent call last):
          File "<python-input-0>", line 1, in <module>
            import plus
        ModuleNotFoundError: No module named 'plus'
        >>>

yah later still

    touch.py --mkdirs

    pq
    both dumps and dedents - ouch, wrong

more lately

    v exit 1

    dt broke somehow

        % dt echo a b c
        2025-08-28 17:53:14 -0700  (2025-08-29 00:53:14.345781)  enter
        + echo a b c
        + exit 0
        2025-08-28 17:53:14 -0700  (2025-08-29 00:53:14.358182)  exit
        12ms401us
        %

lately

    make a kind of dt that just does elapsed and not before/after
        like for our 'dt :' triggered by 'ssh-add -D'

    paragraph-break's and a __pycache__ archive for:  dt ...

    macOS Terminal launch profile could eat the first .py delay
        try:  python3 /dev/null

    qsis could wc -l its __pycache__ mentions

    $ touch a b && d <(cat a |sed 's,p,x,g') <(cat b |sed 's,q,x,g')
    + diff -brpu /dev/fd/63 /dev/fd/62
    diff: /dev/fd/63: No such file or directory
    diff: /dev/fd/62: No such file or directory
    $

    $ diff -brpu a b
    $

    $ touch a b && python3 -c 'import os, sys; print(open(sys.argv[-2]), open(sys.argv[-1]))' <(cat a |sed 's,p,x,g') <(cat b |sed 's,q,x,g')
    <_io.TextIOWrapper name='/dev/fd/63' mode='r' encoding='UTF-8'> <_io.TextIOWrapper name='/dev/fd/62' mode='r' encoding='UTF-8'>
    $

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


    pq . address should gracefully accept its work done already
        likewise pq . title
        maybe also . codereviews, . google. . jenkins, . jira


    struggle vs special tests of Gateway Verbs:  e k v, d, dt, & dot g

        |g p1 p2 p3
        |g p1 |g p2 |g p3
        |pq 'g p1' 'g p2' 'g p3'

            these input costs are assymetric

        pq 'dt lsa' 'g drwx' 'c '
        pq 'dt echo here' 'pq e' 'dto echo there'

        usage by placement

            |dot doesn't care, always wants indentifier args

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

    > order by name, date or size
        I felt computing went through some kind of shift here, as we crossed into this new century?
        Once storage became so cheap for me, then >> Order by Date Added
        << became the default I nearly always want as I work inside the
        Terminal, as if macOS 'ls -ltrU ' or Linux 'ls -ltr --time=birth'
