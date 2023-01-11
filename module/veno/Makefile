custom_module_name = tcp_veno

obj-m += $(custom_module_name).o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

insert:
	insmod $(custom_module_name).ko

remove:
	rmmod $(custom_module_name).ko
