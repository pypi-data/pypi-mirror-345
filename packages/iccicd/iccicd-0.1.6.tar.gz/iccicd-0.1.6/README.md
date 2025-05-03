# iccicd

This project is a collection of utilities for managing CI/CD pipelines at ICHEC.

It provides opinionated interfaces to encourage standarization of our project structures and workflows.

# Install

The package is available from PyPI:

```sh
pip install iccicd
```

# Features #

## Deploy a Package to a Repository

From the package's top-level directory:

```sh
iccicd deploy --token $REPO_TOKEN
```

As an example, for a Python project this might be the PyPI repository's token.

## Set a Package's Version Number

From the package's top-level directory:

```sh
iccicd set_version $VERSION
```

## Increment a Repository's Tag ##

From the repository's top-level directory, and on the branch the tag will be dervied from:

``` sh
iccicd increment_tag --field patch
```

Here `semver` tag versioning is assumed with a `major.minor.patch` scheme. Note: in a CI/CD pipeline some more input options are needed to initialize the git repo for pushing the tag to. You can use the `--help` flag for more details.

## Sync Content With an External Upstream ##

Here we pull content from an external upstream repository and use it to update the content in a local repo. This can be useful for public mirrors that include a subset of the content in an internal repo.

``` sh
iccicd sync_external_archive \
    --source_token $SOURCE_TOKEN \ 
    --project_id $SOURCE_PROJ_ID \
    --sync_script $MY_SYNC_SCRIPT \
    --asset_name $ASSET_NAME \
    --archive_name $ARCHIVE_NAME \
    --target_token $TARGET_TOKEN
```

The inputs are:

* `SOURCE_TOKEN`: Gitlab access token for the source (private) repo - must have asset download rights
* `SOURCE_PROJ_ID`: The numeric project ID for the source repo
* `MY_SYNC_SCRIPT`: Path to a script that will use the extracted contents of the source archive to update the target repo
* `ASSET_NAME`: Name of the asset corresponding to the archive in the source repo's latest release collection
* `ARCHIVE_NAME`: Name of the downloaded file corresponding to the archive - this can differ from the asset name.
* `TARGET_TOKEN`: OATH token for the target repo - so that it can be pushed to from a CI runner




# Licensing #

This project is licensed under the GPLv3+. See the accompanying `LICENSE.txt` file for details.

