- There might be some scripts in [misc directory](/misc/) to help you setup a development environment.

- [Keep a Changelog](https://keepachangelog.com/en/0.3.0/).

- Update a [version value](/src/zsh_jupyter_kernel/version).

For owners:

- Create and push tags on version changes: 
```zsh
version=`cat version`
git tag -a $version -m $version
git push --follow-tags
```

- To release a new version follow a readme in [distribution directory](/dist/).
