# Developing Your Own Applications

This project contains applications for a few demo services as well as integrations with external services. These are all orchestrated by [NVIDIA AI Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/).

The demo services are all in the `code` folder. The root level of the code folder has a few interactive notebooks meant for technical deep dives. The Chain Server is a sample application utilizing NIMs with LangChain. (Note that the Chain Server here gives you the option to experiment with and without RAG). The Chat Frontend folder contains an interactive UI server for exercising the chain server. Finally, sample notebooks are provided in the Evaluation directory to demonstrate retrieval scoring and validation.

``` mermaid
mindmap
  root((AI Workbench))
    Demo Services
        Chain Server<br />LangChain + NIMs
        Frontend<br />Interactive Demo UI
        Evaluation<br />Validate the results
        Notebooks<br />Advanced usage

    Integrations
        Redis</br>Conversation History
        Milvus</br>Vector Database
        LLM NIM</br>Optimized LLMs
```
