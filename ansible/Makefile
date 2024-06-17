DEFAULT_ARGS = -i inventory/hosts.yml

# Set this to the empty strin, to disable diff mode (on by default)
ANSIBLE_DIFF ?= --diff

all-check:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) --check site.yml

all:
	ansible-playbook $(ANSIBLE_ARGS) $(ANSIBLE_DIFF) $(DEFAULT_ARGS) site.yml
