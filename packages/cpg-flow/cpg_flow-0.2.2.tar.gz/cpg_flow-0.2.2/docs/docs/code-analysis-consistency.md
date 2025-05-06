# 🔍 Code Linting and Formatting

![Precommit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

In order to keep the code clean, consistent and free of bad python practices, more than **Over 10 pre-commit hooks are enabled** !

Complete list of all enabled rules is available in the **[.pre-commit-config.yaml file](https://github.com/populationgenomics/cpg-flow/blob/main/.pre-commit-config.yaml)**.

## ⚙️ Setup

!!! info
    Before linting, you must follow the [installation steps](installation.md#installation).

Then, run the following command

```bash
# Lint
pre-commit run --all-files
```

When setting up local linting for development you can also run the following once:

```bash
# Install the pre-commit hook
pre-commit install

# Or equivalently
make init || make init-dev
```

## 🥇 Project quality scanner

Multiple tools are set up to maintain the best code quality and to prevent vulnerabilities:

![SonarQube](https://img.shields.io/badge/-SonarQube-black?style=for-the-badge&logoColor=white&logo=sonarqube&color=4E9BCD)

SonarQube summary is available **[here](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)**.

[![Coverage](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=coverage&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Duplicated Lines (%)](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=duplicated_lines_density&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Quality Gate Status](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=alert_status&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)

[![Technical Debt](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=sqale_index&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Vulnerabilities](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=vulnerabilities&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Code Smells](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=code_smells&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)

[![Reliability Rating](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=reliability_rating&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Security Rating](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=security_rating&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Bugs](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=bugs&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
