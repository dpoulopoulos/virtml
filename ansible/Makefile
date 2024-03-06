DEFAULT_ARGS = -i hosts.yaml -i state.ini

ANSIBLE_DIFF ?= --diff

all:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) site.yaml

check:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --check site.yaml

qemu:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --tags qemu-vm site.yaml
