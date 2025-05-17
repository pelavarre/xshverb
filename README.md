# xshverb

## Welcome

Let's make it easy for you to tell your Terminal Shell
to show you the most common words in a Git Commit

    git show |i  s  u  s -nr  h  c

While you're still building your trust in us,
type one Y and a Space in front of the other letters
to have us say what we'll do, before you agree to have us to do it

    $ git show |y  i  s  u  s -nr  h  c

    + |p split |p sort |p uniq -c --expand |p sort -nr |p head |p cat -

    >> Press ⌃D to run, or ⌃C to quit <<

Type a Y and a Space and another Y and another Space
when you need to see the full details of how far behind the times
the classic 1970s work of Terminal Shell designs has fallen

    $ git show |y  y  i  s  u  s -nr  h  c

    + |tr '\t' ' ' |sed 's,^  *,,' |sed 's,  *$,,' |tr ' ' '\n' |grep . |LC_ALL=C sort |uniq -c |expand |LC_ALL=C sort -nr |head |cat -

    >> Press ⌃D to run, or ⌃C to quit <<

For sure you can spell out all this detail,
to build out a purely classic Shell Pipe that does its work adequately well.
But, uhh, odds on you mostly don't want to. I mean look at what it takes, nowadays

Here we build better Sh Pipes for lots cheaper, out of single Letters.
As often as you don't start with the "y " prefix,
then we figure you're feeling plenty lucky,
absolutely bold enough to just try it and see what happens

We like making quick strong good Terminal Shell moves this way,
nudging us to make mistakes often enough,
frequently giving us great practice in how skillfully we recover from mistakes.
We don't like people
telling us it must be us who adds in the many ⇧| Shell Pipe Filter marks ourselves.
We don't like people
telling us to type more than one letter per Shell Verb.
They talk as if our now was their now of fifty years ago.
And, hello, it isn't

Have we got this idea across to you?

Now you do feel you can speak the most ordinary Shell Pipes briefly, clearly, and natively?
Want to try it out?

Quick Install can look like this =>
Pick a Folder to work inside of. Grab the Code.
Add as many Letters into your Sh Path as you please, at the back or at the front.
We recommend adding single Letters only at the back,
so as to leave your other operations strictly undisturbed.
Make your first Shell Pipe that you've ever made out of single letters,
and feel lucky enough to just try it

    rm -fr dir/ && mkdir -p dir/ && cd dir/ && pwd

    curl -k -LSs https'://'raw'.'githubusercontent'.'com''/pelavarre/xshverb/refs/heads/main/bin/xshverb'.'py >xshverb'.'py

    chmod +x xshverb'.'py

    head xshverb'.'py

    for F in c h i p s u y; do ln -s $PWD/xshverb'.'py $F; done

    export PATH="$PWD:$PATH:$PWD"

    git show |i  s  u  s -nr  h  c

You get how this works?

Our same web address of the Code, formatted as a simpler hotlink, is
https://raw.githubusercontent.com/pelavarre/xshverb/refs/heads/main/bin/xshverb.py

You definitely can drop out all our mess of single quote ' marks out of our install,
so long as you actually don't have aggressive social media
remaking your every other word into an irrelevant unsecured hotlink

Shell Error Messages like "zsh: command not found: 404"
or "bash: 404: command not found"
mean the download went wrong.
We've found some corporate firewalls at work disrupt the download like that
You can find your Internet outside, if need be


## 23 is just barely enough

Myself,
I find our 23 basic Shell Verbs memorable
Just the greatest, most classic, Shell Pipe Filters,
but with their defaults rethought and corrected to fit our new world of large memories

+ |a is for **Awk**, but default to drop all but the last Column
+ |b
+ |c is for **Cat**, for when you don't want to end with '|pbcopy' & start with 'pbpaste |'
+ |d is for **Diff**, but default to '|diff -brpu a b'
+ |e is for **Emacs**, but inside the Terminal with no Menu Bar and no Splash
+ |f is for **Find**, but default to search $PWD spelled as ""
+ |g is for **Grep**, but with Py RegEx, and default to '-i' and fill in the '-e' per Arg
+ |h is for **Head**, but fill a third of the Terminal, don't always stop at just 10 Lines
+ |i is for **Py Str Split**, the inverse of |x
+ |j is for **Json Query**, but don't force you to install Jq and turn off sorting the keys
+ |k is for **Less** of the '|less -FIRX' kind because |l and |m were taken
+ |l is for **Ls** of the '|ls -dhlAF -rt' kind, not more popular less detailed '|ls -CF'
+ |m is for **Make**, but timestamp the work and never print the same Line twice
+ |n is for **Number** with the '|cat -n |expand' index, whereas |n -0 is '|nl -v0 |expand'
+ |o is for **Py Line Strip**
+ |p is for **Python**, but stop making you spell out the Imports
+ |p dedent is for Py Str TextWrap DeDent
+ |q is for **Git**, because G was taken
+ |r is for **Py Lines Reversed**, a la Linux Tac and Mac '|tail -r'
+ |s is for **Sort**, but default to classic LC_ALL=C, same as last century
+ |t is for **Tail**, but update the classic -10 default just like |h does
+ |u is for **Uniq** of the '|uniq -c |expand' kind, except don't force you to sort Lines
+ |v is for **Vi** but default to edit the Os Copy/Paste Buffer, same as at |e
+ |w
+ |x is for **XArgs**, which defaults to mean Py Space List Join, the inverse of |i
+ |y is to show what's up and halt till you say move on
+ |z

We define most of the 26 a..z Letters,
but we leave '|b' and '|w' and '|z' unoccupied by us.
We leave '|w' unoccupied, because Linux & Mac so often define '|w' to mean a form of 'who'.
Even so, our '| p w' or '|p len' will give you the '|wc -l' count of Lines

In case you need to adopt this tech more slowly,

+ bin/p is for while you've not put all of a..z into your Sh Path
+ bin/\\| is a 2X longer way of spelling out bin/p
+ bin/xshverb.py is a 7X longer way of spelling out bin/p

Adding '--help' as an option will also get us to say what work we'll do,
before you remove that option to agree to have us to do the work.
You can abbreviate '--help' down to '--h'.
And if you go down farther to '-h' that can work too,
but not at 'cal -h' and 'df -h' and 'du -h' and 'ls -h' and so on

My actual Shell sometimes quits on me, refusing to work with unusual bytes.
Our kind of Python runs well in place of my actual Shell,
practically never slapping me out like that


## Future work

Next we dream up what uppercase A..Z should mean? Or the 0..9 Digits? Or the Sh Verb 404?

Building out Shell Pipes as if people matter now, this is a good thing?


## Past work

This XShVerb Repo is presently my one Repo,
where I put all my work that isn't my work for hire.
GitHub will show you a dozen other Git Repos, where I've put work before now.
ByoVerbs was the my one Repo before this Repo became my one Repo, in May/2025

I write the Doc, before the Tests, before the Code,
as my habit designed to produce the most correct Code most quickly,
in the way of Test Driven Design (TDD).
So if you're keeping up closely, you'll see my Tests and yours fail before they pass

Let's talk?

Tell me how it's going for you?


## Up online

Posted as:  https://github.com/pelavarre/xshverb/blob/main/README.md<br>
Questioned by:  https://twitter.com/intent/tweet?text=/@PELaVarre+XShVerb<br>
Built by:  VsCode ⇧⌘V Markdown: Open Preview<br>
Copied from:  git clone https://github.com/pelavarre/xshverb.git<br>
