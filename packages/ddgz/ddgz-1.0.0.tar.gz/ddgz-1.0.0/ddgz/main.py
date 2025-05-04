import argparse

import ddgr
import fzf

PARSER = argparse.ArgumentParser(description='Search duckduckgo, select result with fzf and write result to stdout')
PARSER.add_argument('query', nargs="*")
args = PARSER.parse_args()


def main():
    opts = ddgr.parse_args(args.query)
    ddgr.DdgCmd.colors = []
    cmd = ddgr.DdgCmd(opts, "ddgz")
    cmd.fetch()
    chosen, = fzf.fzf([r.title for r in cmd.results])
    print(cmd.results[chosen.index].url)
