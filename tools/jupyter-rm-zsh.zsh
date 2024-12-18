jupyter kernelspec list --json | jq -r '.kernelspecs | keys[]' | grep zsh | xargs jupyter kernelspec remove -y
