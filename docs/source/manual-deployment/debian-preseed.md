# Deploy Debian on KVM

This guide walks you through booting a VM from the network and installing Debian 12 (Bookworm),
using a PXE server. Moreover, you will learn how to use a [preseed](https://wiki.debian.org/DebianInstaller/Preseed)
file to automate the installation of Debian 12 on any VM.

## Step 1: Define the Worker VM

In this section, you define a new VM. We will use this as a use case. Then, you can deploy any VM
you want to create a Kubernetes cluster (e.g., a control plane, another worker, etc.) using exactly
the same process.

### What you'll need

To complete this guide, you will need the following:

* A working [QEMU/KVM installation](../qemu-kvm).
* A configured [PXE Server](pxe-server).

### Procedure

Follow the steps below to define a new VM:

1. Change to root user:

    ```console
    user:~$ sudo su -
    root:~#
    ```

1. Navigate to the project's root directory:

    ```console
    root:~# cd /home/user/virtlml
    ```

    ```{note}
    Replace `/home/user/virtlml` with the path to your project's root directory.
    ```

1. Create a new `QCOW2` virtual disk for the VM:

    ```console
    root:/home/user/virtlml# qemu-img create -f qcow2 /var/lib/libvirt/images/worker.qcow2 96G
    Formatting '/var/lib/libvirt/images/worker.qcow2', fmt=qcow2 cluster_size=65536 extended_l2=off compression_type=zlib size=103079215104 lazy_refcounts=off refcount_bits=16
    ```

1. Define a new VM, using the XML file inside the `infra` directory:

    ```console
    root:/home/user/virtlml# virsh define --file infra/worker.xml
    Domain 'worker' defined from worker.xml
    ```

    ```{note}
    The `worker.xml` file is a template for the VM. You can modify it to fit your needs. Pay close
    attention to the sections where you specify the path to the `QCOW2` file.
    ```

### Verify

Verify that the VM has been defined correctly and is in the `shut off` state:

1. List the VMs you have defined:

    ```console
    root:/home/user/virtlml# virsh list --all
    Id   Name         State
    -----------------------------
    1    pxe-server   running
    -    worker       shut off
    ```

## Step 2: Configure the PXE Server

In this section, you configure your PXE Server to repond to request from this specific VM. To
achieve this, you use the MAC address of your newly created machine.

### What you'll need

To complete this guide, you will need the following:

* A defined worker VM.

### Procedure

1. Change back to your user:

    ```console
    root:/home/user/virtlml# exit
    user:~$
    ```

1. Navigate to your project's directory:

    ```console
    user:~$ cd virtlml
    ```

    ```{note}
    Replace `virtlml` with the path to your project's root directory.
    ```

1. Decide on login credentials for the `root` user of new worker VM:

    ```console
    user:~/virtlml$ export ROOTPW_HASH=$(openssl passwd -6)
    ```

1. Export your public SSH key:

    ```console
    user:~/virtlml$ export SSH_KEY=$(cat ~/.ssh/id_rsa.pub)
    ```

1. Render the preseed file:

    ```console
    user:~/virtlml$ j2 infra/preseed.cfg.j2 > preseed.cfg
    ```

1. Copy the preseed file onto the PXE Server:

    ```console
    user:~/virtlml$ scp preseed.cfg root@pxe-server:/srv/tftp/preseed.cfg
    ```

1. Decide on the IP address and the hostname of the worker VM:

    a. Set the VM's IP address:

    ```console
    user:~/virtlml$ export CLIENT_IP=192.168.1.16
    ```

    b. Set the VM's MAC address:

    ```console
    user:~/virtlml$ export CLIENT_MAC=$(virsh dumpxml worker | grep "<mac address=" | awk -F"'" '{print $2}')
    ```

    c. Set the VM's hostname:

    ```console
    user:~/virtlml$ export CLIENT_HOSTNAME=worker
    ```

1. Render the `dnsmasq` configuration:

    ```console
    user:~/virtlml$ j2 infra/dnsmasq.conf.j2 > dnsmasq.conf-01-${CLIENT_MAC//:/-}
    ```

1. Copy the configuration file onto the PXE Server:

    ```console
    user:~/virtlml$ scp dnsmasq.conf-01-<CLIENT_MAC> root@pxe-server:/etc/dnsmasq.d/dnsmasq.conf-<CLIENT_MAC>
    ```

    ```{note}
    The `<CLIENT_MAC>` suffix is the MAC address of the worker VM.
    ```

1. SSH into the PXE server VM:

    ```console
    user:~/virtlml$ ssh user@pxe-server
    ```

    ```{note}
    Replace `user` with your username. Also, replace `pxe-server` with the IP address of the VM.
    Alternatively, you can add an entry to your `/etc/hosts` file with the IP address and hostname
    of the VM.
    ```

1. Change to root user:

    ```console
    user@pxe-server:~$ sudo su -
    root@pxe-server:~#
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

In this final section, you start the worker VM and watch as it boots from the network and installs
Debian automatically.

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
    root:~# virsh start worker
    Domain 'worker' started
    ```

### Verify

1. Connect to the worker VM through the "Virtual Machine Manager" UI and watch as the Debian
   installer automatically installs the OS, without any human intervention.

    ```console
    root:/home/user/virtlml# virt-manager
    ```
