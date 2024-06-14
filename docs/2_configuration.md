

# Application Configuration

The Chain Server can be configured with either a configuration file or environment variables.

## Config from a file

By default, the application will search for a configuration file in all of the following locations.
If multiple configuration files are found, values from lower files in the list will take precendence.

  - ./config.yaml
  - ./config.yml
  - ./config.json
  - ~/app.yaml
  - ~/app.yml
  - ~/app.json
  - /etc/app.yaml
  - /etc/app.yml
  - /etc/app.json

## Config from a custom file

An additional config file path can be specified through an environment variable named `APP_CONFIG`.
The value in this file will take precedence over all the default file locations.

```bash
export APP_CONFIG=/etc/my_config.yaml
```

## Config from env vars

Configuration can also be set using environment variables.
The variable names will be in the form: `APP_FIELD__SUB_FIELD`
Values specified as environment variables will take precedence over all values from files.



## Chain Server config schema

```yaml
# Your API key for authentication to AI Foundation.
# ENV Variables: NGC_API_KEY, NVIDIA_API_KEY, APP_NVIDIA_API_KEY
# Type: string, null
nvidia_api_key: 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

# The Data Source Name for your Redis DB.
# ENV Variables: APP_REDIS_DSN
# Type: string
redis_dsn: redis://localhost:6379/0

chat_model: 
    # The name of the model to request.
    # ENV Variables: APP_CHAT_MODEL__NAME
    # Type: string
    name: meta/llama3-70b-instruct

    # The URL to the model API.
    # ENV Variables: APP_CHAT_MODEL__URL
    # Type: string
    url: https://integrate.api.nvidia.com/v1


embedding_model: 
    # The name of the model to request.
    # ENV Variables: APP_EMBEDDING_MODEL__NAME
    # Type: string
    name: NV-Embed-QA


milvus: 
    # The host machine running Milvus vector DB.
    # ENV Variables: APP_MILVUS__URL
    # Type: string
    url: http://localhost:19530

    # The name of the Milvus collection.
    # ENV Variables: APP_MILVUS__COLLECTION_NAME
    # Type: string
    collection_name: collection_1


# Options for the logging levels.
# ENV Variables: APP_LOG_LEVEL
log_level: WARNING


```

## Chat Frontend config schema

The chat frontend has a few configuraiton options as well. They can be set in the same manner as the chain server.

```yaml
# The URL to the chain on the chain server.
# ENV Variables: APP_CHAIN_URL
# Type: string
chain_url: http://localhost:3030/

# The url prefix when this is running behind a proxy.
# ENV Variables: PROXY_PREFIX, APP_PROXY_PREFIX
# Type: string
proxy_prefix: /

# Path to the chain server's config.
# ENV Variables: APP_CHAIN_CONFIG_FILE
# Type: string
chain_config_file: ./config.yaml

# Options for the logging levels.
# ENV Variables: APP_LOG_LEVEL
log_level: INFO


```

