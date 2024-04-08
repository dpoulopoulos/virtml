# Create a Debian VM

This guide walks you through creating a new VM using `libvirt` and installing Debian on it. This is
the VM that you will later use as a PXE server to boot the Kubernetes nodes.

## What you'll need

To complete this guide, you will need the following:

* A Debian-based system.
* A working [QEMU/KVM installation](qemu-kvm).

## Procedure

Follow the steps below to create a new VM and install Debian on it.

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
    Replace `/home/user/virtlml` with the path to the project's root directory.
    ```

1. Create a new `QCOW2` virtual disk for the VM:

    ```console
    root:/home/user/virtlml# qemu-img create -f qcow2 /var/lib/libvirt/images/pxe-server.qcow2 32G
    Formatting '/var/lib/libvirt/images/pxe-server.qcow2', fmt=qcow2 cluster_size=65536 extended_l2=off compression_type=zlib size=34359738368 lazy_refcounts=off refcount_bits=16
    ```

1. Define a new VM, using the XML file inside the `infra` directory:

    ```console
    root:/home/user/virtlml# virsh define --file infra/pxe-server.xml
    Domain 'pxe-server' defined from pxe-server.xml
    ```

    ```{note}
    The `pxe-server.xml` file is a template for the PXE server VM. You can modify it to fit your
    needs. Pay close attention to the sections where you specify the path to the `QCOW2` file and
    the Debian `12.4` ISO.
    ```

1. Start the PXE server VM:

    ```console
    root:/home/user/virtlml# virsh start pxe-server
    Domain 'pxe-server' started
    ```

1. Connect to the PXE server VM through the "Virtual Machine Manager" UI and run the Debian
   installer. The Debian installer will guide you through the installation process. You can use the
   default settings for most of the options.

    ```console
    root:/home/user/virtlml# virt-manager
    ```

    ```{note}
     We recommend doing a minimal installation of Debian, without any graphical interface.
    ```

## Verify

1. Verify that the VM is running:

    ```console
    root:/home/user/virtlml# virsh list --all
    Id   Name         State
    -----------------------------
    1    pxe-server   running
    ```

1. Change back to your user:

    ```console
    root:/home/user/virtlml# exit
    user:~/virtlml$
    ```

1. Create an SSH key, if you don't already have one:

    ```console
    user:~/virtlml$ ssh-keygen
    ```

1. Copy the SSH public key to the PXE server VM:

    ```console
    user:~/virtlml$ ssh-copy-id user@pxe-server
    ```

    ```{note}
    Replace `user` with your username. Also, replace `pxe-server` with the IP address of the VM.
    Alternatively, you can add an entry to your `/etc/hosts` file with the IP address and hostname
    of the VM.
    ```

1. Verify that you can SSH into the PXE server VM:

    ```console
    user:~/virtlml/infra$ ssh user@pxe-server
    The authenticity of host '192.168.122.89 (192.168.122.89)' can't be established.
    ED25519 key fingerprint is SHA256:dNnHdISPbUDbtJWqSLDpEdGEO3tGEIQ1TiSrfPxyRHg.
    This key is not known by any other names.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    Warning: Permanently added '192.168.122.89' (ED25519) to the list of known hosts.
    dimpo@192.168.122.89's password: 
    Linux pxe-server 6.1.0-17-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.69-1 (2023-12-30) x86_64

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Wed Feb  7 18:10:32 2024
    user@pxe-server:~$
    ```

    ```{note}
    Replace `user` with your username and `pxe-server` with the IP address of the PXE server VM.
    ```

    ```{important}
    You should add your SSH public key to the authorized keys list of the root user on the PXE
    server VM. This is something that you will need later, as you should be able to SSH into the
    PXE server VM as the root user.
    ```
