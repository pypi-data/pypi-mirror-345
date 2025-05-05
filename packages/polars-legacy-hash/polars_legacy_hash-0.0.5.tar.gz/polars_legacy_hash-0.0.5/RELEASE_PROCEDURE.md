1. Merge all the relevant branches
2. Create the release commit by updating the version in the Cargo.toml (this propagates into the python lib)
3. Push the release tag, and the pypi build will be triggered
4. 