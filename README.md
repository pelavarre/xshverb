<!-- omit in toc -->
# xshverb

Contents

- [Welcome](#welcome)
- [23 is just barely enough](#23-is-just-barely-enough)
- [Arguments that don't begin with a Dash '-'](#arguments-that-dont-begin-with-a-dash--)
  - [Punctuated Arguments](#punctuated-arguments)
  - [Regular Expressions Unions](#regular-expressions-unions)
- [Run ahead despite unusual Bytes](#run-ahead-despite-unusual-bytes)
- [Bugs dropped, not kept up](#bugs-dropped-not-kept-up)
  - [|awk -vOFS=$'\\x0A'](#awk--vofsx0a)
  - [|awk -vOF=:](#awk--vof)
  - [|grep -e=O -e=U](#grep--eo--eu)
  - [|grep hello](#grep-hello)
  - [|sort](#sort)
  - [|sort -n](#sort--n)
  - [|uniq](#uniq)
  - [|uniq -c](#uniq--c)
- [Future work](#future-work)
- [Past work](#past-work)
- [Up online](#up-online)

<!-- I'd fear people need the headings numbered, if it were just me -->
<!-- VsCode autogenerates this unnumbered Table-of-Contents. Maybe people will cope -->

## Welcome

Let's make it easy for you to tell your Terminal Shell
to show you the most common words in a Git Commit

    git show |i  u  s -nr  h  c

While you're still building your trust in us,
type one Y and a Space in front of the other letters
to have us say what we'll do, before you agree to have us to do it

    $ git show |y  i  u  s -nr  h  c

    + |p split |p sort |p counter |p sort -nr |p head |cat -

    >> Press ⌃D to run, or ⌃C to quit <<

Type a Y and a Space and another Y and another Space
when you need to see the full details of how far behind the times
the classic 1970s work of Terminal Shell designs has fallen

    $ git show |y  y  i  u  s -nr  h  c

    + |tr ' \t' '\n' |grep . |LC_ALL=C sort |uniq -c |expand |LC_ALL=C sort -nr |head -$((LINES / 3)) |cat -

    >> Press ⌃D to run, or ⌃C to quit <<

For sure you can spell out all this detail,
to build out a purely classic Shell Pipe that does its work adequately well.
But, uhh, odds on you mostly don't want to. I mean look at what it takes, nowadays

And you can't even correctly expand |u as '|LC_ALL=C sort |uniq -c |expand'
except when it is followed by a |sort such as our '|LC_ALL=C sort -nr' here

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

    git show |i  u  s -nr  h  c

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
+ |g is for **Grep**, but with Py RegEx, and default to '-i -F' and fill in the '-e' per Arg
+ |h is for **Head**, but fill a third of the Terminal, don't always stop at just 10 Lines
+ |i is for **Py Str Split**, the inverse of |x
+ |j is for **Json Query**, but don't force you to install Jq and turn off sorting the keys
+ |k is for **Less** of the '|less -FIRX' kind because |l and |m were taken
+ |l is for **Ls** of the '|ls -dhlAF -rt' kind, not more popular less detailed '|ls -CF'
+ |m is for **Make**, but timestamp the work and never print the same Line twice
+ |n is for **NL** with the '|cat -n |expand' index, whereas |n -0 is '|nl -v0 |expand'
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
after you perfectly memorize far too many workarounds,
or if you distribute your own fresher versions of them


### |awk -vOFS=$'\x0A'

Classic Awk refuses to take a Line-Break as its Output Separator

    % echo a b c |awk -vOFS=$'\x0A' 1
    awk: newline in string
    ... at source line 1
    %


### |awk -vOF=:

Classic Awk doesn't autocorrect nor check the spelling of -vOFS=,
and spells the far more common -F=ISEP wildly differently from the rare -vOFS=

    % echo a b c |awk -vOFS=: '{print $1, $2, $3}'
    a:b:c
    % echo a b c |awk -vOF=: '{print $1, $2, $3}'
    a b c
    %


### |grep -e=O -e=U

Classic Grep takes this as a search for '=O' and '=U', not as a search for 'O' and 'U'

    % echo 'O U =O =U' |tr ' ' '\n' |grep -e=O -e=U
    =O
    =U
    %


### |grep hello

Classic Grep takes this as a search for a pattern
that fails to match if the reality differs only in case

    % echo HELLO Hello hello |tr ' ' '\n' |grep hello
    hello
    %


### |sort

Classic Sort takes this as a sort by the locale's collation order,
unlike

    |LC_ALL=C sort


### |sort -n

Classic Sort Numeric drops the Exponents of Float Literals,
as if you needed speed more than accuracy,
unlike

    |sort -g

Classic Sort Numeric sorts the Lines not prefixed by a Number as if prefixed by 0

This comes as Nulls Last when sorting descending without negative numbers, and I like that.
But coming out mixed with the zeroes in the middle of negative and positive numbers makes no sense?
Like are they slapping you for forcing them to think through a corner case they dislike?

Maybe our whole industry gets confused in this?
They tell me Python Sorts do sort NaN indeterminately, as never meaningfully comparable.
NumPy Sorts that sort NaN as always Nulls Last and never as Nulls First.
Pandas Sorts that default to Nulls Last but can do .na_position='first'
Maybe they don't much test with ordinary living people around?

We sort Nulls Last

To get there in classic Shell, you've got to go separate your Lines prefixed by a Number or not.
Tactics such as

    |expand |grep -v '^ *[-+.0-9]'


### |uniq

Classic Uniq requires a Sort before you drop the Duplicates,
unlike

    |awk '!d[$0]++'


### |uniq -c

Classic Uniq takes this as a request to inject quasi-binary \x09 Hard Tabs into the output,
unlike

    |uniq -c |expand


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
