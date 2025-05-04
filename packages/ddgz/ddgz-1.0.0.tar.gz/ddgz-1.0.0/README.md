# ddgz
**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined
)[⚡️](https://readwithai.substack.com/s/technical-miscellany)[🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

Duckduckgo search using fzf. This is a wrapper around the duckduckgo command-line util [ddgr](https://github.com/jarun/ddgr) which uses the fuzzy search tool, [fzf](https://github.com/junegunn/fzf), to select a result and then writes the url of the result to standard output.


# Attribution
This tool is effectively a thin wrapper around [ddgr](https://github.com/jarun/ddgr) and [python fzf](https://github.com/nk412/pyfzf)

# Installation
```
pipx install ddgz
```

# Usage
```
ddgz hello world
```

You likely want to use the result, my motivation was to place it on the clipboard while editing documents, for which I use this.

```
ddgz | xclip -selection clipboard -i
```

I personally define a snippet (which I call `ddcli`) for the above using my zsh snippet manager [zshnip](https://github.com/facetframer/zshnip).


# Alternatives and prior work
ddgr can output results to JSON, this can be used for arbitrary purposes.

I tried to find tools to search google. I found [googler](https://github.com/jarun/googler) but this was deprecated and I could not install this with [pipx](https://github.com/pypa/pipx)


# About me
I am @readwithai, I make tools related to productivity, agency, research and reading sometimes using Obsidian.

If this is the sort of tool that interests you, then you can.

1. Follow me on [X](https://x.com/readwithai) where I tend to post about this sort of thing.
2. Check out my [list of command line productivity tools](https://readwithai.substack.com/p/my-productivity-tools)
3. Read the [Technical Miscellany](https://readwithai.substack.com/s/technical-miscellany) section of my blog

If you are interested in computer-aided reading which is my interest you might like to start with my somewhat academic [Review of note taking with Obsidian](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)
