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

1. Create a new `QCOW2` virtual disk for the VM:

    ```console
    user:~/kubeflow-on-kvm$ qemu-img create -f qcow2 ~/.local/libvirt/disks/pxe-server.qcow2 32G
    Formatting '/home/user/.local/libvirt/disks/pxe-server.qcow2', fmt=qcow2 cluster_size=65536 extended_l2=off compression_type=zlib size=34359738368 lazy_refcounts=off refcount_bits=16
    ```

1. Define a new VM for the PXE server, using the XML file inside the `infra` directory:

    ```console
    user:~/kubeflow-on-kvm$ virsh define --file infra/pxe-server.xml
    Domain 'pxe-server' defined from infra/pxe-server.xml
    ```

    > **Note**: The `pxe-server.xml` file is a template for the PXE server VM. You can modify it to
    > fit your needs. Pay close attention to the sections where you specify the path to the
    > `QCOW2` file and the Debian `12.4` ISO.

1. Start the PXE server VM:

    ```console
    user:~/kubeflow-on-kvm/infra$ virsh start pxe-server
    Domain 'pxe-server' started
    ```

    <details>
    <summary>Troubleshoot</summary>
    
    If you get the following error during the VM start process:
        
    ```console
    error: Failed to start domain 'pxe-server'
    error: /usr/lib/qemu/qemu-bridge-helper --use-vnet --br=virbr0 --fd=33: failed to communicate with bridge helper: stderr=failed to parse default acl file `/etc/qemu/bridge.conf'
    : Transport endpoint is not connected
    ```

    Make sure you have the following line in your `/etc/qemu/bridge.conf` file:

    ```console
    allow virbr0
    ```

    If the file does not exist, create it and add the line above.

    Also, make sure that the `qemu-bridge-helper` binary has the correct permissions:

    ```console
    user:~/kubeflow-on-kvm/infra$ sudo chmod u+s /usr/local/libexec/qemu-bridge-helper
    ```

    Then, try to start the VM again. For more information, see the [here](https://wiki.qemu.org/Features/HelperNetworking#Setup).
        
    </details>

1. Connect to the PXE server VM through the "Virtual Machine Manager" UI and run the Debian
   installer. The Debian installer will guide you through the installation process. You can use the
   default settings for most of the options.

   > **Note**: We recommend doing a minimal installation of Debian, without any graphical interface.

### Verify

1. Verify that the PXE server VM is running:

    ```console
    user:~/kubeflow-on-kvm$ virsh list --all
    Id   Name         State
    -----------------------------
    1    pxe-server   running
    ```

1. Create an SSH key, if you don't already have one:

    ```console
    user:~/kubeflow-on-kvm$ ssh-keygen
    ```

1. Copy the SSH public key to the PXE server VM:

    ```console
    user:~/kubeflow-on-kvm$ ssh-copy-id user@pxe-server
    ```

    > **Note**: Replace `user` with your username and `pxe-server` with the IP address of the PXE
    > server VM.

1. Verify that you can SSH into the PXE server VM:

    ```console
    user:~/kubeflow-on-kvm/infra$ ssh user@pxe-server
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

    > **Note**: Replace `user` with your username and `pxe-server` with the IP address of the PXE
    > server VM.
