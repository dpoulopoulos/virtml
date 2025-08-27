DEFAULT_ARGS = -i inventory/hosts.yml -i inventory/state.ini

# Set this to the empty string, to disable diff mode (on by default)
ANSIBLE_DIFF ?= --diff

vms-check:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) --check site.yml

vms:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) site.yml

k8s-check:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) --check cluster.yml

k8s:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) cluster.yml
