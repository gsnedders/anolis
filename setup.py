from distutils.core import setup

setup(name = "specGen",
	license="""MIT""",
	version = "1.0b2",
	author = "Geoffrey Sneddon",
	author_email = "geoffers@gmail.com",
	packages = ["specGen", "specGen/processes"],
	scripts = ["spec-gen"],
	)
