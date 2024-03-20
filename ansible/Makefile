DEFAULT_ARGS = -i inventory/hosts.yaml -i inventory/state.ini

ANSIBLE_DIFF ?= --diff

check:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --check cluster.yaml

kubernetes:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) cluster.yaml
