# Deploy Kubeflow

In this section, you will learn how to deploy [Kubeflow](https://www.kubeflow.org/) on your
Kubernetes cluster. Kubeflow is an open-source machine learning (ML) toolkit for Kubernetes. It is
designed to simplify the process of training, serving, and deploying ML models at scale.

Having a local instance of Kubeflow is useful for development and testing purposes. It allows you to
experiment with different ML models and workflows without incurring the costs of cloud resources. It
is an invaluable step for learning MLOps practices and understanding how Kubernetes works by
examing a real-world use case.

## What you'll need

To complete this guide, you will need the following:

* A running Kubernetes cluster. You can use the [Kubernetes cluster](kubernetes) you created in the
  previous section.
* Longhorn installed on your Kubernetes cluster. You can install it by following the instructions in
  the [previous section](longhorn).
* Kustomize installed on your local machine. You can install it by following the instructions in the
  [official documentation](https://kubectl.docs.kubernetes.io/installation/kustomize/).

## Procedure

Follow the steps below to deploy Kubeflow on your Kubernetes cluster:

1. Clone the Kubeflow manifests repository:

    ```console
    user:~$ git clone https://github.com/kubeflow/manifests.git
    ```

1. Change to the manifests directory:

    ```console
    user:~$ cd manifests
    ```

1. Checkout a specific version of the Kubeflow manifests repository:

    ```console
    user:~/manifests$ git checkout tags/v1.8.1
    ```

    ```{note}
    This documentation uses version `1.8.1` of the Kubeflow manifests. You can replace `v1.8.0` with
    the version you want to use.
    ```

1. Deploy Kubeflow using the Kustomize:

    ```console
    user:~/manifests$ while ! kustomize build example | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
    ```

    ```{note}
    The `while` loop retries the `kubectl apply` command until it succeeds. The whole process can
    take up to 10 minutes.
    ```

## Verify

Verify that Kubeflow is running.

1. Check the status of the pods in the `kubeflow` namespace:

    ```console
    user:~$ kubectl get pods -n kubeflow
    ```

    ```{note}
    The output should show a list of pods running in the `kubeflow` namespace.
    ```

1. Port-forward the Istio Ingress Gateway service to access the Kubeflow dashboard:

    ```console
    user:~$ kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
    ```

1. Open a web browser and navigate to `http://localhost:8080`. You should see the Kubeflow
   dashboard.

    ```{note}
    The default username is `user@example.com` and the default password is `12341234`.
    ```
