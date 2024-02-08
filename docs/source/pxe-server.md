# Configure a PXE server

This guide will help you configure a PXE server to boot the control-plane and worker nodes of a
Kubernetes cluster.

## Step 1: Create a VM for the PXE server on KVM

In this section you will create a KVM VM for the PXE server, using a Debian `12.4` image.

### What you'll need

* A machine with QEMU/KVM installed.
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

    ```console
    user:~/kubeflow-on-kvm/infra$ virt-manager
    ```   

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

## Step 2: Configure the PXE server

In this section you will configure the PXE server to boot any machine that is connected to the same
network and install Debian `12.4` on it.

### What you'll need

* A VM with Debian `12.4` deployed. You can use the PXE server VM that you created in the previous
  step.

### Procedure

1. SSH into the PXE server VM:

    ```console
    user:~/kubeflow-on-kvm$ ssh user@pxe-server
    ```

    > **Note**: Replace `user` with your username and `pxe-server` with the IP address of the PXE
    > server VM.

1. Change to root user:

    ```console
    user@pxe-server:~$ sudo su -
    root@pxe-server:~#
    ```

1. Install the required packages:

    ```console
    root@pxe-server:~# apt update && apt install -y dnsmasq python3-jinja2 tftp
    ```

1. Set up a useful alias to render templates:

      ```console
      root@pxe-server:~# alias j2r="python3 -c 'import os; import sys; import jinja2 as j2; print(j2.Environment(undefined=j2.StrictUndefined).from_string(sys.stdin.read()).render(os.environ))'"
      ```

1. Download the `netboot.tar.gz` file, which contains the network installer for Debian `12.4`:

    ```console
    root@pxe-server:~# wget https://deb.debian.org/debian/dists/Debian12.4/main/installer-amd64/current/images/netboot/netboot.tar.gz
    ```

1. Create a `tftp` directory to store the files that will be served by the TFTP server, and navigate
   into it:

    ```console
    root@pxe-server:~# mkdir -p /srv/tftp && cd /srv/tftp
    ```

1. Extract the `netboot.tar.gz` file:

    ```console
    root@pxe-server:/srv/tftp# tar xzvf ~/netboot.tar.gz
    ```

1. Remove any unnecessary files:

    ```console
    root@pxe-server:/srv/tftp# rm ldlinux.c32 pxelinux.0 pxelinux.cfg
    ```

1. Create a few extra symlinks for the `bootnetx64.efi` and `grubx64.efi` files:

    ```console
    root@pxe-server:/srv/tftp# ln -s debian-installer/amd64/bootnetx64.efi .
    ```

    ```console
    root@pxe-server:/srv/tftp# ln -s debian-installer/amd64/grubx64.efi .
    ```

1. Navigate to the `/etc/dnsmasq.d` directory:

    ```console
    root@pxe-server:/srv/tftp# cd /etc/dnsmasq.d
    ```

1. Export environment variables for your network settings. Replace the example values with values
   specific to your network:

    * `DHCP_NETWORK`: The network address of the DHCP server.
    * `DHCP_GATEWAY`: The gateway address of the DHCP server.
    * `DHCP_NETMASK`: The netmaWsk of the DHCP server.
    * `DHCP_DNS_SERVER`: The DNS server address of the DHCP server.

    <br/>

    ```console
    root@pxe-server:/etc/dnsmasq.d# export DHCP_NETWORK="192.168.1.0"
    ```

    ```console
    root@pxe-server:/etc/dnsmasq.d# export DHCP_GATEWAY="192.168.1.1"
    ```

    ```console
    root@pxe-server:/etc/dnsmasq.d# export DHCP_NETMASK="255.255.255.0"
    ```

    ```console
    root@pxe-server:/etc/dnsmasq.d# export DHCP_DNS_SERVER="8.8.8.8"
    ```

