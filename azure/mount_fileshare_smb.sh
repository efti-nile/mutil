#!/bin/bash


az_login() {
    if [ ! "$#" -eq 3 ]; then
        local USER="$1"
        local SECRET="$2"
        local TENANT="$3"
        az login --service-principal -u "$USER" -p "$SECRET" --tenant "$TENANT"
    else
        echo "Usage: az_login USER SECRET TENANT"
    fi
}


# Checks if a Azure fileshare is accessible through SMB.
az_check_smb() {
    if [ ! "$#" -eq 2 ]; then
        local RESOURCE_GROUP_NAME="$1"
        local STORAGE_ACCOUNT_NAME="$2"

        # The command below assumes you have logged in with `az login`.

        # Get the http endpoint, remove any double quotes.
        HTTP_ENDPOINT=$(az storage account show \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --name "$STORAGE_ACCOUNT_NAME" \
            --query "primaryEndpoints.file" --output tsv | tr -d '"')

        # Remove the protocol (first 7 characters).
        SMB_PATH=$(echo "$HTTP_ENDPOINT" | cut -c7-${#HTTP_ENDPOINT})

        # Remove all slashes.
        FILE_HOST=$(echo "$SMB_PATH" | tr -d "/")

        # Check the SMB port availability.
        nc -zvw3 $FILE_HOST 445
    else
        echo "Usage: az_check_smb RESOURCE_GROUP_NAME STORAGE_ACCOUNT_NAME"
    fi
}


# Mounts Azure file share to a specified folder.
az_mount_smb() {
    if [ "$#" -eq 4 ]; then
        local MNT_ROOT="$1"
        local RESOURCE_GROUP_NAME="$2"
        local STORAGE_ACCOUNT_NAME="$3"
        local FILESHARE_NAME="$4"

        # Create a folder for mounting the file share.
        MNT_PATH="$MNT_ROOT/$STORAGE_ACCOUNT_NAME/$FILESHARE_NAME"
        sudo mkdir -p "$MNT_PATH"

        # The command below assumes you have logged in with `az login`.

        # Get the HTTP endpoint and remove any double quotes.
        HTTP_ENDPOINT=$(az storage account show \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --name "$STORAGE_ACCOUNT_NAME" \
            --query "primaryEndpoints.file" --output tsv | tr -d '"')
        
        # Remove the protocol (first 7 characters).
        SMB_PATH=$(echo $HTTP_ENDPOINT | cut -c7-)$FILESHARE_NAME

        # Get the storage account key.
        STORAGE_ACCOUNT_KEY=$(az storage account keys list \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --account-name "$STORAGE_ACCOUNT_NAME" \
            --query "[0].value" --output tsv | tr -d '"')

        # Mount the file share to the specified point.
        sudo mount -t cifs "$SMB_PATH" "$MNT_PATH" -o username=$STORAGE_ACCOUNT_NAME,password=$STORAGE_ACCOUNT_KEY,serverino,nosharesock,actimeo=30,mfsymlinks
    else
        echo "Usage: az_mount_smb MNT_ROOT RESOURCE_GROUP_NAME STORAGE_ACCOUNT_NAME FILESHARE_NAME"
    fi
}
