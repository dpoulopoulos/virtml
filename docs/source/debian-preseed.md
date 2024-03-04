# Deploy Debian on KVM

This guide walks you through deploying a VM with Debian 12 (Bookworm), on KVM. Moreover, you will
learn how to use a [preseed](https://wiki.debian.org/DebianInstaller/Preseed) file to automate the
deployment of Debian 12 on any VM.

## Step 1: Define the Worker VM

In this section, you define a new worker VM for your Kubernetes cluster. We will use this as a use
case. Then, you can deploy the rest of your VMs (e.g., a control plane, another worker, etc.) using
exactly the same process.

### What you'll need

* A working [QEMU/KVM installation](qemu-kvm).
* A configured [PXE Server](pxe-server).

### Procedure

1. Change to root user:

    ```console
    user:~$ sudo su -
    root:~#
    ```

1. Navigate to the project's root directory:

    ```console
    root:~# cd /home/user/kubeflow-on-kvm
    ```

    > **Note**: The path `/home/user/kubeflow-on-kmv` is an example. Change it to reflect your
    > working environment.

1. Create a new `QCOW2` virtual disk for the VM:

    ```console
    root:/home/user/kubeflow-on-kvm# qemu-img create -f qcow2 /var/lib/libvirt/images/worker-1.qcow2 256G
    Formatting '/var/lib/libvirt/images/pxe-server.qcow2', fmt=qcow2 cluster_size=65536 extended_l2=off compression_type=zlib size=34359738368 lazy_refcounts=off refcount_bits=16
    ```

1. Define a new worker VM, using the XML file inside the `infra` directory:

    ```console
    root:/home/user/kubeflow-on-kvm# virsh define --file infra/worker-1.xml
    Domain 'pxe-server' defined from pxe-server.xml
    ```

    > **Note**: The `pxe-server.xml` file is a template for the PXE server VM. You can modify it to
    > fit your needs. Pay close attention to the sections where you specify the path to the
    > `QCOW2` file and the Debian `12.4` ISO.

### Verify

1. List the VMs you have defined:

    ```console
    root:/home/user/kubeflow-on-kvm# virsh --list --all
    Id   Name         State
    -----------------------------
    1    pxe-server   running
    -    worker-1     shut off
    ```

## Step 2: Configure the PXE Server

In this section, you will configure your PXE Server to repond to request from this specific VM. To
achieve this, you will use the MAC address of your newly created machine.

### What you'll need

* The MAC address of a defined worker VM

### Procedure

1. Change back to your user:

    ```console
    root:/home/user/kubeflow-on-kvm# exit
    user:~$
    ```

1. Navigate to your project's directory:

    ```console
    user:~$ cd kubeflow-on-kvm
    ```

    > **Note**: The path `~/kubeflow-on-kmv` is an example. Change it to reflect your working
    > environment.

1. Decide on login credentials for the `root` user of new worker VM:

    ```console
    user:~/kubeflow-on-kvm$ export ROOTPW_HASH=$(openssl passwd -6)
    ```

1. Render the preseed file:

    ```console
    user:~/kubeflow-on-kvm$ j2 infra/preseed.cfg.j2 > preseed.cfg
    ```

1. Copy the preseed file onto the PXE Server:

    ```console
    user:~/kubeflow-on-kvm$ scp preseed.cfg root@pxe-server:/srv/tftp/preseed.cfg
    ```

1. Decide on the IP address and the hostname of the worker VM:

    a. Set the VM's IP address:

    ```console
    user:~/kubeflow-on-kvm$ export CLIENT_IP=192.168.1.16
    ```

    b. Set the VM's MAC address:

    ```console
    user:~/kubeflow-on-kvm$ export CLIENT_MAC=52:54:00:fd:b9:8b
    ```

    c. Set the VM's hostname:

    ```console
    user:~/kubeflow-on-kvm$ export CLIENT_HOSTNAME=worker-1
    ```

1. Render the `dnsmasq` configuration:

    ```console
    user:~/kubeflow-on-kvm$ j2 infra/dnsmasq.conf.j2 > dnsmasq.conf-01-${CLIENT_MAC//:/-}
    ```

1. Copy the configuration file onto the PXE Server:

    ```console
    user:~/kubeflow-on-kvm$ scp dnsmasq.conf-01-52-54-00-fd-b9-8b root@pxe-server:/etc/dnsmasq.d/dnsmasq.conf-01-52-54-00-fd-b9-8b
    ```

1. Connect to the PXE Server:

    ```console
    user:~/kubeflow-on-kvm$ ssh root@pxe-server
    ```

1. Restart the `dnsmasq` service:

    ```console
    root@pxe-server:~# systemctl restart dnsmasq
    ```

1. Log out the PXE Server:

    ```console
    root@pxe-server:~# exit
    ```

## Step 3: Start the worker VM

In this final section, you will start the worker VM and watch as it boots from the network and
installs Debian automatically.

### What you'll need

* A defined worker VM.
* A configured PXE Server, ready to respond to DHCP discover requests from a spcific MAC address.

### Procedure

1. Change to root user:

    ```console
    user:~$ sudo su -
    root:~#
    ```

1. Start the worker VM:

    ```console
    root:~# virsh start worker-1
    Domain 'worker-1' started
    ```

### Verify

1. Connect to the PXE server VM through the "Virtual Machine Manager" UI and watch as the Debian
   installer automatically installs the OS, without any human intervention.

    ```console
    root:/home/user/kubeflow-on-kvm# virt-manager
    ```
