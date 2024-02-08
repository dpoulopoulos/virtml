# Install QEMU/KVM on Debian/Ubuntu

This guide will show you how to install QEMU/KVM on a Debian-based system.

## What you'll need

* A Debian-based system.

## Procedure

1. Change to root user:

    ```console
    user:~$ sudo su -
    root:~#
    ```

1. Check if your CPU supports virtualization technology:

    ```console
    root:~# egrep -c '(vmx|svm)' /proc/cpuinfo
    56
    ```

    If Virtualization is supported, the output should be greater than `0`.

1. Check if KVM virtualization is supported:

    ```console
    root:~# kvm-ok
    INFO: /dev/kvm exists
    KVM acceleration can be used
    ```

    <details>
    <summary>Troubleshoot</summary>
    
    If the `kvm-ok` utility is missing, install the `cpu-checker` package:

    ```console
    root:~# apt update && apt install -y cpu-checker
    ```
    </details>

1. Install QEMU/KVM and other required packages:

    ```console
    root:~# apt update && \
    apt install -y qemu-kvm libvirt-clients libvirt-daemon-system \
    bridge-utils virtinst virt-manager
    ```

    This will install the following packages:

    - **qemu-kvm**: An open-source emulator that emulates the hardware resources of a computer.
    - **libvirt-clients**: APIs and client-side libraries for managing virtual machines from the
      command line.
    - **libvirt-daemon-system**: Provides configuration files needed to run the virtualization
      service.
    - **bridge-utils**: A set of command-line tools for managing bridge devices.
    - **virtinst**: A collection of command-line utilities for creating and making changes to
      virtual machines.
    - **virt-manager**: A Qt-based GUI interface for creating and managing virtual machines using
      the libvirt daemon.

    <br/>

1. Enable and start the `libvirtd` virtualization daemon:
    
    ```console
    root:~# systemctl enable --now libvirtd
    ```

1. Change back to your user account:

    ```console
    root:~# exit
    user:~$
    ```

1. Add your user account to the `kvm` and `libvirt` groups:

    ```console
    user:~$ sudo usermod -aG kvm,libvirt $USER
    ```

## Verify

1. Verify that the `libvirtd` service is running:

    ```console
    user:~$ sudo systemctl status libvirtd
    ● libvirtd.service - Virtualization daemon
     Loaded: loaded (/lib/systemd/system/libvirtd.service; enabled; preset: enabled)
     Active: active (running) since Thu 2024-02-08 08:07:20 EET; 7h ago
    ...skipping...
    ```

1. Launch the `virt-manager` application:

    ```console
    user:~$ virt-manager
    ```
