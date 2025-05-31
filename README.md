<!-- omit in toc -->
# xshverb

Contents

- [Highlights](#highlights)
- [Installation](#installation)
- [First Look](#first-look)
- [Welcome](#welcome)
- [Quick Install](#quick-install)
- [23 is just barely enough](#23-is-just-barely-enough)
- [Arguments that don't begin with a Dash '-'](#arguments-that-dont-begin-with-a-dash--)
  - [Punctuated Arguments](#punctuated-arguments)
  - [Regular Expressions Unions](#regular-expressions-unions)
- [Run ahead despite unusual Bytes](#run-ahead-despite-unusual-bytes)
- [Bugs dropped, not kept up](#bugs-dropped-not-kept-up)
  - [|awk -vOFS=$'\\x0A'](#awk--vofsx0a)
  - [|awk -vOF=:](#awk--vof)
  - [|awk '{print 0x123}'](#awk-print-0x123)
  - [|grep -e=O -e=U](#grep--eo--eu)
  - [|grep hello](#grep-hello)
  - [|head -0x10](#head--0x10)
  - [|sort](#sort)
  - [|sort -n](#sort--n)
  - [|tail -0x10](#tail--0x10)
  - [|uniq](#uniq)
  - [|uniq -c](#uniq--c)
- [Ancient Python](#ancient-python)
- [Past work](#past-work)
- [Future work](#future-work)
- [Up online](#up-online)

<!-- I fear people need the Headings numbered -->
<!-- but VsCode autogenerates this unnumbered Table-of-Contents. Maybe people will cope -->


## Highlights

For when typing out and running Shell Pipes inside your Terminal Window Tab Pane

Run better in 2025 by forgetting more of 1975

Say for yourself what the blanks between your words imply

Say for yourself what the blanks at the end of your every line imply


## Installation

Find a Terminal to work inside of,
with a Python from this decade in it, such as the Oct/2021 Python 3.10 of Ubuntu 2022

Install XShVerb to run once

    curl -LSsf https://raw.githubusercontent.com/pelavarre/xshverb/refs/heads/main/install.sh | sh

Or tap through to look at this Install·Sh Script first to know what it does
> https://raw.githubusercontent.com/pelavarre/xshverb/refs/heads/main/install.sh

It destroys without backup whatever you had before at ./dir/. Just so that it can run there

You can drop all the ' Single Quote marks out of it.
Those are only needed when your Social Media remakes every web address into a hotlink,
like LinkedIn and Twitter do


## First Look

Let's make it easy for you to tell your Terminal Shell
to show you the most common words in a Git Commit

    git show |i  u  s -nr  h  c

While you're still building your trust in us,
type one Y and a Space in front of the other letters
to have us say what we'll do, before you agree to have us to do it

    $ git show |y  i  u  s -nr  h  c

    + |p split |p sort |p counter |p sort -nr |p head |cat -

    >> Press ⌃D to run, or ⌃C to quit <<

Type a Y and a Space and another Y and Space
to have us speak less concisely, more conventionally, in terms of classic Shell Pipes

    $ git show |y  y  i  u  s -nr  h  c

    + |tr ' \t' '\n' |grep . |LC_ALL=C sort |uniq -c |expand |LC_ALL=C sort -nr |head -$((LINES / 3)) |cat -

    >> Press ⌃D to run, or ⌃C to quit <<

For sure you can spell out all this classic detail yourself,
to build out a merely classic Shell Pipe that does its work adequately well.
But, uhh, odds on you mostly don't want to. I mean look at what it takes, nowadays

And |u only means the '|LC_ALL=C sort |uniq -c |expand' that destroys the initial order of Lines
when it's followed by something else that more explicitly mutates order of Lines,
such as our trailing '|LC_ALL=C sort -nr' here

## Welcome

We're here to invite you to give attention to reading well the blanks between words, in the Command Lines of the Terminal Shell

Lisp people feel the blank between words should mean form a List.
Awk people feel the blank should mean append to a String.
Rexx people feel the blank should mean append to a String after appending a single Space as a Separator

We're showing the blank should change what it means by context.
Our kind of Shell Pipe has it mean send output into the next Process.
Our kind of Awk has it mean append a double Space as a stronger Separator

Download & run our work here to build better Sh Pipes for lots cheaper, out of single Letters.
As often as you don't start with the "y " prefix,
then we figure you're feeling plenty lucky,
absolutely bold enough to just try it and see what happens

We like making quick strong good Terminal Shell moves this way,
nudging us to make mistakes often enough,
frequently giving us great practice in how skillfully we recover from mistakes

I don't like people telling me it must be me who adds in the many ⇧| Shell Pipe Filter marks myself.
I'm not much a fan of typing out intricately placed and balanced combinations of ⇧" Double Quote and ' Single Quote marks.
I don't like people telling me to type more than one letter per Shell Verb.
i feel they're talking as if our now was their now of fifty years ago.
As if we want to live burdened by how things were first partly understood.
And, hello, it isn't & we don't

Have we got this idea across to you?

Now you do feel you can speak the most ordinary Shell Pipes briefly, clearly, and natively?
Want to try it out?

## Quick Install

Quick Install can look like this,
while you want closing your Terminal Tab Pane to mean Complete Uninstall

Pick a Folder to work inside of. Grab the Code.
Add as many Letters into your Sh Path as you please, at the back or at the front.
We recommend adding single Letters only at the back,
so as to leave your other operations strictly undisturbed.
Make your first Shell Pipe that you've ever made out of single letters,
and feel lucky enough to just try it

    rm -fr dir/ && mkdir -p dir/ && cd dir/ && pwd

    curl -LSsf https'://'raw'.'githubusercontent'.'com''/pelavarre/xshverb/refs/heads/main/bin/xshverb'.'py >xshverb'.'py

    wc -l xshverb'.'py  # smaller than 1000 is a download problem

    chmod +x xshverb'.'py

    for F in c h i p s u y; do ln -s $PWD/xshverb'.'py $F; done

    export PATH="$PWD:$PATH:$PWD"

    ls -l |i  u  s -nr  h  c

You get how this works?

Our same web address of the Code, formatted as a hotlink without the Shell's Single Quote marks is
https://raw.githubusercontent.com/pelavarre/xshverb/refs/heads/main/bin/xshverb.py

You definitely can drop out all our mess of Single Quote ' marks out of our install procedure,
so long as you actually don't have aggressive social media interfering here,
remaking your every other word into an irrelevant hotlink

Shell Error Messages can come at you to say the download went wrong.
We've found some corporate firewalls at work disrupt the download.
Often it works if you just try again a couple more times.
You can find your Internet outside, of course, if need be


## 23 is just barely enough

Myself,
I find our 23 basic Shell Verbs memorable
Just the greatest, most classic, Shell Pipe Filters,
but with their defaults and options rethought and corrected to fit our new century of large memories

+ |a is for **Awk**, but default to drop all but the last Column
+ |b
+ |c is for **Cat**, for when you don't want to end with '|pbcopy' & start with 'pbpaste |'
+ |d is for **Diff**, but default to '|diff -brpu a b'
+ |e is for **Emacs**, but inside the Terminal with no Menu Bar and no Splash
+ |f is for **Find**, but default to search $PWD spelled as ""
+ |g is for **Grep**, but default to '-i -F', and fill in the '-e' per Arg, and Python RegEx
+ |h is for **Head**, but fill a third of the Terminal, don't always stop at just 10 Lines
+ |i is for **Py Str Split**, the approximate inverse of the |x of XArgs meaing Py Lines Join
+ |j is for **Json Query**, but don't force you to install Jq and do turn off sorting the keys
+ |k is for **Less** of the '|less -FIRX' kind because |l and |m were taken
+ |l is for **Ls** of the '|ls -dhlAF -rt' kind, not more popular less detailed '|ls -CF'
+ |m is for **Make**, but timestamp the work and never print the same Line twice
+ |n is for **NL** with '|cat -n' of '|nl' or '|nl -v1', and |n +0 is '|nl -v0', but do '|expand'
+ |o is for **Py Lines Strip Each**, to remove leading and trailing Blanks from each Line
+ |p is for **Python**, but stop making you spell out the Imports
+ |p dedent is for Py Str TextWrap DeDent
+ |p dent is to insert 4 Spaces at the left of each Line
+ |q is for **Git**, because G was taken
+ |r is for **Py Lines Reversed**, a la Linux Tac and Mac '|tail -r'
+ |s is for **Sort**, but default to classic LC_ALL=C, same as last century
+ |t is for **Tail**, but update the classic -10 default just like |h does
+ |u is for **Uniq** Counter of the '|uniq -c |expand' kind, except don't force you to sort Lines
+ |v is for **Vi** but default to edit the Os Copy/Paste Buffer, same as at |e
+ |w
+ |x is for **XArgs**, which defaults to mean Py Lines Join, the approximate inverse of |i
+ |y is to show what's up and halt till you say move on
+ |z

We define most of the 26 a..z Letters,
but we leave '|b' and '|w' and '|z' unoccupied by us.
We leave '|w' unoccupied, because Linux & Mac so often define '|w' to mean a form of 'who'.
Even so, our '| p w' or '|p len' will give you the '|wc -l' count of Lines

In case you need to adopt this tech more slowly,

+ bin/p is for while you've not put all of a..z into your Sh Path
+ bin/pq is a 2X longer way of spelling out bin/p, but more similar to classic jq
+ bin/\\| is another 2X longer way of spelling out bin/p
+ bin/xshverb.py is a 7X longer way of spelling out bin/p

Adding '--help' as an option will also get us to say what work we'll do,
before you remove that option to agree to have us to do the work.
You can abbreviate '--help' down to '--h'.
And if you abbreviate down farther to '-h' that can work too,
but not at 'cal -h' and 'df -h' and 'du -h' and 'ls -h' and so on

My actual Shell sometimes quits on me, refusing to work with unusual bytes.
Our kind of Python runs well in place of my actual Shell,
practically never slapping me out like that


## Arguments that don't begin with a Dash '-'


### Punctuated Arguments

Besides things like

    |g -eO -eU

you can also write things like

    |g 'O|U'

    |g [OU]

This works because,
when you put punctuation into words,
we figure that you gave us these words as arguments that don't begin with a Dash '-'

Of course, we don't interfere with your Shell.
Like if you have gone and created Files named ./O and ./U,
then the 'echo g [OU]' you typed into the Shell will come to us as 'echo g O U'

If you don't like that, then you have to type it out more explicitly as

    |g '[OU]'


### Regular Expressions Unions

Classic Grep makes searching for more than one match in parallel weirdly difficult to spell out

TODO: Think more making -i -F -e into the default while keeping the rest near

For example, to search for the letter O or the letter U, you can learn to write any one of

    |grep -i -F -e O -e U

    |grep -i -F -eO -eU

    |grep -i -E 'O|U'

    |grep -i [OU]

It works, but it annoys me to type out the ' -e ' parts so often. So we also accept

    |g O,U

beyond the more direct abbreviations of only the classics

    |g -e O -e U

    |g -eO -eU

    |g 'O|U'

    |g [OU]

Sadly, the classic '|grep -e=O -e=U' means something else, and our '|g -e=O -e=U' doesn't mean that


## Run ahead despite unusual Bytes

Classic Terminal Shell Pipes choke over unusual Bytes, especially at macOS

Working in Python 3 errors="surrogateescape"
lets us work well with most forms of UnicodeDecodeError

Examples of Classic Shell gone wrong

    % echo $'\xC0\x80' |awk /./
    awk: towc: multibyte conversion failure on: '??'
    input record number 1, file
    source line number 1
    %

    % echo $'\xC0\x80' |grep .
    %


    % echo $'\xC0\x80' |sed 's,^  *,,'
    sed: RE error: illegal byte sequence
    %

    % echo $'\xC0\x80' |sort
    sort: Illegal byte sequence
    %

    % echo $'\xC0\x80' |tr ' \t' '\n'
    tr: Illegal byte sequence
    %

Python also doesn't go wild at mentions of the U+0000 Null Character

Example of Classic Shell gone wrong,
silently wrongly calling Equal for all Characters beyond the first U+0000

    % echo $'\x00Alfa' |grep -a $'\x00Bravo'
    Alfa
    %

## Bugs dropped, not kept up

Classic Terminal Shell Pipes can work just fine,
if you do perfectly memorize far too many workarounds.
Or if you distribute your own fresher versions of them


### |awk -vOFS=$'\x0A'

Classic Awk refuses to take a Line-Break as its Output Separator

    % echo a b c |awk -vOFS=$'\x0A' 1
    awk: newline in string
    ... at source line 1
    %


### |awk -vOF=:

Classic Awk doesn't autocorrect nor check the spelling of -vOFS=,
and spells the far more common -F=ISEP wildly differently from the rare -vOFS=,
and splits differently for ' ' Spaces than for other Separators

    % echo a b c |awk -vOFS=: '{print $1, $2, $3}'
    a:b:c
    % echo a b c |awk -vOF=: '{print $1, $2, $3}'
    a b c
    %

    % echo a::c:d:e |awk -F: '{print $1, $3}'
    a c
    % echo 'a  c d e' |awk -F' ' '{print $1, $3}'
    a d
    % echo 'a  c d e' |awk -F'  ' '{print $1, $3}'
    a


### |awk '{print 0x123}'

Classic Awk understands Decimal Int Literals, and shrugs off leading Zeroes,
but Binary/ Hexadecimal/ Octal Int Literals can silently suddenly mean 0 or octal or hex

Linux says 0, 8, and 16

    $ echo |awk '{print 0b1}'
    0
    $
    $ echo |awk '{print 010}'
    8
    $
    $ echo |awk '{print 0x10}'
    16
    $

macOS says 0, 10, and 0

    % echo |awk '{print 0b1}'
    0
    % echo |awk '{print 010}'
    10
    % echo |awk '{print 0x10}'
    0
    %


### |grep -e=O -e=U

Classic Grep takes '-e=' as a search for '=O' or '=U', not as a search for 'O' or 'U'

    % echo 'O U =O =U' |tr ' ' '\n' |grep -e=O -e=U
    =O
    =U
    %


### |grep hello

Classic Grep searches for your pattern,
but secretly fails to match when your reality differs only in case

    % echo HELLO Hello hello |tr ' ' '\n' |grep hello
    hello
    %


### |head -0x10

Classic Head accepts decimal, and decimal with leading zeroes, but not hex. Classic Linux Tail does the same

    % seq 99 |head -0010
    ...
    10
    %

    % seq 99 |head -0x10
    head: illegal line count -- 0x10
    %


### |sort

Classic Sort takes goes by your Locale's Collation Order

    % echo A a Z z |tr ' ' '\n' |sort
    a
    A
    z
    Z
    %

    % locale |grep ^LC_COLLATE=
    LC_COLLATE="en_US.UTF-8"
    %

Unlike our much preferred default

    |LC_ALL=C sort


### |sort -n

Classic Sort Numeric drops the Exponents of Float Literals,
as if you needed speed more than accuracy,
unlike

    |sort -g

Classic Sort Numeric sorts the Lines not prefixed by a Number as if prefixed by 0

This comes as Nulls Last when sorting descending without negative numbers, and I like that.
But coming out mixed with the zeroes in the middle of negative and positive numbers makes no sense?
Do they mean to be slapping you for forcing them to think through a corner case they dislike?

Does our whole industry gets confused in this?
People tell me Python Sorts do sort NaN indeterminately, as never meaningfully comparable.
NumPy Sorts that sort NaN as always Nulls Last and never as Nulls First.
Pandas Sorts that default to Nulls Last but can do .na_position='first'
Maybe we're not much testing operations with ordinary people involved?

We sort Nulls Last, unless you ask us to sort Nulls First

    |p sort --nulls=first

To get there in classic Shell, you've got to go separate your Lines prefixed by a Number or not.
Tactics such as

    |expand |grep -v '^ *[-+.0-9]'


### |tail -0x10

Classic Tail takes Int Literals of different bases as 0 or octal or hex

    % seq 99 -1 0 |tail -010
    ...
    7
    %

Linux Tail presently takes these differently, as decimal, or as decimal with leading zeroes, but not hex

    $ seq 99 -1 0 |tail -0010
    9
    ...
    $

    $ seq 99 -1 0 |tail -0x10
    tail: option used in invalid context -- 0
    $


### |uniq

Classic Uniq requires a Sort before you drop the Duplicates,
unlike

    |awk '!d[$0]++'


### |uniq -c

Classic Uniq takes this as a request to inject quasi-binary \x09 Hard Tabs into the output,
unlike

    |uniq -c |expand


## Ancient Python

We do make an effort to run well in the far past, even back before this decade

Can you find bugs in how we run the Jun/2018 Python 3.7?

we know we fail simply when we run the Dec/2016 Python 3.6 of Ubuntu 2018

    $ python3.6 -c 'from __future__ import annotations'
    File "<string>", line 1
    SyntaxError: future feature annotations is not defined
    $

Our emulation of running a Jun/2018 Python 3.7 is

    cp -ip ~/.bashrc ~/.bashrc~

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

    eval "$(/home/pelavarre/miniconda3/bin/conda shell.bash hook)"
    conda init
    logout

    eval "$(/home/pelavarre/miniconda3/bin/conda shell.bash hook)"
    conda create -n py370 python=3.7.0
    conda activate py370


## Past work

I figure the big variable in this effort is whether I show up on the regular, or not

It's hard for me to show up while no one else is talking,
but the chatbots do reply when I tell them to reply

I have stopped scattering my effort across multiple Repos.
This XShVerb Repo is presently my one Repo,
where I put all my work that isn't my work for hire.
GitHub will show you a dozen other Git Repos, where I've put work before now.
ByoVerbs was the my one Repo before this Repo became my one Repo, in May/2025

Next now, I'm pushing to reduce my own Sh Path down to just this one Repo

For the next time I work on Shell 'watch',
I've promised me that I'll solve just the defaults and the scrolling, nothing more for now

When I'm going for producing the most correct Code most quickly,
I write the Doc, before the Tests, before the Code,
in the way of Test Driven Design (TDD).
So if you're keeping up closely, you'll see my Tests and yours fail before they pass

Let's talk?

Tell me how it's going for you?


## Future work

Next we dream up what uppercase A..Z should mean? Or the 0..9 Digits? Or the Sh Verb 404?

1 and 2 and 3 could be Ssh Servers for work, home, and collaboration

A and B could mean ./a and ./b

E could mean ~/emojis.txt

Building out Shell Pipes as if people matter now, this is a good thing?


## Up online

Posted as:  https://github.com/pelavarre/xshverb/blob/main/README.md<br>

Questioned by:  https://twitter.com/intent/tweet?text=/@PELaVarre+XShVerb<br>

Built by:  VsCode ⇧⌘V Markdown: Open Preview<br>

Copied from:  git clone https://github.com/pelavarre/xshverb.git<br>
