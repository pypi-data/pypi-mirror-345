# Contributing to uynab

In order to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with Github

We use github to host code, to track issues and feature requests, as well as accept pull requests.

## Development environment

We use specific development environment, it is not necessary to use the same environment,
but having same or at least similar reduce the amount of time wasting for debugging not existent bugs.

In short, we use: 

- Python, version 3.10 or higher,
- UV, for the project management, 
- Ruff for formatting, 
- Pytest for testing,
- Make for making all the actions and setup easier.

For details checkout [Environment]() page

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests

Pull requests are the best way to propose changes to the codebase (we use [Github Flow](https://guides.github.com/introduction/flow/index.html)). We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints (use [ruff] formatter).
6. Issue that pull request!

## What do we need

Look at the [issues](https://github.com/ajwalkiewicz/uynab/issues) to see what is needed.

Unit tests are always welcome.

If you have any other suggestions feel welcome to open new [issue](https://github.com/ajwalkiewicz/uynab/issues).

## Any contributions you make will be under the MIT license

In short, when you submit code changes, your submissions are understood to be under the same [MIT](https://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](https://github.com/ajwalkiewicz/uynab/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/ajwalkiewicz/uynab/issues); it's that easy!

## Same for any features

Features or enhancements are welcome. Write an new [issue](https://github.com/ajwalkiewicz/uynab/issues) suggesting new feature or even better create your own pull request.

## Write bug reports with detail, background, and sample code

[This is an example](http://stackoverflow.com/q/12488905/180626) of a good bug report.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can. [My stackoverflow question](http://stackoverflow.com/q/12488905/180626) includes sample code that _anyone_ with a base python setup can run to reproduce what I was seeing
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People _love_ thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [ruff](https://docs.astral.sh/ruff/) formatter to style your code.

Following PEP's can help you write better and cleaner code:

- PEP 8
- PEP 484
- PEP 3107

In cases where PEP's differ from `ruff`, always choose `ruff`!

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md),
and modified accordingly for this project needs.