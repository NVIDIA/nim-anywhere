# NVIDIA NIM Anywhere [![Clone Me with AI Workbench](https://img.shields.io/badge/Open_In-AI_Workbench-76B900)](https://ngc.nvidia.com/open-ai-workbench/aHR0cHM6Ly9naXRodWIuY29tL05WSURJQS9uaW0tYW55d2hlcmUK)

[![NVIDIA: LLM NIM](https://img.shields.io/badge/NVIDIA-LLM%20NIM-green?logo=nvidia&logoColor=white&color=%2376B900)](https://docs.nvidia.com/nim/#large-language-models)
[![NVIDIA: Embedding NIM](https://img.shields.io/badge/NVIDIA-Embedding%20NIM-green?logo=nvidia&logoColor=white&color=%2376B900)](https://docs.nvidia.com/nim/#nemo-retriever)
[![NVIDIA: Reranker NIM](https://img.shields.io/badge/NVIDIA-Reranker%20NIM-green?logo=nvidia&logoColor=white&color=%2376B900)](https://docs.nvidia.com/nim/#nemo-retriever)
[![CI Pipeline Status](https://github.com/nvidia/nim-anywhere/actions/workflows/ci.yml/badge.svg?query=branch%3Amain)](https://github.com/NVIDIA/nim-anywhere/actions/workflows/ci.yml?query=branch%3Amain)
![Python: 3.10 | 3.11 | 3.12](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-yellow?logo=python&logoColor=white&color=%23ffde57)


 
Please join \#cdd-nim-anywhere slack channel if you are a internal user,
open an issue if you are external for any question and feedback.

One of the primary benefit of using AI for Enterprises is their ability
to work with and learn from their internal data. Retrieval-Augmented
Generation
([RAG](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/))
is one of the best ways to do so. NVIDIA has developed a set of
micro-services called [NIM
micro-service](https://docs.nvidia.com/nim/large-language-models/latest/introduction.html)
to help our partners and customers build effective RAG pipeline with
ease.

NIM Anywhere contains all the tooling required to start integrating NIMs
for RAG. It natively scales out to full-sized labs and up to production
environments. This is great news for building a RAG architecture and
easily adding NIMs as needed. If you're unfamiliar with RAG, it
dynamically retrieves relevant external information during inference
without modifying the model itself. Imagine you're the tech lead of a
company with a local database containing confidential, up-to-date
information. You don’t want OpenAI to access your data, but you need the
model to understand it to answer questions accurately. The solution is
to connect your language model to the database and feed them with the
information.

To learn more about why RAG is an excellent solution for boosting the
accuracy and reliability of your generative AI models, [read this
blog](https://developer.nvidia.com/blog/enhancing-rag-applications-with-nvidia-nim/).

Get started with NIM Anywhere now with the [quick-start](#quick-start)
instructions and build your first RAG application using NIMs!

![NIM Anywhere Screenshot](.static/_static/nim-anywhere.png)
 
- [Quick-start](#quick-start)
  - [Generate your NGC Personal Key](#generate-your-ngc-personal-key)

# Quick-start

## Generate your NGC Personal Key

To allow AI Workbench to access NVIDIA’s cloud resources, you’ll need to
provide it with a Personal Key. These keys begin with `nvapi-`.

<details>
<summary>
<b>Expand this section for instructions for creating this key.</b>
</summary>

1.  Go to the [NGC Personal Key
    Manager](https://org.ngc.nvidia.com/setup/personal-keys). If you are
    prompted to, then register for a new account and sign in.

    > **HINT** You can find this tool by logging into
    > [ngc.nvidia.com](https://ngc.nvidia.com), expanding your profile
    > menu on the top right, selecting *Setup*, and then selecting
    > *Generate Personal Key*.

2.  Select *Generate Personal Key*.

    ![Generate Personal Key](.static/_static/generate_personal_key.png)

3.  Enter any value as the Key name, an expiration of 12 months is fine,
    and select all the services. Press *Generate Personal Key* when you
    are finished.

    ![Personal Key Form](.static/_static/personal_key_form.png)

4.  Save your personal key for later. Workbench will need it and there
    is no way to retrieve it later. If the key is lost, a new one must
    be created. Protect this key as if it were a password.

    ![Personal Key](.static/_static/personal_key.png)

</details>
