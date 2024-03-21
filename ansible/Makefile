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
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) add-k8s-node.yaml --limit=$(new-node)

remove-node:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) remove-k8s-node.yaml -e node=$(old-node)

# If the node you want to remove is not online, you should add
# `reset_nodes=false` and `allow_ungraceful_removal=true` to your extra-vars:
# https://kubespray.io/#/docs/nodes?id=_3-remove-an-old-node-with-remove-nodeyml
remove-offline-node:
	ansible-playbook $(DEFAULT_ARGS) $(ANSIBLE_DIFF) remove-k8s-node.yaml -e node=$(old-node) -e reset_nodes=false -e allow_ungraceful_removal=true

# To replace a node, first add the new node to the inventory, locate the node
# to be replaced, and then run the following Make target.
replace-node: add-node remove-node
