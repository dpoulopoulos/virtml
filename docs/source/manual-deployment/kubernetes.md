# Deploy Kubernetes

In this section, you will learn how to deploy a Kubernetes cluster using [kubespray](https://github.com/kubernetes-sigs/kubespray).
Now that you have a few VMs running, you can use them as targets for the Kubernetes cluster.

Kubespray is a set of Ansible playbooks that you can use to deploy a Kubernetes cluster. It is
designed to be used in a variety of environments, including bare metal, virtual machines, and cloud
providers. In this case, you will use it to deploy a Kubernetes cluster on VMs running on your local
machine.

## What you'll need

To complete this guide, you will need the following:

* A set of running VMs. You can use the [VMs](debian-preseed) you created in the previous sections.

## Procedure

Follow the steps below to deploy a Kubernetes cluster:

1. Clone the kubespray repository:

    ```console
    user:~$ git clone https://github.com/kubernetes-sigs/kubespray.git
    ```

1. Change to the kubespray directory:

    ```console
    user:~$ cd kubespray
    ```

1. Copy the `inventory/sample` file as `inventory/mycluster`:

    ```console
    user:~/kubespray$ cp -rfp inventory/sample inventory/mycluster
    ```

1. Update the Ansible inventory file using the inventory builder script:

    ```console
    user:~/kubespray$ declare -a IPS=(10.10.1.3 10.10.1.4 10.10.1.5 10.10.1.6)
    ```

    ```{note}
    Replace the IP addresses with the ones of your VMs.
    ```

    ```console
    user:~/kubespray$ CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
    ```

1. Review and change parameters under `inventory/mycluster/group_vars`:

    ```console
    user:~/kubespray$ cat inventory/mycluster/group_vars/all/all.yml
    ```

    ```console
    user:~/kubespray$ cat inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml
    ```

1. Deploy Kubespray with Ansible Playbook:

    ```console
    user:~/kubespray$ ansible-playbook -i inventory/mycluster/hosts.yaml --user=root cluster.yml
    ```

    ```{note}
    This command will deploy a Kubernetes cluster on the VMs you specified in the inventory file.
    ```

## Verify

Follow the steps below to verify the Kubernetes deployment:

1. Verify that the Kubernetes cluster is up and running:

    ```console
    user:~/kubespray$ kubectl get nodes
    NAME       STATUS   ROLES           AGE   VERSION
    node1      Ready    control-plane   1m    v1.29.3
    node2      Ready    control-plane   1m    v1.29.3
    node3      Ready    <none>          1m    v1.29.3
    node4      Ready    <none>          1m    v1.29.3
    ```

    ```{note}
    The output should show the nodes in the cluster and their status. What you care about is that all
    nodes are `Ready`.
    ```
