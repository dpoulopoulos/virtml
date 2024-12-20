# Create e VirtML Administrative VM

This guide will take you step-by-step through the process of creating a new virtual machine (VM)
using libvirt and installing Debian on it. We'll use this VM as the administrative machine for the
project. After setting it up, we will connect to this machine and use it to run the remaining
guides.

## What you'll need

To complete this guide, you will need the following:

* A Debian-based system with root access.
* A working [QEMU/KVM installation](qemu-kvm).
* A Debian 12.x ISO image. You can download it from the [Debian website](https://debian.org/distrib/netinst).

```{important}
The guide assumes that you have already downloaded a Debian 12.x ISO image in the default directory
`/var/lib/libvirt/images`. We will be working with a Debian netinst ISO image, which is a minimal
installation image that downloads packages from the internet during the installation process.
```

## Procedure

Follow the steps below to create a new VM and install Debian on it.

1. Change to the project's root directory:

    ```console
    user:~$ cd /home/user/virtlml
    ```

    ```{note}
    Replace `/home/user/virtlml` with the path to the project's root directory.
    ```

1. Decide on login credentials for the `root` user:

    ```console
    user:~/virtml$ export ROOTPW_HASH=$(openssl passwd -6)
    ```

1. Export your public SSH key:

    ```console
    user:~/virtml$ export SSH_KEY=$(cat ~/.ssh/id_rsa.pub)
    ```
 
1. Export the environment variables for your network settings. Replace the example values with
   values specific to your network:

    * `GUEST_IP`: The IP address you want to assign to the VM.
    * `GATEWAY`: The network gateway.
    * `NETMASK`: The network mask.
    * `NAMESERVERS`: The network DNS server.
    * `DOMAIN`: The network domain.

    <br/>

    ```console
    user:~/virtml$ export GUEST_IP="192.168.20.100"
    ```

    ```console
    user:~/virtml$ export GATEWAY="192.168.20.1"
    ```

    ```console
    user:~/virtml$ export NETMASK="255.255.255.0"
    ```

    ```console
    user:~/virtml$ export NAMESERVERS="192.168.20.1"
    ```

    ```console
    user:~/virtml$ export DOMAIN="example.com"
    ```

1. Render the `preseed` file:

    ```console
    user:~/virtml$ j2 infra/preseed.cfg.j2 > infra/preseed.cfg
    ```

1. Create the new VM using `virt-install`. The following command will start a new, completely
   automated, Debian installation. The VM will be on the same network as your host machine, using
   the `br0` bridge.

    ```console
    user:~/virtlml$ virt-install \
        --name virtml-admin \
        --vcpus 1 \
        --cpu mode=host-passthrough \
        --ram 2048 \
        --disk size=24,format=qcow2,cache=none,discard=unmap \
        --location /var/lib/libvirt/images/debian-12.5.0-amd64-netinst.iso \
        --os-variant linux2022 \
        --initrd-inject=infra/preseed.cfg \
        --bridge=br0 \
        --graphics none \
        --extra-args 'auto=true console=ttyS0,115200n8' \
        --boot uefi
    ```

## Verify

1. Verify that the VM is running:

    ```console
    user:~/virtlml$ virsh list --all
    Id   Name         State
    -----------------------------
    1    virtml-admin running
    ```

1. Verify that you can SSH into the PXE server VM:

    ```console
    user:~/virtlml$ ssh root@virtml-admin
    Linux virtml-admin 6.1.0-20-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.85-1 (2024-04-11) x86_64

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Thu May  2 13:04:36 2024 from 192.168.20.25
    root@virtml-admin:~#
    ```

    ```{note}
    Replace `virtml-admin` with the IP address of the VM. Alternatively, you can set the hostname
    for the VM in your `/etc/hosts` file.
    ```
