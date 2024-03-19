DEFAULT_ARGS = -i inventory/hosts.yaml -i inventory/state.ini

ANSIBLE_DIFF ?= --diff

check:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --check site.yaml

all:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) site.yaml
