<div align="center"> <!-- markdownlint-disable MD041 MD033 -->
  <img src="/assets/KEYBOARD_HAPPY_FLOYD.png" alt="Logo" width="150"/>
</div>

# Contributing to CPG Flow

We appreciate your interest in contributing to CPG Flow! This project, sponsored by the Centre for Population Genomics, has a global community of contributors who have added significant value over time. This guide outlines how we manage external contributions to maximize their impact and reduce delays in getting your pull requests (PRs) reviewed and accepted.

## Share your idea with us first

Before diving into writing a substantial amount of code, we recommend reaching out by submitting an [issue](https://github.com/populationgenomics/cpg-flow/issues/new) to gather feedback. We may offer advice on the best way to approach the problem, and in some cases, there might be unforeseen challenges that could affect your solution. Catching these early can save time and effort, and help prevent your PR from being rejected due to overlooked constraints.

## Consider maintenance

The CPG software team continuously maintains and improves the application to meet the needs of both internal and external users. There may be instances where we recognize a feature or contribution as valuable, but we might not have the capacity to maintain it long-term. This could be due to project priorities or time limitations on the maintainers. Getting feedback early in the process can help avoid this situation.

## Pull request reviews

Reviewing PRs requires time and attention, so we prioritize them as part of our regular sprint planning. The team works in fortnightly sprints, which means if you submit a PR early in the cycle, it might take some time before it’s reviewed. We understand this can be frustrating and strive to provide updates on the status of your PR as promptly as possible.

## Commitlint and Commitizen

Releases on **main** branch are generated and published automatically,
pre-releases on the **alpha** branch are also generated and published by:

![Semantic Release](https://img.shields.io/badge/-Semantic%20Release-black?style=for-the-badge&logoColor=white&logo=semantic-release&color=000000)

It uses the **[conventional commit](https://www.conventionalcommits.org/en/v1.0.0/)** strategy.

This is enforced using the **[commitlint](https://github.com/opensource-nepal/commitlint)** pre-commit hook that checks commit messages conform to the conventional commit standard.

We recommend installing and using the tool **[commitizen](https://commitizen-tools.github.io/commitizen/) in order to create commit messages. Once installed, you can use either `cz commit` or `git cz` to create a commitizen generated commit message.
