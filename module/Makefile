modules_names = bbr hybla infinity vegas veno westwood
modules_path = $(for x in $(modules_names); do echo "$(x)/tcp_$(x).ko"; done)


all: $(modules_path)

%.ko:
	echo $@