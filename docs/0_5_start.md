## Start This Project

Even the most basic of LLM Chains depend on a few additional microservices. These can be ignored during development for in-memory alternatives, but then code changes are required to go to production. Thankfully, Workbench manages those additional microservices for development environments.

<details>
<summary>
<b>Expand this section for details on starting the demo application.</b>
</summary>

> **HINT:** For each application, the debug output can be monitored in the UI by clicking the Output link in the lower left corner, selecting the dropdown menu, and choosing the application of interest (or **Compose** for applications started via compose). 

Since you can either pull NIMs and run them locally, or utilize the endpoints from *ai.nvidia.com* you can run this project with *or* without GPUs. 

1. The applications bundled in this workspace can be controlled by navigating to two tabs:

    - **Environment** > **Compose**
    - **Environment** > **Applications**

1. First, navigate to the **Environment** > **Compose** tab. If you're not working in an environment with GPUs, you can just click **Start** to run the project using a lightweight deployment. This default configuration will run the following containers:

    - *Milvus Vector DB*: An unstructured knowledge base 

    - *Redis*: Used to store conversation histories

1. If you have access to GPU resources and want to run any NIMs locally, use the dropdown menu under **Compose** and select which set of NIMs you want to run locally. Note that you *must* have at least 1 available GPU per NIM you plan to run locally. Below is an outline of the available configurations:

    - Local LLM (min 1 GPU required)
        - The first time the LLM NIM is started, it will take some time to download the image and the optimized models.
            - During a long start, to confirm the LLM NIM is starting, the progress can be observed by viewing the logs by using the *Output* pane on the bottom left of the UI.

            - If the logs indicate an authentication error, that means the provided *NGC_API_KEY* does not have access to the NIMs. Please verify it was generated correctly and in an NGC organization that has NVIDIA AI Enterprise support or trial.

            - If the logs appear to be stuck on `..........: Pull complete`. `..........: Verifying complete`, or `..........: Download complete`; this is all normal output from Docker that the various layers of the container image have been downloaded.

            - Any other failures here need to be addressed.
    - Local LLM + Embedding (min 2 GPUs required)

    - Local LLM + Embedding + Reranking (min 3 GPUs required)
        

    > **NOTE:** 
    > - Each profile will also run *Milvus Vector DB* and *Redis*
    > - Due to the nature of Docker Compose profiles, the UI will let you select multiple profiles at the same time. In the context of this project, selecting multiple profiles does not make sense. It will not cause any errors, however we recommend only selecting one profile at a time for simplicity.

1. Once the compose services have been started, navigate to the **Environment** > **Applications** tab. Now, the *Chain Server* can safely be started. This contains the custom LangChain code for performing our reasoning chain. By default, it will use the local Milvus and Redis, but use *ai.nvidia.com* for LLM, Embedding, and Reranking model inferencing.

1. Once the *Chain Server*  is up, the *Chat Frontend* can be started. Starting the interface will automatically open it in a browser window. If you are running any local NIMs, you can edit the config to connect to them via the *Chat Frontend*

  ![NIM Anywhere Frontend](_static/na_frontend.png)

</details>
