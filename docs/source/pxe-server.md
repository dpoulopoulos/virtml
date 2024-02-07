# Configure a Debian PXE server

This guide will help you to configure a PXE server to boot the control-plane and worker nodes of a
Kubernetes cluster.

🚧 🚧 🚧 This is Work-in-Progress. 🚧 🚧 🚧

## Step 1: Create a VM for the PXE server on KVM

In this section you will create a KVM VM for the PXE server, using a Debian `12.4` image.

### What you'll need

* A machine with KVM installed.
* A Debian `12.4` ISO. You can download it from the [official Debian website](https://www.debian.org/distrib/netinst).

### Procedure

1. Change to root user:

    ```console
    user:~$ sudo su -
    root:~#
    ```

1. Navigate to the project's root directory:

    ```console
    root:~# cd kubeflow-on-kvm
    ```

1. Create a new `QCOW2` virtual disk for the VM:

    ```console
    root:~/kubeflow-on-kvm# qemu-img create -f qcow2 /var/lib/libvirt/images/pxe-server.qcow2 32G
    Formatting '/var/lib/libvirt/images/pxe-server.qcow2', fmt=qcow2 cluster_size=65536 extended_l2=off compression_type=zlib size=34359738368 lazy_refcounts=off refcount_bits=16
    ```

1. Define a new VM for the PXE server, using the XML file inside the `infra` directory:

    ```console
    root:~/kubeflow-on-kvm# cd infra
    root:~/kubeflow-on-kvm/infra# virsh define pxe-server.xml
    Domain 'pxe-server' defined from pxe-server.xml
    ```

    > **Note**: The `pxe-server.xml` file is a template for the PXE server VM. You can modify it to
    > fit your needs. Pay close attention to the sections where you specify the path to the
    > `QCOW2` file and the Debian `12.4` ISO.

1. Start the PXE server VM:

    ```console
    root:~/kubeflow-on-kvm/infra# virsh start pxe-server
    Domain 'pxe-server' started
    ```

1. Connect to the PXE server VM through the "Virtual Machine Manager" UI and run the Debian
   installer. The Debian installer will guide you through the installation process. You can use the
   default settings for most of the options.

### Verify

1. Verify that the PXE server VM is running:

    ```console
    root:~/kubeflow-on-kvm/infra# virsh list --all
    Id   Name         State
    -----------------------------
    1    pxe-server   running
    ```

1. Change back to your user:
    
    ```console
    root:~/kubeflow-on-kvm/infra# exit
    user:~/kubeflow-on-kvm/infra$
    ```

1. Verify that you can SSH into the PXE server VM:

    ```console
    user:~/kubeflow-on-kvm/infra$ ssh user@pxe-server
    Linux pxe-server 6.1.0-17-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.69-1 (2023-12-30) x86_64

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Wed Feb  7 16:43:02 2024 from 192.168.1.1
    ```

    > **Note**: Replace `user` with your username and `pxe-server` with the IP address of the PXE
    > server VM.

