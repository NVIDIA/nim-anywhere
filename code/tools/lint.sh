#!/bin/bash
set -e

cd  $(dirname $0)/../..

if [ -z "$1" ] || [ "$1" = "deps" ]; then
    echo "Installing dependencies..."
    which pylint || pip install pylint
    which mypy || pip install mypy
    which black || pip install black
    echo -e "\n\n\n"
fi

if [ -z "$1" ] || [ "$1" = "pylint" ]; then
    echo "Checking Python syntax with Pylint."
    pylint --rc-file pyproject.toml $(git ls-files 'code/*.py' | grep -v tutorial_app)
    echo -e "\n\n\n"
fi

if [ -z "$1" ] || [ "$1" = "mypy" ]; then
    echo "Checking Type Hints with MyPy"
    mypy --config-file pyproject.toml $(git ls-files 'code/*.py')
    echo -e "\n\n\n"
fi

if [ -z "$1" ] || [ "$1" = "black" ]; then
    echo "Checking code formatting with Black"
    black --check . --line-length 120 $(git ls-files 'code/*.py')
    echo -e "\n\n\n"
fi

if [ -z "$1" ] || [ "$1" = "ipynb" ]; then
    echo "Checking Notebooks for cells with output."
    fail_count=0
    for file in $(git ls-files 'code/*.ipynb'); do
        echo -en "$file\t"
        # filter the ipynb json to get only the cell output, remove empty values
        outputs=$(cat $file | jq '.cells[].outputs' | grep -Pv '(null|\[\])' | cat)
        if [ "$outputs" == "" ]; then
            echo "pass"
        else
            echo "fail"
            echo "$outputs"
            fail_count=$(expr $fail_count + 1)
        fi
    done

    if [ $fail_count > 0 ]; then
        exit $fail_count
    fi
    echo -e "\n\n\n"
fi

if [ -z "$1" ] || [ "$1" = "docs" ]; then
    echo "Checking if the Documentation is up to date."
    cd docs;
    if ! make -q; then
        make -qd | grep -v '^  ' | grep -v 'is older than'
        echo 'fail: in the docs folder run `make all` to update the readme' >&2
        exit 1
    fi
    echo "pass"
    cd ..
    echo -e "\n\n\n"
fi

if [ "$1" = "fix" ]; then
    echo "Fixing code formatting with Black"
    black . --line-length 120 $(git ls-files 'code/*.py')
    echo -e "\n\n\n"

    echo "Ensuring the README.md is up to date"
    cd docs
    make
    cd ..

    echo "Clearing Jupyter Notebook cell output."
    for ipynb in $(git ls-files 'code/*.ipynb'); do
        if cat "$ipynb" | jq '.cells[].outputs' | grep -Pv '(null|\[\])' > /dev/null ; then
            echo "$ipynb"
            jupyter nbconvert "$ipynb" --ClearOutputPreprocessor.enabled=True --to=notebook --inplace --log-level=ERROR
        fi
    done

    echo -e "\n\n\n"
fi

echo -e "Success."

