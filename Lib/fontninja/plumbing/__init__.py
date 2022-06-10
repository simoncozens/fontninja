from .cu2qu import Cu2Qu
from .writefeatures import WriteFeatures
from .compilefeatures import CompileFeatures
from .decomposemixed import DecomposeMixed
from .ufo2ttf import Ufo2Ttf

commands = {
	"compilefeatures": CompileFeatures,
	"writefeatures": WriteFeatures,
	"decompose-mixed": DecomposeMixed,
	"cu2qu": Cu2Qu,
	"ufo2ttf": Ufo2Ttf
}

def run(parser):
	parser.description = "Font builder (low-level)"
	subparsers = parser.add_subparsers()
	for command, impl in commands.items():
			subparser = subparsers.add_parser(command)
			impl.setup_parser(subparser)
			subparser.set_defaults(func=impl.run)
	args = parser.parse_args()
	args.func(args)

def setup_ninja_rules(writer):
	writer.comment("Rules\n")
	for command, impl in commands.items():
		writer.comment(impl.__doc__)
		writer.rule(command, f"python3 -m fontninja --plumbing {command} $args $in $out")
		writer.newline()
