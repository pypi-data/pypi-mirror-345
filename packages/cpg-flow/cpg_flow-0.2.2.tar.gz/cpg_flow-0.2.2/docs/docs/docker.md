# 🐳 Docker

## ⬇️ Pulling and Using the `cpg-flow` Docker Image

These steps are restricted to CPG members only. Anyone will have access to the code in this public repositry and can build a version of cpg-flow themselves. The following requires authentication with the CPG's GCP.

To pull and use the Docker image for the `cpg-flow` Python package, follow these steps:

1. **Authenticate with Google Cloud Registry**:

    ```sh
    gcloud auth configure-docker australia-southeast1-docker.pkg.dev
    ```

2. **Pull the Docker Image**:
    - For alpha releases:

      ```sh
      docker pull australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:0.1.0-alpha.11
      ```

    - For main releases:

      ```sh
      docker pull australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:1.0.0
      ```

3. **Run the Docker Container**:

    ```sh
    docker run -it australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:<tag>
    ```

### ⏳ Temporary Images for Development

Temporary images are created for each commit and expire in 30 days. These images are useful for development and testing purposes.

- Example of pulling a temporary image:

  ```sh
  docker pull australia-southeast1-docker.pkg.dev/cpg-common/images-tmp/cpg_flow:991cf5783d7d35dee56a7ab0452d54e69c695c4e
  ```

### 🔨 Accessing Build Images for CPG Members

Members of the CPG can find the build images in the Google Cloud Registry under the following paths:

- Alpha and main releases: `australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow`
- Temporary images: `australia-southeast1-docker.pkg.dev/cpg-common/images-tmp/cpg_flow`

Ensure you have the necessary permissions and are authenticated with Google Cloud to access these images.
