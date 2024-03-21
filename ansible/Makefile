DEFAULT_ARGS = -i inventory/hosts.yaml -i inventory/state.ini

ANSIBLE_DIFF ?= --diff

check:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) --check cluster.yaml

kubernetes:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) cluster.yaml

# Use `--limit=NODE_NAME` to avoid disturbing other nodes in the cluster.
# Before using `--limit` run facts.yaml without the limit to refresh facts cache
# for all nodes:
# https://kubespray.io/#/docs/nodes?id=_2-run-scaleyml
add-node:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) facts.yaml
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) add-k8s-node.yaml --limit=$(node)
