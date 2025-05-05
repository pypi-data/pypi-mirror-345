#!/bin/bash
# This script runs an ezbatch container command, but does some pre/post operations before/after the command is run.
# Check if root, if not, then rerun this script with sudo su
if [ "$(id -u)" -ne 0 ]; then
    # check if sudo is installed
    if ! command -v sudo &> /dev/null
    then
        echo "Please run this script as root or install sudo"
        exit 1
    fi
    exec sudo su -c "bash $0"
fi
# Define some convenience functions to make the script more readable
function is_apt_installed {
    command -v apt-get &> /dev/null
}
function is_dnf_installed {
    command -v dnf &> /dev/null
}
function is_yum_installed {
    command -v yum &> /dev/null
}
function is_apk_installed {
    command -v apk &> /dev/null
}
function is_wget_installed {
    command -v wget &> /dev/null
}
function is_unzip_installed {
    command -v unzip &> /dev/null
}
function is_tar_installed {
    command -v tar &> /dev/null
}
function is_gzip_installed {
    command -v gzip &> /dev/null
}
function is_jq_installed {
    command -v jq &> /dev/null
}
function setup_dependencies {
    dependencies=""
    if ! is_wget_installed
    then
        dependencies="$dependencies wget"
    fi
    if ! is_unzip_installed
    then
        dependencies="$dependencies unzip"
    fi
    if ! is_tar_installed
    then
        dependencies="$dependencies tar"
    fi
    if ! is_gzip_installed
    then
        dependencies="$dependencies gzip"
    fi
    if ! is_jq_installed
    then
        dependencies="$dependencies jq"
    fi
    if [ ! -z "$dependencies" ]
    then
        if is_apt_installed
        then
            export DEBIAN_FRONTEND=noninteractive
            apt-get update && apt-get install -y $dependencies
        elif is_dnf_installed
        then
            dnf install -y $dependencies
        elif is_yum_installed
        then
            yum install -y $dependencies
        elif is_apk_installed
        then
            apk add $dependencies
        else
            echo "No package manager found"
            exit 1
        fi
    fi
}
function is_aws_cli_installed {
    command -v aws &> /dev/null
}
function setup_aws_cli {
    if ! is_aws_cli_installed
    then
        wget -q "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
        unzip -q awscli-exe-linux-x86_64.zip
        ./aws/install
        rm -rf awscli-exe-linux-x86_64.zip ./aws
    fi
    aws --version
}
# Setup dependencies
setup_dependencies
setup_aws_cli
# Download s3 mounts that are specified in the EZBATCH_S3_MOUNTS environment variable
if [ ! -z "$EZBATCH_S3_MOUNTS" ]
then
    echo "Downloading s3 data..."
    # use jq to parse the json
    echo $EZBATCH_S3_MOUNTS | jq -rc '.read[]' | while read -r MOUNT_INFO; do
        echo "Source: $(echo $MOUNT_INFO | jq -r '.source') -> Destination: $(echo $MOUNT_INFO | jq -r '.destination')"
        aws s3 cp $(echo $MOUNT_INFO | jq -r '.source') $(echo $MOUNT_INFO | jq -r '.destination') $(echo $MOUNT_INFO | jq -r '.options')
    done
    echo "Downloaded s3 data."
fi
# Now run the command that was passed to the script, this will be stored in the EZBATCH_COMMAND environment variable
eval $EZBATCH_COMMAND
status=$?
# Upload to s3 mounts that are specified in the EZBATCH_S3_MOUNTS environment variable
if [ ! -z "$EZBATCH_S3_MOUNTS" ]
then
    echo "Uploading s3 data..."
    # use jq to parse the json
    echo $EZBATCH_S3_MOUNTS | jq -rc '.write[]' | while read -r MOUNT_INFO; do
        echo "Source: $(echo $MOUNT_INFO | jq -r '.source') -> Destination: $(echo $MOUNT_INFO | jq -r '.destination')"
        aws s3 cp $(echo $MOUNT_INFO | jq -r '.source') $(echo $MOUNT_INFO | jq -r '.destination') $(echo $MOUNT_INFO | jq -r '.options')
    done
    echo "Uploaded s3 data."
fi
exit $status