#!/bin/bash

cd $(dirname $0)


TEMPLATE_NAME="template"
export PAGE_NAME=$1

envsubst < pages_templates/${TEMPLATE_NAME}.py.envsub > pages/${PAGE_NAME}.py
envsubst < pages_templates/${TEMPLATE_NAME}.en_US.yaml.envsub > pages/${PAGE_NAME}.en_US.yaml
envsubst < pages_templates/${TEMPLATE_NAME}_tests.py.envsub > pages/${PAGE_NAME}_tests.py

cat <<EOM >> pages/sidebar.yaml
      - label: "$PAGE_NAME"
        target: $PAGE_NAME
EOM
