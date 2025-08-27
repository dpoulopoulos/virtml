# Configure a PXE server

This guide will guide you through setting up a PXE server that allows any machine connected to the
same network to boot and install Debian `12.x`. We will use the virtml-admin VM, transforming it
into our PXE server for this purpose.

## What you'll need

To complete this guide, you will need the following:

* A VM with [Debian `12.x`](../virtml-admin) installed.

## Procedure

Follow the steps below to configure a PXE server:

1. SSH into the PXE server VM:

    ```console
    user:~/virtlml$ ssh root@virtml-admin
    ```

    ```{note}
    Replace `virtml-admin` with the IP address of the VM. Alternatively, you can add an entry to
    your `/etc/hosts` file with the IP address and hostname of the VM.
    ```

1. Install the required packages:

    ```console
    root@virtml-admin:~# apt update && apt install -y dnsmasq python3-jinja2 tftp
    ```

1. Set up a useful alias to render templates:

      ```console
      root@virtml-admin:~# alias j2r="python3 -c 'import os; import sys; import jinja2 as j2; print(j2.Environment(undefined=j2.StrictUndefined).from_string(sys.stdin.read()).render(os.environ))'"
      ```

1. Download the `netboot.tar.gz` file, which contains the network installer for Debian `12.x`:

    ```console
    root@virtml-admin:~# wget https://deb.debian.org/debian/dists/Debian12.5/main/installer-amd64/current/images/netboot/netboot.tar.gz
    ```

    ```{note}
    The `netboot.tar.gz` file we are using is for Debian `12.5`. If you want to use a different
    version, you can find the appropriate file on the [Debian website](https://https://deb.debian.org/debian/dists/).
    ```

1. Create a `tftp` directory to store the files that will be served by the TFTP server, and navigate
   into it:

    ```console
    root@virtml-admin:~# mkdir -p /srv/tftp && cd /srv/tftp
    ```

1. Extract the `netboot.tar.gz` file:

    ```console
    root@virtml-admin:/srv/tftp# tar xzvf ~/netboot.tar.gz
    ```

1. Remove any unnecessary files:

    ```console
    root@virtml-admin:/srv/tftp# rm ldlinux.c32 pxelinux.0 pxelinux.cfg
    ```

1. Create a few extra symlinks for the `bootnetx64.efi` and `grubx64.efi` files:

    ```console
    root@virtml-admin:/srv/tftp# ln -s debian-installer/amd64/bootnetx64.efi .
    ```

    ```console
    root@virtml-admin:/srv/tftp# ln -s debian-installer/amd64/grubx64.efi .
    ```

1. Navigate to the `/etc/dnsmasq.d` directory:

    ```console
    root@virtml-admin:/srv/tftp# cd /etc/dnsmasq.d
    ```

1. Export environment variables for your network settings. Replace the example values with values
   specific to your network:

    * `DHCP_NETWORK`: The network address of the DHCP server.
    * `DHCP_GATEWAY`: The gateway address of the DHCP server.
    * `DHCP_NETMASK`: The netmaWsk of the DHCP server.
    * `DHCP_DNS_SERVER`: The DNS server address of the DHCP server.

    <br/>

    ```console
    root@virtml-admin:/etc/dnsmasq.d# export DHCP_NETWORK="192.168.20.0"
    ```

    ```console
    root@virtml-admin:/etc/dnsmasq.d# export DHCP_GATEWAY="192.168.20.1"
    ```

    ```console
    root@virtml-admin:/etc/dnsmasq.d# export DHCP_NETMASK="255.255.255.0"
    ```

    ```console
    root@virtml-admin:/etc/dnsmasq.d# export DHCP_DNS_SERVER="192.168.20.1"
    ```

1. Configure the `dnsmasq` service to disable DNS, and enable DHCP and TFTP:

    a. Run the following command:

    ```console
    root@virtml-admin:/etc/dnsmasq.d# j2r > virtlml.conf
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
    root@virtml-admin:/etc/dnsmasq.d# j2r > virtlml.conf <<EOF
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

1. Restart the `dnsmasq` service:

    ```console
    root@virtml-admin:/etc/dnsmasq.d# systemctl restart dnsmasq
    ```

1. Return to your local machine:

    ```console
    root@virtml-admin:/etc/dnsmasq.d# exit
    user:~/virtlml$
    ```

1. Change the `grub.cfg` file to choose the "Automated Install" option by default:

    ```console
    user:~/virtlml$ export PXE_SERVER="192.168.20.100"
    ```

    ```{note}
    Replace the `PXE_SERVER` IP value with IP address of `virtml-admin`.
    ```

    ```console
    user:~/virtlml$ j2 infra/grub.cfg.j2 > infra/grub.cfg
    ```

    ```console
    user:~/virtlml$ scp infra/grub.cfg root@virtml-admin:/srv/tftp/debian-installer/amd64/grub/grub.cfg
    ```

## Verify

Verify that the `dnsmasq` service is running and serving files over TFTP:

1. SSH into the PXE server VM:

    ```console
    user:~/virtlml$ ssh root@virtml-admin
    ```

1. Ensure that the `dnsmasq` service is running:

    ```console
    root@virtml-admin:/etc/dnsmasq.d# systemctl status dnsmasq.service
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

    Feb 08 11:52:07 virtml-admin systemd[1]: Starting dnsmasq.service - dnsmasq - A lightweight DHCP and caching DNS server...
    Feb 08 11:52:07 virtml-admin dnsmasq[493]: started, version 2.89 DNS disabled
    ```

1. Confirm `dnsmasq` serves files over TFTP:

    ```console
    root@virtml-admin:/etc/dnsmasq.d# tftp localhost -c get /version.info /dev/stdout
    Debian version:  12 (bookworm)
    Installer build: 20230607+deb12u4
    ```
