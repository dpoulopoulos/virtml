DEFAULT_ARGS = -i hosts.yaml

ANSIBLE_DIFF ?= --diff

all:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) site.yaml

check:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --check site.yaml