1. Configure the `dnsmasq` service to disable DNS, and enable DHCP and TFTP:

    a. Run the following command:

    ```console
    root@pxe-server:/etc/dnsmasq.d# j2r > kubeflow-on-kvm.conf
    ```

    b. Copy and paste the following text:

    ```
    # DNS: Disable
    port=0

    # DHCP: Enable (for specific addresses)
    dhcp-range={{ DHCP_NETWORK }},static
    dhcp-option=option:netmask,{{ DHCP_NETMASK }}
    dhcp-option=option:router,{{ DHCP_GATEWAY }}
    dhcp-option=option:dns-server,{{ DHCP_DNS_SERVER }}
    log-dhcp

    # TFTP: Enable
    enable-tftp
    tftp-root=/srv/tftp
    dhcp-boot=/bootnetx64.efi
    ```
    
    c. Run `CTRL + D` to exit.

    <!-- ```console
    root@pxe-server:/etc/dnsmasq.d# j2r > kubeflow-on-kvm.conf <<EOF
    > # DNS: Disable
    > port=0
    > 
    > # DHCP: Enable (for specific addresses)
    > dhcp-range={{ DHCP_NETWORK }},static
    > dhcp-option=option:netmask,{{ DHCP_NETMASK }}
    > dhcp-option=option:router,{{ DHCP_GATEWAY }}
    > dhcp-option=option:dns-server,{{ DHCP_DNS_SERVER }}
    > log-dhcp
    > 
    > # TFTP: Enable
    > enable-tftp
    > tftp-root=/srv/tftp
    > dhcp-boot=/bootnetx64.efi
    > EOF
    ``` -->

1. Create a template for `dnsmaq` to respond to individual DHCP requests:

    a. Run the following command:

    ```console
    root@pxe-server:/etc/dnsmasq.d# cat > .template.j2
    ```

    a. Copy and paste the following text:

    ```
    dhcp-host={{ CLIENT_MAC }},{{ CLIENT_HOSTNAME }},{{ CLIENT_IP }}
    ```
    
    a. Run `CTRL + D` to exit.

    <!-- ```console
    root@pxe-server:/etc/dnsmasq.d# cat > .template.j2 <<EOF
    > dhcp-host={{ CLIENT_MAC }},{{ CLIENT_HOSTNAME }},{{ CLIENT_IP }}
    > EOF
    ``` -->

    > **Note**: You will later set the `{{ MAC_ADDRESS }}` with the MAC address of the machine you
    > want to boot, and assign the hostname and IP address you want via the corresponding
    > environment variables (i.e., CLIENT_HOSTNAME, CLIENT_IP).

1. Restart the `dnsmasq` service:

    ```console
    root@pxe-server:/etc/dnsmasq.d# systemctl restart dnsmasq
    ```

### Verify

1. Ensure that the `dnsmasq` service is running:

    ```console
    root@pxe-server:/etc/dnsmasq.d# systemctl status dnsmasq.service
    ● dnsmasq.service - dnsmasq - A lightweight DHCP and caching DNS server
        Loaded: loaded (/lib/systemd/system/dnsmasq.service; enabled; preset: enabled)
        Active: active (running) since Thu 2024-02-08 11:52:08 EET; 10min ago
       Process: 469 ExecStartPre=/etc/init.d/dnsmasq checkconfig (code=exited, status=0/SUCCESS)
       Process: 484 ExecStart=/etc/init.d/dnsmasq systemd-exec (code=exited, status=0/SUCCESS)
       Process: 494 ExecStartPost=/etc/init.d/dnsmasq systemd-start-resolvconf (code=exited, status=0/SUCCESS)
      Main PID: 493 (dnsmasq)
         Tasks: 1 (limit: 2307)
        Memory: 4.3M
           CPU: 72ms
        CGroup: /system.slice/dnsmasq.service
                └─493 /usr/sbin/dnsmasq -x /run/dnsmasq/dnsmasq.pid -u dnsmasq -7 /etc/dnsmasq.d,.dpkg-dist,.dpkg-old,.dpkg-new --local-service --trust-anchor=.,2032>

    Feb 08 11:52:07 pxe-server systemd[1]: Starting dnsmasq.service - dnsmasq - A lightweight DHCP and caching DNS server...
    Feb 08 11:52:07 pxe-server dnsmasq[493]: started, version 2.89 DNS disabled
    ```

1. Confirm `dnsmasq` serves files over TFTP:

    ```console
    root@pxe-server:/etc/dnsmasq.d# tftp localhost -c get /version.info /dev/stdout
    Debian version:  12 (bookworm)
    Installer build: 20230607+deb12u4
    ```
