import argparse
import fontninja.build
import fontninja.plumbing
import sys

def main():
	parser = argparse.ArgumentParser(description='Font builder')

	if len(sys.argv) > 1 and sys.argv[1] == "--plumbing":
		del sys.argv[1]
		fontninja.plumbing.run(parser)
	else:
		fontninja.build.run(parser)

if __name__ == "__main__":
	main()
