.. title:: VirtML

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. image:: ../../assets/images/virtml-logo-black.svg
   :alt: VirtML Logo
   :align: center

|br|

.. image:: https://img.shields.io/badge/license-apache%202.0-blue
   :target: https://www.apache.org/licenses/LICENSE-2.0
   :alt: License: Apache 2.0

.. image:: https://img.shields.io/badge/debian-bookworm-red
   :target: https://www.debian.org/
   :alt: Debian: Bookworm

.. image:: https://img.shields.io/badge/kubeflow-v1.8-orange
   :target: https://www.kubeflow.org/
   :alt: Kubeflow: v1.8

.. image:: https://img.shields.io/badge/kubernetes-v1.29.3-orange
   :target: https://kubernetes.io/
   :alt: Kubernetes: v1.29.3

|br|

VirtML is a project dedicated to simplifying the process of setting up `Kubeflow <https://www.kubeflow.org/>`_
in a virtualized environment, making it easier for data scientists to leverage the power of Machine
Learning (ML) workflows on Kubernetes.

Follow the guides below to get started with VirtML! You have two options:

👨‍🔬 **Manual Deployment**: Follow the step-by-step guides to set up a virtualized environment for
Kubeflow using a manual approach, setting everything by hand. This is a great way to learn the ins
and outs of the process.

🤖 **Automated Deployment**: Use Ansible playbooks to automate the deployment of a virtualized
environment for Kubeflow. This is a great way to quickly get started with VirtML.

In any case, you should complete the core guides first, as they lay the foundation for either
approach.

.. note::

   This project is tested on Debian 12 (Bookworm). It should work on other Debian-based
   distributions but it will require some modifications. We also plan to support Rocky Linux in the
   future.

🚧 🚧 🚧 This is Work-in-Progress 🚧 🚧 🚧

.. toctree::
   :maxdepth: 1
   :caption: Core Guides

   qemu-kvm
   gpu-passthrough
   debian-vm

.. toctree::
   :maxdepth: 1
   :caption: Deployment Guides

   manual-deployment/index.rst

Contact
-------

* Dimitris Poulopoulos dimitris.a.poulopoulos@gmail.com

We warmly welcome your feedback and look forward to hearing from you!

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
