# How to Run NIM Anywhere with Compose

## Steps to Get Started

1. **Clone and Configure**
   - Follow the existing clone and configuration instructions.  
   - You can **skip the mount setup**.  
   - Make sure to set your **NGC API KEY secret**.

2. **Start the Application**
   - Scroll down to the **Apps** section in your environment.
   - Look for the **Compose** section under Applications.
   - From the dropdown menu:
     - Select the number of GPUs you have.
     - Click **Start**.
   - This will start up the following containers based on your profile:
     - **0 GPUs**: `milvus` and `redis`
     - **1 GPU**: `milvus`, `redis`, and the LLM `NIM`
     - **2 GPUs**: `milvus`, `redis`, LLM `NIM`, and Embedding `NIM`
     - **3 GPUs**: `milvus`, `redis`, LLM `NIM`, Embedding `NIM`, and Reranking `NIM`

3. **Launch Additional Services**
   - After Compose starts up the containers, you can also start:
     - **Chain Server**
     - **Chat Frontend**
     - **Jupyter Lab**

