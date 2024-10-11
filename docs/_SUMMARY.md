Please contact ameliay@nvidia.com, rkraus@nvidia.com, or join [this] slack channel if you are a internal user, for any question and feedback.

One of the primary benefit for AI for Enterprises is their ability to work with and learn from their internal data. Retrieval-Augmented Generation ([RAG](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/)) is one of the best way to do so. NVIDIA has developed a set of micro-services called NVIDIA Inference Micro-service([NIM](https://docs.nvidia.com/nim/large-language-models/latest/introduction)) to help our partners and customers build effective RAG pipeline with ease. 

NIM Anywhere is an integration of all the tooling required to start integrating NIMs. It natively scales out to full-sized labs and up to production environments. This is great news for building a RAG architecture and easily adding NIMs as needed! If you're unfamiliar with RAG, it dynamically retrieves relevant
external information during inference without modifying the model
itself. Imagine you're the [xx] of a company with a local database containing confidential, up-to-date information. You don’t want OpenAI to access it, but you need the model to understand it to answer questions accurately. The solution, connect your language model to the database and feed them with the information. 

To learn more about why RAG is an excellent solution for boosting the accuracy and reliability of your generative AI models, [click me](deeper dive into RAG here). Another technique other than RAG is fine-tuning, an overview of this can be seen [here](link to finetuning, resource outside NV?).

Get started with NIM Anywhere now with the [quick-start](#quick-start) instructions and build your first RAG application using NIMs!

![NIM Anywhere Screenshot](_static/nim-anywhere.png)
