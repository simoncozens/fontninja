import argparse
import fontninja.build
import fontninja.plumbing
import sys

parser = argparse.ArgumentParser(description='Font builder')

if sys.argv[1] == "--plumbing":
	del sys.argv[1]
	fontninja.plumbing.run(parser)
else:
	fontninja.build.run(parser)
