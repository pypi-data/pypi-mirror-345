# CHANGELOG


## v0.2.2 (2025-05-05)

### Bug Fixes

- **create_multicohort**: Cache result on identical input_cohorts list
  ([`e5bcd63`](https://github.com/populationgenomics/cpg-flow/commit/e5bcd635061c94f589439c4604c4751eed8d4e6f))

This is a proposed solution to Issue #79 where each call to get_multicohort is re-creating the
  cohort object again from scratch. This results in many more calls to the Metamist API than
  required. The cache on create_multicohort will resue the result rather than recreate it.

Resolves Issue #79, SET-568

### Documentation

- Add comment to get_multicohort()
  ([`35460ed`](https://github.com/populationgenomics/cpg-flow/commit/35460ed5424d27a29e4998b01433172d82526705))

### Testing

- Fix tests that mock create_multicohort & fix cohort ids in configs
  ([`9d5bebc`](https://github.com/populationgenomics/cpg-flow/commit/9d5bebc79898d495df0909b47918eba578902c60))


## v0.2.1 (2025-04-10)

### Bug Fixes

- Trigger a release by having a fix commit
  ([`41f6aa1`](https://github.com/populationgenomics/cpg-flow/commit/41f6aa147b05e0711e220477c817cbcfded020ce))

### Continuous Integration

- Add manual ci-build
  ([`bf8386a`](https://github.com/populationgenomics/cpg-flow/commit/bf8386a04329575b410767473d0b448d43e7cbb8))

- Publish on push to this branch
  ([`c23146c`](https://github.com/populationgenomics/cpg-flow/commit/c23146c2f3fa8f8974f689b583731d1aa0662400))

- Rm package on this branch and uncomment if
  ([`c13e396`](https://github.com/populationgenomics/cpg-flow/commit/c13e396f8063258eaaf4fb777a43117bc78d97bc))

- Switch to trusted publisher and change ci-build to rm local version
  ([`7fb5a22`](https://github.com/populationgenomics/cpg-flow/commit/7fb5a2287327853c5c7c357ad4d1828f869e8ac1))

- Update all workflow steps to latest versions
  ([`2995d82`](https://github.com/populationgenomics/cpg-flow/commit/2995d828f20e554fd413528c7c6fbf7c426a7132))

### Refactoring

- Add .dummy
  ([`d5c8038`](https://github.com/populationgenomics/cpg-flow/commit/d5c8038007045ab74ad39bac3a1ab901b24e7274))


## v0.2.0 (2025-03-31)

### Bug Fixes

- **Cohort**: Remove the .analysis_dataset property
  ([`b648fe3`](https://github.com/populationgenomics/cpg-flow/commit/b648fe39eb4d24b3dcac1e7e311db9e6f0e33fc7))

After discussion on the PR the thought is to remove it to reduce confusion.

- **Stage**: Fetch project_name for Cohort to use .dataset
  ([`0f7430d`](https://github.com/populationgenomics/cpg-flow/commit/0f7430d5ae85c53699d2f1a2f0fc0a48a6e11406))

### Code Style

- Fix ruff-format pre-commit hook and commit ruff fixes
  ([`a3c3b38`](https://github.com/populationgenomics/cpg-flow/commit/a3c3b38da08dbc9d399fb6194c6e0fd59a45f650))

### Documentation

- **mkdocs**: Replicate changes made to the README.md
  ([`1fb606b`](https://github.com/populationgenomics/cpg-flow/commit/1fb606b72a8de672069c44d1a12fe09539a91fcf))

### Features

- **Cohort**: Add dataset attribute to Cohort target
  ([`4a5c22c`](https://github.com/populationgenomics/cpg-flow/commit/4a5c22c564418095cf9d4351dbc11cac9d27dd2c))

This PR will solve the raised issue #75 where the Cohort target currently does not have access to
  its own dataset (as an attribute) in order to save output files. The proposed solution is as
  follows.

We keep the analysis_dataset property available in order to maintain the current functionality of
  existing pipelines.

This also means in future this gives the power to the Pipeline Developers to choose the most
  appropriate place to save the outputs:

* In the analysis_dataset as defined in the config provided to the analysis_runner (the same one as
  used in the MultiCohortStage)

* The dataset as pulled from the metadata in Metamist to save each respective Cohorts results in its
  respective dataset location.

This naming convention is also consistent with say SequencingGroups which don't have an
  analysis_dataset attribute only a dataset attribute which is determined entirely by metadata on
  that individual sequencing group (pulled from metamist).

We could discuss whether it would be a helpful feature for all Target types to have access to this
  analysis_dataset property or not. That would come down to whether it's needed, or useful or would
  just cause confusion.

SET-490, Resolves #75

### Testing

- Update cohort test data and mocks
  ([`859b631`](https://github.com/populationgenomics/cpg-flow/commit/859b631328bb3f93817e64740c472acb2fd5e5ad))

Make the dataset argument option for the multicohort.create_cohort method (since it is optional in
  the class constructor). Also, add the dataset to all of our mock test data.


## v0.1.3 (2025-03-11)

### Bug Fixes

- **Workflow**: Catch the correct ConnectionError and rm useless log line
  ([`eba1c37`](https://github.com/populationgenomics/cpg-flow/commit/eba1c37714456f87e87a0169dde19de0f46a4aa2))

This change was motivated by the local dry_run of cpg-flow always failing by attempting to contact
  metamist. By catching the appropriate error this is no longer the case. We also log a final line
  with dry_run complete.

SET-448

### Build System

- Removes cpg-flow from deps
  ([`7063dcb`](https://github.com/populationgenomics/cpg-flow/commit/7063dcb844eac9d75d38cd992d57e77db837f8d0))

- **Dockerfile,pyproject.toml**: Bump uv version in Dockerfile
  ([`feecc9c`](https://github.com/populationgenomics/cpg-flow/commit/feecc9c25d5af7405575da0a1fdb5a9b346f475b))

- **uv.lock**: Pin cryptography [security]
  ([`c30380c`](https://github.com/populationgenomics/cpg-flow/commit/c30380cbfb15cc3795e69feef6d12517fc31ebdd))

### Continuous Integration

- **.github/workflows/package.yaml,pyproject.toml,uv.lock**: Add step to publish tagged versions on
  docs
  ([`f32bd9f`](https://github.com/populationgenomics/cpg-flow/commit/f32bd9f84255c88524d364b51de133ec03b77fdc))

### Documentation

- **mkdocs.yml,docs/index.md**: Adding versioning to docs
  ([`8a56baa`](https://github.com/populationgenomics/cpg-flow/commit/8a56baa4de8e5c0a632f56048c9e4e6eb7f99080))

- **README.md**: Fix installation instructions for users vs devs
  ([`cd64b13`](https://github.com/populationgenomics/cpg-flow/commit/cd64b1319494fe5c56074df9df0ee7ddfda1ae64))

### Testing

- Move test data into assets/
  ([`b2f5b61`](https://github.com/populationgenomics/cpg-flow/commit/b2f5b61348851bfcc4f985ae4c5b868a8ee50aba))

SET-369

- **test_cohort**: Fix bug in mock get_analyses_by_sgid
  ([`c071979`](https://github.com/populationgenomics/cpg-flow/commit/c07197948a0c8a44ae29d68b23dcce1c40622fb7))


## v0.1.2 (2025-02-05)

### Bug Fixes

- **stage.py**: As_str to take in path as well as str
  ([`d50a994`](https://github.com/populationgenomics/cpg-flow/commit/d50a994896124f6c645bdbf861f29c9372012f98))

current method not useful, make it make sense


## v0.1.1 (2025-02-02)

### Bug Fixes

- **docker.yaml**: Add condition to only push versioned image on bump
  ([`06f7326`](https://github.com/populationgenomics/cpg-flow/commit/06f73261323b40eeec5c830a45f094bb665d4975))


## v0.1.0 (2025-01-28)

### Continuous Integration

- **.github/workflows**: Cleanup packaging workflow
  ([`9fca024`](https://github.com/populationgenomics/cpg-flow/commit/9fca024a88bd8dc1aaa2029594a5bdbf1e24bc68))

- **.github/workflows/package.yaml**: Add p.a.t for package checkout
  ([`e6a2a77`](https://github.com/populationgenomics/cpg-flow/commit/e6a2a7708412c96690e9bf5a43afa9cf28a439fc))

- **.github/workflows/package.yaml**: Reverted package workflow to working state
  ([`da95c2a`](https://github.com/populationgenomics/cpg-flow/commit/da95c2a90cfd6f9947d8d30225f43b3d41c240ab))

- **.github/workflows/updated-badges.yaml**: Remove update badges workflow
  ([`b508ba4`](https://github.com/populationgenomics/cpg-flow/commit/b508ba4a5e01874c7257cd5c91bcb7a6d47d35a2))

- **.github/workflows/web-docs.yaml,docs/update_readme.py,Makefile,.pre-commit-config.yaml**: Fix
  docs workflow, remove update-readme pre-commit hook
  ([`888afd1`](https://github.com/populationgenomics/cpg-flow/commit/888afd1e72519c59ee295850f6fc2e22467684c3))

- **package.yaml**: Rm update alpha action
  ([`c94d52f`](https://github.com/populationgenomics/cpg-flow/commit/c94d52f87109bb4b58b7a9f2eae548e16cdcc68b))

- **update-badges.yaml**: Push with cpg ci bot
  ([`c148f8e`](https://github.com/populationgenomics/cpg-flow/commit/c148f8e68700c26022d8fe3089a7fc4f47b0c0d5))

- **web-docs.yaml**: Add uv run
  ([`cf50620`](https://github.com/populationgenomics/cpg-flow/commit/cf506203dd7080bfb16d36d4aba48939785b270e))

### Documentation

- **docs/docs/index.md**: Remove broken docs links
  ([`01c0651`](https://github.com/populationgenomics/cpg-flow/commit/01c06518ed8de867c2e7ca01b543c2dff18aa537))

- **README.md**: Remove badges
  ([`2d2d200`](https://github.com/populationgenomics/cpg-flow/commit/2d2d2006e35392976edc81c201bd334af34d4862))

- **README.md,docs/docs/index.md**: Remove more broken docs links
  ([`2d6f900`](https://github.com/populationgenomics/cpg-flow/commit/2d6f900e1154af58df93132dd88cbb0813a993de))


## v0.1.0-alpha.18 (2025-01-28)

### Bug Fixes

- **./,src/cpg_flow/**: Merge alpha
  ([`953181e`](https://github.com/populationgenomics/cpg-flow/commit/953181e597fd7b9b064d471679f9a442a9266a9c))

- **README.md**: Merge alpha
  ([`0d0735f`](https://github.com/populationgenomics/cpg-flow/commit/0d0735fe1e4eaf02b57eb34f8cb3d037bece1187))

### Build System

- **Makefile**: Refactor docs command to use mkdocs
  ([`8628f3b`](https://github.com/populationgenomics/cpg-flow/commit/8628f3b43e50a84e6745016e6a6b0717826e18de))

### Chores

- Update badges.yaml with test results and coverage
  ([`b88bf6e`](https://github.com/populationgenomics/cpg-flow/commit/b88bf6eb295d6b8def6e18678e7b923e616b23a9))

- Update badges.yaml with test results and coverage
  ([`6b66a51`](https://github.com/populationgenomics/cpg-flow/commit/6b66a51ffeaffaa08f7c7eef21b55f663bf7de6b))

### Documentation

- **docs/docs,-README.md,-uv.lock,-pyproject.toml**: Setup mkdocs
  ([`10b16ab`](https://github.com/populationgenomics/cpg-flow/commit/10b16ab60840b73c2eed10f636cb30f301ac6b02))

- **README.md**: Cleaup badges
  ([`e148dda`](https://github.com/populationgenomics/cpg-flow/commit/e148dda76f6744f393bec77b3bc2881a5d54aff5))

- **README.md**: Run new pre-commit hook from alpha
  ([`eb98c1e`](https://github.com/populationgenomics/cpg-flow/commit/eb98c1e29ee0e01fd2925c7e4ecb08fdd27d48a7))

### Features

- **README.md,graph.py**: Major show workflow improvements
  ([`55def6b`](https://github.com/populationgenomics/cpg-flow/commit/55def6b5816b72f9c3c94fbd169484bc44d85995))


## v0.1.0-alpha.17 (2025-01-15)

### Bug Fixes

- **./,.github/workflows/**: Mv update readme to pre-commit
  ([`3afe591`](https://github.com/populationgenomics/cpg-flow/commit/3afe5918e71991ac58244dea2583c7060d4a9fff))

- **./,.github/workflows/,docs/**: Bug in update_readme
  ([`8f37ef2`](https://github.com/populationgenomics/cpg-flow/commit/8f37ef25dec0f0ab13e2bcdbc3ae7dcfb0292cea))

- **./,.github/workflows/,docs/**: Fix when CI runs
  ([`516eedd`](https://github.com/populationgenomics/cpg-flow/commit/516eedd4e11ad6b0245bb5a5faa561f7ce1b57e2))

- **docs/update_readme.py**: Show diff on edit
  ([`fcc990f`](https://github.com/populationgenomics/cpg-flow/commit/fcc990ff0dff954b74c4ab67faae13a701fde7ce))

- **README.md,docs/update_readme.py**: Sort list of workflows
  ([`249399d`](https://github.com/populationgenomics/cpg-flow/commit/249399d7cd7bef2f34a1b335595ef5064e729831))

### Build System

- **.pre-commit-config.yaml**: Update-readme config
  ([`b6451a2`](https://github.com/populationgenomics/cpg-flow/commit/b6451a28241705e71696c16dd58af31ecfa6d333))

### Chores

- Update badges.yaml with test results and coverage
  ([`f482f9b`](https://github.com/populationgenomics/cpg-flow/commit/f482f9bd8d5475d56f0467312ca664cca049eba2))

- Update badges.yaml with test results and coverage
  ([`5574626`](https://github.com/populationgenomics/cpg-flow/commit/5574626f58d312a30a065ede403d07b6317a719a))

- Update badges.yaml with test results and coverage
  ([`cb52d5e`](https://github.com/populationgenomics/cpg-flow/commit/cb52d5e2d739785bc8900ebca4e2e3376f537ea8))

### Code Style

- **.github/workflows/lint.yaml,security.yaml**: Formatting
  ([`fe55314`](https://github.com/populationgenomics/cpg-flow/commit/fe55314ab85b450eb998ff049315cac8f7c44eaa))

### Continuous Integration

- **./,.github/workflows/**: Rm pull_request
  ([`a4eec4d`](https://github.com/populationgenomics/cpg-flow/commit/a4eec4dc549c00c66764444911fcdc4d4847ef1b))

- **.github/workflows/package.yaml**: Fix condition
  ([`31f5464`](https://github.com/populationgenomics/cpg-flow/commit/31f54642f9d20652709d81192232effd9b231e16))

- **.github/workflows/test.yaml,web-docs.yaml**: Update Install uv
  ([`6efe601`](https://github.com/populationgenomics/cpg-flow/commit/6efe601a9e2a94faf51a0529fddb3c5f0d98f05b))

- **package.yaml,test.yaml**: Github.ref -> github.ref_name
  ([`b1311b5`](https://github.com/populationgenomics/cpg-flow/commit/b1311b54503f21e371af83a9723921622ff44fdd))

- **web-docs.yaml**: Change var name
  ([`f7406eb`](https://github.com/populationgenomics/cpg-flow/commit/f7406eb6bf1607adc4f57e24bbf624655f682f19))

- **web-docs.yaml**: Fix uv install
  ([`b1761ac`](https://github.com/populationgenomics/cpg-flow/commit/b1761ac21627232e0f72c84589dbfb0ec8d28c67))

- **web-docs.yaml**: Reorder steps
  ([`9ca2194`](https://github.com/populationgenomics/cpg-flow/commit/9ca2194ddb369306a319051ed485c685a177da48))

- **web-docs.yaml**: Run on push
  ([`bc721a4`](https://github.com/populationgenomics/cpg-flow/commit/bc721a4f48e17d2a2508685f0999088e3afd8fa9))

- **web-docs.yaml**: Update if
  ([`9b05cb2`](https://github.com/populationgenomics/cpg-flow/commit/9b05cb22629cc5c0c8a03ba7f01b690a5dde633f))


## v0.1.0-alpha.16 (2025-01-15)

### Bug Fixes

- Add logging statements to help find bug
  ([`d439901`](https://github.com/populationgenomics/cpg-flow/commit/d4399019ecde919feba2b0b103797c129297672e))

- Add original change and extra log statement
  ([`aa44f2b`](https://github.com/populationgenomics/cpg-flow/commit/aa44f2b7921342cb74cd71abc43b8993459e615a))

to continue testing

- Undo name change to check error and provide informative logs
  ([`048db79`](https://github.com/populationgenomics/cpg-flow/commit/048db791c3205a74dcceaf6196b64f615f4e7fa5))

- **graph.py**: Fix bug with _get_node_color default
  ([`7bd8093`](https://github.com/populationgenomics/cpg-flow/commit/7bd8093d7f4828f81b2bb65400d4cfc139d13407))

### Build System

- **sonar-project.properties**: Optimise settings
  ([`78f9f50`](https://github.com/populationgenomics/cpg-flow/commit/78f9f50fe4688605dad88bd55480bd3e1c812db4))

### Chores

- Make docs update
  ([`4aa5dca`](https://github.com/populationgenomics/cpg-flow/commit/4aa5dcae37b7609b29dbaee3f5651580079bc613))

- Make docs update
  ([`4842144`](https://github.com/populationgenomics/cpg-flow/commit/484214478fd017375b05101515565afc100b4dc3))

- Make docs update
  ([`1259329`](https://github.com/populationgenomics/cpg-flow/commit/12593294bad530f60cdea55ad1230ce3f09ab975))

- Make docs update
  ([`210da09`](https://github.com/populationgenomics/cpg-flow/commit/210da09e7101e75d4e4e97c627a954103deeea21))

- Make docs update
  ([`1f4cbe8`](https://github.com/populationgenomics/cpg-flow/commit/1f4cbe870889d1c4e099bd46afcfd959d1ed7d65))

- Make docs update
  ([`1100f7f`](https://github.com/populationgenomics/cpg-flow/commit/1100f7f6a2b26775c36a5caf26bc28f960ad56ed))

- Make docs update
  ([`b3a77eb`](https://github.com/populationgenomics/cpg-flow/commit/b3a77ebb7e525b484267e67f2fc3b2a5b9f19d74))

- Make docs update
  ([`af3b29b`](https://github.com/populationgenomics/cpg-flow/commit/af3b29b8a11af0cc545b22792a30c37286f606b3))

- Update badges.yaml with test results and coverage
  ([`2b7c222`](https://github.com/populationgenomics/cpg-flow/commit/2b7c2223953f91573f0e77701f7b2ec497244c4f))

- Update badges.yaml with test results and coverage
  ([`0588ce1`](https://github.com/populationgenomics/cpg-flow/commit/0588ce103d143e186d75283bb2f685c935f0bcfd))

- Update badges.yaml with test results and coverage
  ([`3eef434`](https://github.com/populationgenomics/cpg-flow/commit/3eef43447682aa8b0b429fae53c423349f94450d))

### Code Style

- Remove verbose logging and comments
  ([`c87879f`](https://github.com/populationgenomics/cpg-flow/commit/c87879fe972d00d2eefdfe1719680f2ac6b4b507))

testing artifacts

### Continuous Integration

- **.github/workflows/package.yaml,web-docs.yaml**: Add secret
  ([`9ba0907`](https://github.com/populationgenomics/cpg-flow/commit/9ba0907f91d0e9fce1cd50a0be3ffb31151b5f04))

- **Makefile**: Add extra ls in make docs
  ([`444ef0d`](https://github.com/populationgenomics/cpg-flow/commit/444ef0d8119d7937418a5471a4b776b63337e412))

- **Makefile**: Fix if
  ([`38d6702`](https://github.com/populationgenomics/cpg-flow/commit/38d6702c3ea39a44a99932d06186fbf635a4955b))

- **Makefile**: If statement fix
  ([`39a4586`](https://github.com/populationgenomics/cpg-flow/commit/39a4586e326a5d9ea5ee05167117cd2b6fbeb9d1))

- **Makefile**: Move if to one line
  ([`769dff8`](https://github.com/populationgenomics/cpg-flow/commit/769dff834bfe94ea5661af074f08a2cbb8d59198))

- **Makefile,README.md**: Make docs command fixed
  ([`1085947`](https://github.com/populationgenomics/cpg-flow/commit/10859478b9e2f539892fd11d392d6ef12673d008))

- **package.yaml**: Only package on test success or workflow_dispatch
  ([`75ff6c7`](https://github.com/populationgenomics/cpg-flow/commit/75ff6c7a261a92457f74ec22dfeff7f9040aebf6))

- **web-docs.yaml**: Debug git push
  ([`ec7d385`](https://github.com/populationgenomics/cpg-flow/commit/ec7d385785b6c7864b8ad1b91156b932af6cd1e5))

- **web-docs.yaml**: Debug git push
  ([`7d9e9ae`](https://github.com/populationgenomics/cpg-flow/commit/7d9e9aef10071b47df986d0ecf020744a9fe9589))

- **web-docs.yaml**: Debug git push
  ([`15d3024`](https://github.com/populationgenomics/cpg-flow/commit/15d3024d7e5b093457033f7be5ff854966b04503))

- **web-docs.yaml**: Debug git push
  ([`6ffa3f7`](https://github.com/populationgenomics/cpg-flow/commit/6ffa3f755d44426adfb29c4897f2a68542057658))

- **web-docs.yaml**: Debug push
  ([`af31d11`](https://github.com/populationgenomics/cpg-flow/commit/af31d11b000e5ee224bbb3ac3cfadc4f71394d73))

- **web-docs.yaml**: Debugging git push
  ([`eda60d7`](https://github.com/populationgenomics/cpg-flow/commit/eda60d70eaba2f803c32e1774d5782d7a228958b))

- **web-docs.yaml**: Fix git push
  ([`296ac5d`](https://github.com/populationgenomics/cpg-flow/commit/296ac5d8715c81fc539b0846a6f39060f87f9494))

- **web-docs.yaml**: Fix rm in push
  ([`884c042`](https://github.com/populationgenomics/cpg-flow/commit/884c0424f6b9de00cc389a09395004fb0c7d999a))

- **web-docs.yaml**: Fix token
  ([`5ca47de`](https://github.com/populationgenomics/cpg-flow/commit/5ca47de1563e9710c8c2903bd3d21cb144711ddd))

- **web-docs.yaml**: Fix uv install on web docs ci
  ([`043cb87`](https://github.com/populationgenomics/cpg-flow/commit/043cb87a6c49ab16a15bf37153d0a006bfafaa14))

- **web-docs.yaml**: Only push if there's a change
  ([`8b7ab0e`](https://github.com/populationgenomics/cpg-flow/commit/8b7ab0e8665d0cd356f29dcd3c9e0fbf6e314bcb))

- **web-docs.yaml**: Push doc changes to branch
  ([`a612c4f`](https://github.com/populationgenomics/cpg-flow/commit/a612c4f1ba0b41a5efcb20f44e4af0a63dd6057a))

- **web-docs.yaml**: Show generated files
  ([`0b20530`](https://github.com/populationgenomics/cpg-flow/commit/0b205300c69f35704fe8b908b782774add60a50c))

- **web-docs.yaml,Makefile**: Add ls to make docs command
  ([`82393c0`](https://github.com/populationgenomics/cpg-flow/commit/82393c048407b311dd1c439b80bff8d3f4ba704c))

- **web-docs.yaml,Makefile**: Pass in branch to make docs
  ([`e5c87e5`](https://github.com/populationgenomics/cpg-flow/commit/e5c87e55ebffde5bce951c6c452f08db1044a726))

### Documentation

- **workflow_descriptions.yaml**: Fix typo in web-docs.yaml key
  ([`d5ceb8e`](https://github.com/populationgenomics/cpg-flow/commit/d5ceb8e07fb1125a083cd816b3c90c50c03a0d62))

### Refactoring

- **package.yaml,web-docs.yaml-,+17**: Rm generated code
  ([`53d53da`](https://github.com/populationgenomics/cpg-flow/commit/53d53da512ec2624d6d202edf0f0e5e4a0b865bb))


## v0.1.0-alpha.15 (2025-01-13)

### Bug Fixes

- Migrate prod pipes PR#951
  ([`7f16948`](https://github.com/populationgenomics/cpg-flow/commit/7f169485444438ae260ae10dbfea1c5d022c6b8a))

- Replicate prod pipes PR#1068
  ([`cf782c9`](https://github.com/populationgenomics/cpg-flow/commit/cf782c93686ec4346e3730af165a892986cf68fc))

- **defaults.toml**: Remove unnecessary options and add more comment
  ([`57f80ca`](https://github.com/populationgenomics/cpg-flow/commit/57f80ca6eb4e92efca56a751e5aea60bf5cc07c8))

- **graph.py**: Rm search in repo for stages (removed in cpg_flow)
  ([`648e7d7`](https://github.com/populationgenomics/cpg-flow/commit/648e7d7b269c80150640abbd0fdc422e411e29cc))

- **inputs.py,tests/test_multicohort.py**: Replicate prod pipes PR#989
  ([`f1d6fcd`](https://github.com/populationgenomics/cpg-flow/commit/f1d6fcdbd6390c0d6eaa09ae72f589294f90e2ef))

- **Makefile**: Add debug pwd/ls
  ([`282f62c`](https://github.com/populationgenomics/cpg-flow/commit/282f62c40223de18769f22f3fd470db57f5d01e7))

- **Makefile**: Add uv to to init commands
  ([`44ac58d`](https://github.com/populationgenomics/cpg-flow/commit/44ac58d3c29e323b1ab0e94490c33293ef93b79a))

- **multicohort**: Replace multicohort name with hash
  ([`7ce04bd`](https://github.com/populationgenomics/cpg-flow/commit/7ce04bda8ed4b0cd9efb3984679b3e8c15ee3770))

multicohort.name too long for *nix. hash will be static in length

- **package.yaml,Makefile**: Install uv, uv sync
  ([`5fcadd9`](https://github.com/populationgenomics/cpg-flow/commit/5fcadd9d9743993feeaffc4f77442d36da1d207e))

- **package.yaml,Makefile**: Make docs out of ci-build command
  ([`4df965b`](https://github.com/populationgenomics/cpg-flow/commit/4df965bf9e74594abc8cee4b7c5a2203319f4325))

- **pyproject.toml,src/cpg_flow/metamist.py-,+5**: Merge alpha
  ([`84ef763`](https://github.com/populationgenomics/cpg-flow/commit/84ef7632eae5abab9c1ef2fa4b3ed6f423d22e85))

- **src/cpg_flow/,tests/**: Metamist custom cohort mock fixed
  ([`1bb0ddd`](https://github.com/populationgenomics/cpg-flow/commit/1bb0ddd6c6bfb67fbb7be8531c423b4610786c05))

- **src/cpg_flow/workflow.py**: Create write_to_gcs_bucket
  ([`0452eb8`](https://github.com/populationgenomics/cpg-flow/commit/0452eb8c588ff328d9dc3b2b41c31f41fa40a83b))

- **src/cpg_flow/workflow.py**: Don't fail on connection error
  ([`0348bd4`](https://github.com/populationgenomics/cpg-flow/commit/0348bd47236ca92973404413eaa036a1aacc0131))

- **src/cpg_flow/workflow.py**: Fix 'skipped' attr missing in nx graph
  ([`1c64e6b`](https://github.com/populationgenomics/cpg-flow/commit/1c64e6bdf7e680ed01c6fb844ff95a2caf098a40))

- **src/cpg_flow/workflow.py**: Fix bucket/blob name
  ([`ebfe31a`](https://github.com/populationgenomics/cpg-flow/commit/ebfe31a2af795232cf512d690e0ebd0f061ce596))

- **src/cpg_flow/workflow.py**: Fix bug on 577 to use str
  ([`89ff6fe`](https://github.com/populationgenomics/cpg-flow/commit/89ff6fed88a83a237768252b2cac78a599fd463f))

- **src/cpg_flow/workflow.py**: Fix plotly plot save
  ([`d3e70a6`](https://github.com/populationgenomics/cpg-flow/commit/d3e70a6a5cd33ffb22e1425a8e553f00a3e2b68a))

- **src/cpg_flow/workflow.py**: Fix url path
  ([`bb0e839`](https://github.com/populationgenomics/cpg-flow/commit/bb0e83949b9c1ff55d002bf884374897ae38d1d1))

- **src/cpg_flow/workflow.py**: Get_alignment_inputs_hash()
  ([`71ccd0c`](https://github.com/populationgenomics/cpg-flow/commit/71ccd0c9cb4daac23db6e4bc73af702fedabe3c9))

- **src/cpg_flow/workflow.py**: Info log the url
  ([`def1d03`](https://github.com/populationgenomics/cpg-flow/commit/def1d031ee97aaf81cf2892c7267b839cf975c15))

- **src/cpg_flow/workflow.py**: Rm () from self.web_prefix
  ([`7d4f9b3`](https://github.com/populationgenomics/cpg-flow/commit/7d4f9b3e681c7c5fd9f8858d2b6cf2e4303c88ee))

- **src/cpg_flow/workflow.py**: Use builtin web_prefix method
  ([`6362036`](https://github.com/populationgenomics/cpg-flow/commit/63620365bc71ab957d1cdd555bb62379d9ef5cba))

- **src/cpg_flow/workflow.py**: Write_to_gcs_bucket convert to str
  ([`b782cfa`](https://github.com/populationgenomics/cpg-flow/commit/b782cfaf95cf9cc705cc631f85c86ffb87de9b9b))

### Build System

- **pyproject.toml,uv.lock**: Add pre-commit as core dep
  ([`f03ecaf`](https://github.com/populationgenomics/cpg-flow/commit/f03ecafe99dd5d0042d6c58f27b0bfd26a71fc94))

### Chores

- Update badges.yaml with test results and coverage
  ([`52aa984`](https://github.com/populationgenomics/cpg-flow/commit/52aa9841781820c5c43936f351cea678440e2209))

- Update badges.yaml with test results and coverage
  ([`1994f07`](https://github.com/populationgenomics/cpg-flow/commit/1994f07de95f0bdccaac68ff465130e3c0196df2))

- Update badges.yaml with test results and coverage
  ([`ba9fdb8`](https://github.com/populationgenomics/cpg-flow/commit/ba9fdb8b9125bf0bbafa9ee0955a6780b867118f))

- Update badges.yaml with test results and coverage
  ([`7f2b1ff`](https://github.com/populationgenomics/cpg-flow/commit/7f2b1ff4b8442936fe1c568aecc5832a59f086c3))

- Update badges.yaml with test results and coverage
  ([`0a93026`](https://github.com/populationgenomics/cpg-flow/commit/0a9302638ed75acfe2a0858516f2b8ca00d7c4f2))

- Update badges.yaml with test results and coverage
  ([`cd46929`](https://github.com/populationgenomics/cpg-flow/commit/cd46929ddda6de27010f3428625f23060d86b72c))

- Update badges.yaml with test results and coverage
  ([`9cfccdb`](https://github.com/populationgenomics/cpg-flow/commit/9cfccdbd8c5681b3a56a083aba61d130282f9422))

- Update badges.yaml with test results and coverage
  ([`d3664b4`](https://github.com/populationgenomics/cpg-flow/commit/d3664b4937b11dfd6f5bc216cf3d822a734d461a))

- Update badges.yaml with test results and coverage
  ([`28a23d6`](https://github.com/populationgenomics/cpg-flow/commit/28a23d682e92dbd259083b990a2a6fe6353b09f7))

- Update badges.yaml with test results and coverage
  ([`837d6ba`](https://github.com/populationgenomics/cpg-flow/commit/837d6ba911bc47b665a18e920d915417773039ac))

- Update badges.yaml with test results and coverage
  ([`189c60b`](https://github.com/populationgenomics/cpg-flow/commit/189c60bbdb48766dc6e491ead97bf36c300b3f55))

- Update badges.yaml with test results and coverage
  ([`28eac64`](https://github.com/populationgenomics/cpg-flow/commit/28eac6433c9f9d62bd99d9de7114d6f9a09be047))

- Update badges.yaml with test results and coverage
  ([`b0c3331`](https://github.com/populationgenomics/cpg-flow/commit/b0c333119e3c11a8a66e9ed66a81a64285fc48ea))

- Update badges.yaml with test results and coverage
  ([`54d505d`](https://github.com/populationgenomics/cpg-flow/commit/54d505d9a5bf174f934bfdee64886842842eb9ee))

- Update badges.yaml with test results and coverage
  ([`2deb20b`](https://github.com/populationgenomics/cpg-flow/commit/2deb20b5dc1e9ba8b9c5088ee8a3ecd9240166c7))

- Update badges.yaml with test results and coverage
  ([`5f70383`](https://github.com/populationgenomics/cpg-flow/commit/5f70383ede7d4b4232bd3ecc57966ca9f06795c3))

- Update badges.yaml with test results and coverage
  ([`1605c75`](https://github.com/populationgenomics/cpg-flow/commit/1605c7576efedd48741bc293ebde97d8719be366))

- Update badges.yaml with test results and coverage
  ([`5ee9b6d`](https://github.com/populationgenomics/cpg-flow/commit/5ee9b6dca33b1920a7c60e29da57d14bc8a1418c))

- Update badges.yaml with test results and coverage
  ([`bf48667`](https://github.com/populationgenomics/cpg-flow/commit/bf48667521560337747ac4d3bbe36d72bc47005b))

- Update badges.yaml with test results and coverage
  ([`e50ab94`](https://github.com/populationgenomics/cpg-flow/commit/e50ab94dce6059609e2deb8cb1bd56d0ca632b56))

- Update badges.yaml with test results and coverage
  ([`478d74a`](https://github.com/populationgenomics/cpg-flow/commit/478d74a0572b61875686c5130a66e513e5519a42))

- Update badges.yaml with test results and coverage
  ([`2174a17`](https://github.com/populationgenomics/cpg-flow/commit/2174a178b942609670fca46d2407d71d841d6254))

- Update badges.yaml with test results and coverage
  ([`5dad740`](https://github.com/populationgenomics/cpg-flow/commit/5dad740cebc6b84ce41e0eeb319d3bb33b51e02b))

### Continuous Integration

- **docker.yaml**: Echo out the docker tag
  ([`c991340`](https://github.com/populationgenomics/cpg-flow/commit/c991340339a58a9752fb74094d925474bcf40dd1))

- **Makefile**: Add uv run to all docs commands
  ([`9d9bc00`](https://github.com/populationgenomics/cpg-flow/commit/9d9bc00e6c696c569ef120f6743b714699356061))

- **Makefile**: Fail make docs command to prevent relase
  ([`5f6f6bd`](https://github.com/populationgenomics/cpg-flow/commit/5f6f6bda2ded1e393626e835d86f9a401125e131))

- **package.yaml**: Add package run on push to alpha to debug
  ([`248ab87`](https://github.com/populationgenomics/cpg-flow/commit/248ab8769f4f1f08a3dc5b238253c62cabfea030))

- **package.yaml**: Continue on error build docs
  ([`4666ccb`](https://github.com/populationgenomics/cpg-flow/commit/4666ccb1b864e044091c345447d3a2d944de9182))

- **package.yaml**: Rm if for main/alpha
  ([`3e2a8b4`](https://github.com/populationgenomics/cpg-flow/commit/3e2a8b4e144db1ba47267b5a904970906cd4e5c6))

- **package.yaml**: Run on PR to alpha
  ([`b7d54d1`](https://github.com/populationgenomics/cpg-flow/commit/b7d54d1e5f08e47cb322d8cbd62e24752e7cef27))

- **package.yaml**: Run on push to alpha, re-add if condition
  ([`8cdf8cf`](https://github.com/populationgenomics/cpg-flow/commit/8cdf8cf4445dfc092caffa5c7f245d7d0d143daf))

- **test.yaml**: Cat badge data
  ([`3221492`](https://github.com/populationgenomics/cpg-flow/commit/322149295ce4c2b61e791e3e27ed9a6667ba6079))

- **test.yaml**: Fix removed code in test.yaml
  ([`f353a89`](https://github.com/populationgenomics/cpg-flow/commit/f353a89da5aeffe9584f3cc3256d5763838a07db))

- **update-badges.yaml**: Add git pull
  ([`cbca5c4`](https://github.com/populationgenomics/cpg-flow/commit/cbca5c4b6100473379a0e7d8d0ddb1b4d430a56f))

- **update-badges.yaml**: Add token to checkout
  ([`2e5de8c`](https://github.com/populationgenomics/cpg-flow/commit/2e5de8caad7ee2727a4983ad26496c9a14425542))

- **update-badges.yaml**: Commit with ci bot
  ([`ff8561c`](https://github.com/populationgenomics/cpg-flow/commit/ff8561cbf7e19945d5d3e188a4a162cde1a117e6))

- **update-badges.yaml**: Continue push on fail
  ([`d3fed1b`](https://github.com/populationgenomics/cpg-flow/commit/d3fed1b7266693a0ff6c2ae7d5b89681f4b77dd2))

- **update-badges.yaml**: Fix push bug -m flag
  ([`ce05b2b`](https://github.com/populationgenomics/cpg-flow/commit/ce05b2b1d2e4d386196112e2525a8e3a7b0a9cd5))

- **update-badges.yaml**: Rm final push
  ([`a782609`](https://github.com/populationgenomics/cpg-flow/commit/a7826099c1ff877e8d4becbf1000f30645e27eaa))

- **update-badges.yaml,docs/badges.yaml**: Fix missing data for badges
  ([`21d4e0b`](https://github.com/populationgenomics/cpg-flow/commit/21d4e0be10101d7a6717d568e1630f0c5641eddd))

- **update-badges.yaml,docs/badges.yaml**: Rm trailing whitespace
  ([`2e547c0`](https://github.com/populationgenomics/cpg-flow/commit/2e547c0903197169527c58d8cc09ea12f389c771))

- **update-badges.yaml,docs/badges.yaml**: Success if no changes to branch
  ([`8122669`](https://github.com/populationgenomics/cpg-flow/commit/812266941988f5a556352d9bfaa27a46dc73dbaf))

### Documentation

- **./,docs/**: Fix readme links
  ([`c4cda73`](https://github.com/populationgenomics/cpg-flow/commit/c4cda73d75ecb4489865c495ebda79fb9633d694))

- **./,docs/**: Update docs and readme urls
  ([`938658e`](https://github.com/populationgenomics/cpg-flow/commit/938658e1bd2ccf71cdfa22c8fe235267be599e16))

- **targets/__init__.py**: Write docs for targets
  ([`bc6c0e8`](https://github.com/populationgenomics/cpg-flow/commit/bc6c0e8c66b815cde55c0f3183cfe5683c2a819c))

### Features

- Migrate prod pipes PR#311
  ([`4663cc2`](https://github.com/populationgenomics/cpg-flow/commit/4663cc20774e7a641dab775f5421976feb9b80ef))

- **src/cpg_flow/workflow.py**: Save graph to web bucket
  ([`9a47711`](https://github.com/populationgenomics/cpg-flow/commit/9a47711541e9a9d3aa89f325ada118da34ae7bb7))

### Refactoring

- **.gitignore**: Add .scannerwork
  ([`649e4ac`](https://github.com/populationgenomics/cpg-flow/commit/649e4ac5f51378bbe039e523553be03c808a3a65))

- **Tests**: Remove seqr.toml as it is not used or required
  ([`5f340b6`](https://github.com/populationgenomics/cpg-flow/commit/5f340b6141d99ce5546db9aef485dbd809e0c9d3))

- **utils.py,workflow.py**: Mv write_to_gcs_bucket to utils
  ([`950ba94`](https://github.com/populationgenomics/cpg-flow/commit/950ba94a2a8ea6c98450feca410683068c7720b0))


## v0.1.0-alpha.14 (2025-01-06)

### Bug Fixes

- **.dummy**: Force release
  ([`15b8906`](https://github.com/populationgenomics/cpg-flow/commit/15b8906cbc07338f3ab730a365e89feeecbc4c7a))

### Build System

- **pyproject.toml,uv.lock**: Update jinja2 to 3.1.5
  ([`4dbdf15`](https://github.com/populationgenomics/cpg-flow/commit/4dbdf15a031ee8cd010efb9884458670bfecdaaf))

- **pyproject.toml,uv.lock**: Upgrade jinja2 as pip-audit logs
  ([`101bff5`](https://github.com/populationgenomics/cpg-flow/commit/101bff5becb27435819059f888dd9536efa5bfd3))

- **uv.lock**: Upgrade jinja2 to 3.1.5
  ([`f833517`](https://github.com/populationgenomics/cpg-flow/commit/f8335170ce585158110283d2ecc2926f065c2ab9))

### Continuous Integration

- **.github/workflows/**: Change run order
  ([`84cfa2c`](https://github.com/populationgenomics/cpg-flow/commit/84cfa2cbee3da9659e9e99075f343a77b8efbb16))

- **package.yaml**: Run after update badges
  ([`de2fa6c`](https://github.com/populationgenomics/cpg-flow/commit/de2fa6c6147676072a8ba583885059d012b996c9))

- **package.yaml**: Run on completion of Test
  ([`d9af0a4`](https://github.com/populationgenomics/cpg-flow/commit/d9af0a42864ffee7716f2907ac0408c57638cb20))

- **package.yaml,web-docs.yaml**: Package on alpha/main only
  ([`4734447`](https://github.com/populationgenomics/cpg-flow/commit/4734447246f6e055c8e2c3264a69ed4a77db2f80))

- **test.yaml,update-badges.yaml**: Add save badge data back to test
  ([`d2aab13`](https://github.com/populationgenomics/cpg-flow/commit/d2aab13f16853a69741d2f05174609c4b2a8558a))

- **update-badges.yaml**: Run after Test
  ([`22819cf`](https://github.com/populationgenomics/cpg-flow/commit/22819cf11266c5d8f407d9e77513109253e756cc))

- **web-docs.yaml**: Run after badge update
  ([`d986ecd`](https://github.com/populationgenomics/cpg-flow/commit/d986ecdd0330c59d2ef1cd8a7c74c169fb462e70))

### Refactoring

- **.dummy**: Add file
  ([`4648964`](https://github.com/populationgenomics/cpg-flow/commit/464896412a0113ae6dc69025eb60e7344ee31aee))


## v0.1.0-alpha.13 (2025-01-05)

### Bug Fixes

- **docs/update_readme.py,pyproject.toml-,+7**: Fix linter warnings
  ([`97acdb8`](https://github.com/populationgenomics/cpg-flow/commit/97acdb8db163e29b31832d0ccc4219cce1dbf8cd))

- **pyproject.toml**: Import coloredlogs
  ([`6a875cf`](https://github.com/populationgenomics/cpg-flow/commit/6a875cf3e82009ee376d1e790b79993f440c927c))

### Build System

- **pyproject.toml,uv.lock**: Add pyyaml
  ([`9171532`](https://github.com/populationgenomics/cpg-flow/commit/9171532d4c239a1c24e674b046ae68c89719f0a7))

### Chores

- Merge alpha
  ([`b009c47`](https://github.com/populationgenomics/cpg-flow/commit/b009c471b2e1e425d0f07de394fc83b86da7649b))

- Update badges.yaml with test results and coverage
  ([`9304439`](https://github.com/populationgenomics/cpg-flow/commit/9304439f6d4d9da58f411917022378e8557b3f0f))

- Update badges.yaml with test results and coverage
  ([`db932a4`](https://github.com/populationgenomics/cpg-flow/commit/db932a461e39596a99cbdc81104a8c36f53008a7))

- Update badges.yaml with test results and coverage
  ([`a750689`](https://github.com/populationgenomics/cpg-flow/commit/a750689bbd61c98bf5a11a6ff0ff137dd3dc3936))

- Update badges.yaml with test results and coverage
  ([`ea440eb`](https://github.com/populationgenomics/cpg-flow/commit/ea440eb37ff244f04be2c5924e15032f5926a53a))

- Update badges.yaml with test results and coverage
  ([`16f13be`](https://github.com/populationgenomics/cpg-flow/commit/16f13be0d764ebd3f48d9b8f842bc3e845434dc6))

- Update badges.yaml with test results and coverage
  ([`eb8be5b`](https://github.com/populationgenomics/cpg-flow/commit/eb8be5bbc01d4b75cfd9b6a193d96d2721464d2b))

- Update badges.yaml with test results and coverage
  ([`d3f6b6b`](https://github.com/populationgenomics/cpg-flow/commit/d3f6b6ba013f29a0ed6b0e371f4223c278bb0a54))

### Continuous Integration

- **.github/workflows/**: Package and web docs after test
  ([`adaa682`](https://github.com/populationgenomics/cpg-flow/commit/adaa682c990e87869e07c97a81d9ea6c2ce235b3))

- **.github/workflows/,docs/**: Mv update-badges from test workflow
  ([`3b90377`](https://github.com/populationgenomics/cpg-flow/commit/3b90377104969a03e2f2dda1127564a294b716a9))

- **.github/workflows/,docs/**: Test workflow upload artifact
  ([`390d162`](https://github.com/populationgenomics/cpg-flow/commit/390d1622ae1e64e4d59c75c2e397616fbddfa07d))

- **package.yaml**: Add step to update alpha on package of main
  ([`4d9eb8a`](https://github.com/populationgenomics/cpg-flow/commit/4d9eb8a06fac89570144504334dec1c85a31f161))

- **test.yaml,update-badges.yaml**: Add to default branch
  ([`20ca3a4`](https://github.com/populationgenomics/cpg-flow/commit/20ca3a47ed28a8fde5228c7a16e54275743fb086))

- **test.yaml,update-badges.yaml**: Back to workflow_run trigger
  ([`a1bed2d`](https://github.com/populationgenomics/cpg-flow/commit/a1bed2d93c02a0a92de3324d873efacef919e780))

- **test.yaml,update-badges.yaml**: Change to using artifacts
  ([`6fea9f6`](https://github.com/populationgenomics/cpg-flow/commit/6fea9f6c7a84582c9ae9888de1f7cd83634fe30d))

- **test.yaml,update-badges.yaml**: Download manually
  ([`1375dd6`](https://github.com/populationgenomics/cpg-flow/commit/1375dd62c06c73dacdccb90477bd2e2f0e00c286))

- **test.yaml,update-badges.yaml**: Merge main
  ([`01d6bd7`](https://github.com/populationgenomics/cpg-flow/commit/01d6bd7e3a0c1ce2b4ea732e36c18c31956517b9))

- **test.yaml,update-badges.yaml**: Retry download-artifact
  ([`471c125`](https://github.com/populationgenomics/cpg-flow/commit/471c12597d4187480962601c1b91f981c6b09e73))

- **update-badges.yaml**: Add manual run
  ([`ca01baf`](https://github.com/populationgenomics/cpg-flow/commit/ca01bafe8f98f3325299ec276b29dd43e347af5a))

- **update-badges.yaml**: Add token
  ([`0bd20ee`](https://github.com/populationgenomics/cpg-flow/commit/0bd20eec5232397e58b892acf192d7a88b6c72e5))

- **update-badges.yaml**: Back to workflow_run
  ([`551bd32`](https://github.com/populationgenomics/cpg-flow/commit/551bd32d4f5aed67951e806f85188afb28ae9f0f))

- **update-badges.yaml**: Checkout the branch so push works
  ([`2393d2a`](https://github.com/populationgenomics/cpg-flow/commit/2393d2a1c805654a2f2a03aed7066261c44606e6))

- **update-badges.yaml**: Checkout the triggering workflow ref
  ([`f1c09c9`](https://github.com/populationgenomics/cpg-flow/commit/f1c09c94cc3b681d0f3a94b5ceb77d9b8d29d5b0))

- **update-badges.yaml**: Custom download artifact
  ([`415a376`](https://github.com/populationgenomics/cpg-flow/commit/415a3762d79cee8cbbe9b373ce7391df584e90bd))

- **update-badges.yaml**: Fix unzip
  ([`653851b`](https://github.com/populationgenomics/cpg-flow/commit/653851b79666e3ae6708ca7bdef03c7a8adea9d6))

- **update-badges.yaml**: List downloaded artifacts
  ([`2240494`](https://github.com/populationgenomics/cpg-flow/commit/2240494135cf38546b9dbd3e7356175f692690b6))

- **update-badges.yaml**: Remove push trigger
  ([`d73a32b`](https://github.com/populationgenomics/cpg-flow/commit/d73a32b1c431af6cd234c81ffbfcd26cde47e40e))

- **update-badges.yaml**: Save env variables to GITHUB_ENV
  ([`3816a41`](https://github.com/populationgenomics/cpg-flow/commit/3816a413035c27d19e9610b6d66a98eaa4809647))

- **update-badges.yaml**: Trigger on push to readme
  ([`4152cdf`](https://github.com/populationgenomics/cpg-flow/commit/4152cdf390922affa1b1756d959327b3eaac67e0))

- **update-badges.yaml**: Try wait-for-test job
  ([`46cf28a`](https://github.com/populationgenomics/cpg-flow/commit/46cf28a718476d23e2ee65a58c30f7a01849b896))

- **update-badges.yaml**: Use env correctly
  ([`e337b5a`](https://github.com/populationgenomics/cpg-flow/commit/e337b5a97b45febdc30a0690e8d441aef7ddd482))

- **update-badges.yaml**: Use env variables
  ([`47bd7fd`](https://github.com/populationgenomics/cpg-flow/commit/47bd7fd4ab4167e32904700af49da93e63155979))

- **update-badges.yaml,docs/badges.yaml**: Custom download artifact
  ([`fb177f2`](https://github.com/populationgenomics/cpg-flow/commit/fb177f2a16e1e10ccdf6c982bd03e9630e107449))

- **web-docs.yaml**: Rename to kebab case
  ([`67b1e94`](https://github.com/populationgenomics/cpg-flow/commit/67b1e9422f3c1b3ea306182598bc5aea88c1d465))

### Documentation

- **docs/alpha/**: Create the docs page
  ([`75e772e`](https://github.com/populationgenomics/cpg-flow/commit/75e772edee1095440008adff8b5d4d9e779ac891))

### Refactoring

- **.dummy**: Dummy commit
  ([`258223b`](https://github.com/populationgenomics/cpg-flow/commit/258223b297fd327ac804c50d316edf518a896b07))

- **.dummy**: Dummy commit
  ([`62038c0`](https://github.com/populationgenomics/cpg-flow/commit/62038c03d17d779852c1fa2644d78f15b28a69af))


## v0.1.0-alpha.12 (2024-12-17)

### Bug Fixes

- **pyproject.toml,src/cpg_flow/inputs.py-,+10**: Use better logger
  ([`057ab0e`](https://github.com/populationgenomics/cpg-flow/commit/057ab0e17bebc0f07797bf695c64a74cdec15c14))

### Chores

- Update badges.yaml with test results and coverage
  ([`792f640`](https://github.com/populationgenomics/cpg-flow/commit/792f64026d064cfb3e9bfac1f91ee32cb7c8239f))

- Update badges.yaml with test results and coverage
  ([`02011fe`](https://github.com/populationgenomics/cpg-flow/commit/02011fe31f8bc3e5662d62057f41615433104c19))

### Continuous Integration

- **./,.github/workflows/,docs/**: Update badge values in test workflow
  ([`0f02c23`](https://github.com/populationgenomics/cpg-flow/commit/0f02c230f521b4901026a64d16383a7ce4fecc6c))

- **test.yaml**: Add git pull
  ([`f9477f6`](https://github.com/populationgenomics/cpg-flow/commit/f9477f62c580f91489acbe33bd3bf0bf4ab0b92e))

- **test.yaml**: Fix coverage color logic
  ([`cd4a722`](https://github.com/populationgenomics/cpg-flow/commit/cd4a722a0950bd107f6d47f0f72488f5a1728d84))

- **test.yaml**: Fix for coverage_color calculation
  ([`a57972f`](https://github.com/populationgenomics/cpg-flow/commit/a57972f4dd151a98eab8ebb2c3bffa4846e78b10))

- **test.yaml**: Fix save badge env step
  ([`2a37f74`](https://github.com/populationgenomics/cpg-flow/commit/2a37f7420d23b4a8ee1a74f0e2a5990b702570d1))

- **test.yaml,README.md**: Create badges
  ([`630911b`](https://github.com/populationgenomics/cpg-flow/commit/630911b933833e26c88919843c636934ae88b64c))

- **web_docs.yaml**: Add web doc deploy
  ([`b81dca5`](https://github.com/populationgenomics/cpg-flow/commit/b81dca5bcd1037876700be9b8015ade223c0e1b0))

- **web_docs.yaml**: Only build docs on alpha and main
  ([`63adf12`](https://github.com/populationgenomics/cpg-flow/commit/63adf12c955419edac30c0cfcc971eb1b2105a51))

- **web_docs.yaml,Makefile**: Rm excessive permissions, fix script name
  ([`febaf9c`](https://github.com/populationgenomics/cpg-flow/commit/febaf9c92e5fc68b6157c791c68476a1880b2c70))

### Documentation

- **./,.github/workflows/**: Script to document all of our workflows
  ([`4ffadab`](https://github.com/populationgenomics/cpg-flow/commit/4ffadab227c2a27ffc3d960cb422d1dd064474c9))

- **./,.github/workflows/,docs/**: Document workflow update
  ([`3eff1de`](https://github.com/populationgenomics/cpg-flow/commit/3eff1deee0534005f2928fa6611de2c7e7fd3aad))

- **./,.github/workflows/,docs/**: Replace badges, fix urls
  ([`97a7977`](https://github.com/populationgenomics/cpg-flow/commit/97a797732e6c86e9a84298b2c3356de323c7e57b))

- **.pre-commit-config.yaml,Makefile,docs/**: Use pydoc to document api
  ([`341f0ff`](https://github.com/populationgenomics/cpg-flow/commit/341f0ff17e4a11b9805dc73a4a0e2bbe9e265d74))

- **CONTRIBUTING.md**: Add notes on commitlint and commitizen
  ([`8609727`](https://github.com/populationgenomics/cpg-flow/commit/8609727be4bfb5bcdd66c404473eeeae7b0c75d2))

- **DEVELOPERS.md,README.md**: Finish readme, rm old dev docs
  ([`a1e4676`](https://github.com/populationgenomics/cpg-flow/commit/a1e46767dc266e3fc811d54620923335ca6cae95))

- **README.md**: Add notes about commitlint and commitizen
  ([`396adc7`](https://github.com/populationgenomics/cpg-flow/commit/396adc742294c37a2ccbca8f318230ed65bf4dc3))

- **README.md**: Clean up
  ([`e22d96d`](https://github.com/populationgenomics/cpg-flow/commit/e22d96d17718b9836b44bf10afc6c4678a956a5b))

- **README.md**: Remove pip as suggestion
  ([`0a34d54`](https://github.com/populationgenomics/cpg-flow/commit/0a34d54d647fdd055f849426e8c0ddd0ac3f81e4))

- **README.md**: Test badge
  ([`50ba1af`](https://github.com/populationgenomics/cpg-flow/commit/50ba1af626264e4aa29a9cd9d167c9d5bab7ba47))

- **web_docs.yaml,Makefile-,+22**: Generate docs on all branches
  ([`991cf57`](https://github.com/populationgenomics/cpg-flow/commit/991cf5783d7d35dee56a7ab0452d54e69c695c4e))


## v0.1.0-alpha.11 (2024-12-13)

### Bug Fixes

- **src/cpg_flow/targets/**: Improve hashing efficiency
  ([`b3715e8`](https://github.com/populationgenomics/cpg-flow/commit/b3715e8b68d2fb58a3922730f845cd34e2325b68))

- **target.py**: Add fix for alignment has to target
  ([`8e7b6a9`](https://github.com/populationgenomics/cpg-flow/commit/8e7b6a9268b3f09bd37d808f7720591305c24225))


## v0.1.0-alpha.10 (2024-12-13)

### Bug Fixes

- **src/cpg_flow/**: Add passing cohort ids to create analysis
  ([`d2fa675`](https://github.com/populationgenomics/cpg-flow/commit/d2fa67559f74e6e7ae1108611e3df5cd838179be))

- **src/cpg_flow/,src/cpg_flow/targets/**: Add missing methods
  ([`22edaf2`](https://github.com/populationgenomics/cpg-flow/commit/22edaf2d1f07a3a456e16faa4dfd11b22f530d4c))

- **src/cpg_flow/metamist.py**: Create_analysis make id lists optional
  ([`b3ef85c`](https://github.com/populationgenomics/cpg-flow/commit/b3ef85cc9c14a8acf7e84227d931e76399b7110b))

- **src/cpg_flow/status.py**: Cohort has no method .target_id
  ([`f5f2264`](https://github.com/populationgenomics/cpg-flow/commit/f5f22648d1996043521860075573d25f4804e261))


## v0.1.0-alpha.9 (2024-12-10)

### Bug Fixes

- **.dummy**: Force release of alpha
  ([`41dfb46`](https://github.com/populationgenomics/cpg-flow/commit/41dfb460d30c386ea82e6cb06cfebd2a982c1d5f))

### Build System

- **.dockerignore,-Dockerfile,-tests/hail/config.toml**: Improve uv setup in docker
  ([`652cbee`](https://github.com/populationgenomics/cpg-flow/commit/652cbeeb1cc0510b7110614b8cbfb04a719f8e36))

- **Dockerfile**: Activate venv in dockerfile
  ([`b086e9b`](https://github.com/populationgenomics/cpg-flow/commit/b086e9b54674ee378602249a0b7a0e86a4c56e01))

- **Dockerfile**: Add explicit copying of deps files
  ([`693b3da`](https://github.com/populationgenomics/cpg-flow/commit/693b3daa4a11b68bc72a8ded3a7c550287442dda))

- **Dockerfile**: Adding source shell to Docker stage
  ([`4aa8e1f`](https://github.com/populationgenomics/cpg-flow/commit/4aa8e1f5cf0fba99dd0998c10a8bb01b04794297))

- **Dockerfile**: Fix typo in path
  ([`d181a83`](https://github.com/populationgenomics/cpg-flow/commit/d181a83b2ffdfb001f233b2852f601231b1a46e0))

- **Dockerfile**: Switch to uv and fix dir copy
  ([`b2db11d`](https://github.com/populationgenomics/cpg-flow/commit/b2db11d087e0a370bb4445fb8c8aa1de4d78048d))

- **Dockerfile**: Test running uv from local bin
  ([`11b3477`](https://github.com/populationgenomics/cpg-flow/commit/11b3477af856bec94d2a50b5f06c85dff8f02dcf))

- **Dockerfile**: Test using uv docker img
  ([`6f2ec8f`](https://github.com/populationgenomics/cpg-flow/commit/6f2ec8fd4c34864fc35220e7a1660e7afa04473e))

- **Dockerfile**: Use uv sync to install reqs
  ([`2ff5933`](https://github.com/populationgenomics/cpg-flow/commit/2ff59333f1b97132f17510e8a0f5d426189aa75a))

- **Dockerfile**: Uv sync after copying dir contents
  ([`2bb9dc8`](https://github.com/populationgenomics/cpg-flow/commit/2bb9dc8430602a92e258c4b64f14ec3c2d024c4e))

- **Dockerfile,-tests/hail/workflow.py**: Force install of dev deps
  ([`10beaea`](https://github.com/populationgenomics/cpg-flow/commit/10beaeae82dbc461bce7c10f314c545716bc5622))

- **pyproject.toml,uv.lock**: Add networkx to core deps
  ([`e6a0826`](https://github.com/populationgenomics/cpg-flow/commit/e6a08265a18da34df9eb93a4db0b0ffd3ce24e8e))

- **uv.lock**: Bumped tornado dep
  ([`58a713f`](https://github.com/populationgenomics/cpg-flow/commit/58a713f25b3c4f6f7cd7be7ad59df2a1681e3029))

- **uv.lock,pyproject.toml**: Bumped grpcio dep
  ([`256552f`](https://github.com/populationgenomics/cpg-flow/commit/256552f31d32788a4bbcf1bab5b9392d3a9e37a6))

- **uv.lock,pyproject.toml,.github/workflows/security.yaml**: Bumped deps, improved security
  workflow
  ([`52449a8`](https://github.com/populationgenomics/cpg-flow/commit/52449a8cb05a5601fc859e19894e609e49902d6a))

### Code Style

- **.dummy**: Rm file
  ([`087f7d9`](https://github.com/populationgenomics/cpg-flow/commit/087f7d9f84b0c2c268a2af722ceee57fc6999cb3))

### Continuous Integration

- **.dummy**: Trigger commit docker build
  ([`d1e84bc`](https://github.com/populationgenomics/cpg-flow/commit/d1e84bcc2caaf4ec7eb54088f06793bc24826d66))

- **.github/workflows/,tests/hail/**: Fix tests script again
  ([`03dd3a6`](https://github.com/populationgenomics/cpg-flow/commit/03dd3a651a849351dfc64927079aaa5ffffebdc1))

- **.github/workflows/docker.yaml**: Added test environment
  ([`eff9cdc`](https://github.com/populationgenomics/cpg-flow/commit/eff9cdc1ecd3a0966c7e7ff4a6e3eee457e36b1f))

- **.github/workflows/renovate.yaml**: Removed input on workflow dispatch
  ([`aad0f9b`](https://github.com/populationgenomics/cpg-flow/commit/aad0f9bd4f3e3c14ca062012d76fc85c2ffe1196))

- **docker.yaml**: Add push commit sha step
  ([`3d13938`](https://github.com/populationgenomics/cpg-flow/commit/3d1393817db9df8f01bd46219405975576fcaf7f))

- **docker.yaml**: Change to $GITHUB_SHA
  ([`7d582c0`](https://github.com/populationgenomics/cpg-flow/commit/7d582c0c59f077565d70e577432afa93e08951ad))

- **docker.yaml**: Echo sha
  ([`01f64d1`](https://github.com/populationgenomics/cpg-flow/commit/01f64d1e2052abeda3219d8d2de6c87cad6da4e2))

- **docker.yaml**: Fix build github sha
  ([`5cf3a7a`](https://github.com/populationgenomics/cpg-flow/commit/5cf3a7a7943e91aeed244396a384bcfff329cfad))

- **docker.yaml**: Fix push to images-tmp sha
  ([`df24a1e`](https://github.com/populationgenomics/cpg-flow/commit/df24a1e2141229becbe4f3a6a34ed2c8cc2c0e0f))

- **docker.yaml**: Push commit images to images-tmp
  ([`743a533`](https://github.com/populationgenomics/cpg-flow/commit/743a533fb28f7b8b657748b8184c01489e0b94d2))

- **docker.yaml,pyproject.toml**: Get sem ver to update docker version
  ([`b0279b0`](https://github.com/populationgenomics/cpg-flow/commit/b0279b0cee7517ecbe5d66879f975d60b10457bb))

- **hail.yaml**: Rm uneeded workflow
  ([`54ac1a9`](https://github.com/populationgenomics/cpg-flow/commit/54ac1a99731b3f2f7312086d66645eca1105329b))

- **manual-test.yaml**: Add a manual check for running workflow test
  ([`9a809cc`](https://github.com/populationgenomics/cpg-flow/commit/9a809ccc79188d412313239e5dc38ac737d27689))

- **manual-test.yaml**: Change to echo
  ([`0157daf`](https://github.com/populationgenomics/cpg-flow/commit/0157daf1b6b856931aa9d2abcf06207d042f9364))

### Refactoring

- **.dummy**: Add dummy file
  ([`6317611`](https://github.com/populationgenomics/cpg-flow/commit/63176114962beefc3277701437e97eec57330dae))

- **tests/hail/**: Move to test_workflows_shared repo
  ([`c146832`](https://github.com/populationgenomics/cpg-flow/commit/c1468327bb71507d4ac89862266d307c4374515f))

### Testing

- **./,tests/hail/**: Make tests importable
  ([`7af791d`](https://github.com/populationgenomics/cpg-flow/commit/7af791dd249f29cce38b85abe7b2adac154265c0))

- **.github/workflows/,tests/hail/**: Adding more to workflow test
  ([`eea12e7`](https://github.com/populationgenomics/cpg-flow/commit/eea12e7cd5e5c222f60056642b19d9868b430ac4))

- **Dockerfile**: Add PYTHONPATH to Dockerfile
  ([`fddd50e`](https://github.com/populationgenomics/cpg-flow/commit/fddd50ef32f934e89f2ea4f43be85fe527c11004))

- **tests/hail/**: Start writing cpg-flow workflow test
  ([`930790a`](https://github.com/populationgenomics/cpg-flow/commit/930790a89d9d0720c7def8eb2e4784ea17db1641))

- **tests/hail/***: Fix linting, missing image arg to analysis-runner
  ([`7350986`](https://github.com/populationgenomics/cpg-flow/commit/735098694f1a2a1bc2be07aab38ff1ee9263637b))

- **tests/hail/*.py**: Added logging
  ([`03daed8`](https://github.com/populationgenomics/cpg-flow/commit/03daed807827c59aa30d9fba8e1f82bf30c31adf))

- **tests/hail/*.py**: Fix path reference for expected_outputs
  ([`31a14eb`](https://github.com/populationgenomics/cpg-flow/commit/31a14eba8b4c573847c0f7a8e2de19c5b35fd742))

- **tests/hail/*.py,-Dockerfile**: Add explicit imports from src
  ([`ed0ddf3`](https://github.com/populationgenomics/cpg-flow/commit/ed0ddf3d8eb790d78575570d560b2b23e0662df0))

- **tests/hail/config.toml**: Added access_level and sequencing_type vars
  ([`5ec3812`](https://github.com/populationgenomics/cpg-flow/commit/5ec38124307e16a451989f141ac0a3c3e9e9bef0))

- **tests/hail/config.toml**: Remove local backend setting
  ([`9fdc5af`](https://github.com/populationgenomics/cpg-flow/commit/9fdc5af7adf1ed0759ecba051e718afba1c0cb2b))

- **tests/hail/config.toml,tests/hail/run-test.sh**: Add warnings
  ([`12fa5bd`](https://github.com/populationgenomics/cpg-flow/commit/12fa5bd351a8f8344fc4f697c8bc71f328f48a25))

- **tests/hail/config.toml,tests/hail/stages.py**: Fix?
  ([`e113af2`](https://github.com/populationgenomics/cpg-flow/commit/e113af2f2bfef49260da7e44765b3a81bc95d47f))

- **tests/hail/run-test.sh**: Check commit has pushed
  ([`191f4ca`](https://github.com/populationgenomics/cpg-flow/commit/191f4cacf8c96452442b4721c00c55239ad4e58b))

- **tests/hail/run-test.sh**: Check the image exists
  ([`8ea7013`](https://github.com/populationgenomics/cpg-flow/commit/8ea7013d35ef62ef10b32219bc24107fc93cec5e))

- **tests/hail/run-test.sh**: Fix our script
  ([`3b9e782`](https://github.com/populationgenomics/cpg-flow/commit/3b9e78257cdaeed274b7469d927902b3e2af208d))

- **tests/hail/run-test.sh**: Write better wait for docker loop
  ([`91a55ea`](https://github.com/populationgenomics/cpg-flow/commit/91a55ea459889b359f30e0e278e1f7f85f9dfe50))

- **tests/hail/stage.py**: More testing
  ([`c044488`](https://github.com/populationgenomics/cpg-flow/commit/c044488333ed18f711e2c130273661585f1ada11))

- **tests/hail/stages.py**: Fix?
  ([`765f65e`](https://github.com/populationgenomics/cpg-flow/commit/765f65ee83791b8e40c68165128ab156c1d96b04))

- **tests/hail/stages.py**: Remove use of read_input for cumulative_calc
  ([`ada778e`](https://github.com/populationgenomics/cpg-flow/commit/ada778e85b629ab6ec679a34cbd4ec05941555e9))

- **tests/hail/stages.py**: Removed single quote bug
  ([`30947c1`](https://github.com/populationgenomics/cpg-flow/commit/30947c178e67eb13e33dfe957d3c599e4e231dd0))

- **tests/hail/stages.py**: Testing cumulative calc
  ([`af682c9`](https://github.com/populationgenomics/cpg-flow/commit/af682c9fcf2dd5fa0da95bb2be8d99e3e73da708))

- **tests/hail/stages.py**: Testing python jobs in stages
  ([`374c383`](https://github.com/populationgenomics/cpg-flow/commit/374c38397698204f84a6c53c474b2feb42206d99))

- **tests/hail/stages.py**: Testing python jobs within stages
  ([`5eeaa84`](https://github.com/populationgenomics/cpg-flow/commit/5eeaa84b38652c8a70ba24bb9b989fe257546883))

- **tests/hail/stages.py**: Trying print dump in a python job
  ([`26a69d9`](https://github.com/populationgenomics/cpg-flow/commit/26a69d9fe6f46b33db81a5082398235f61bbb613))

- **tests/hail/stages.py,tests/hail/workflow.py**: Complete workflow
  ([`2f63d3d`](https://github.com/populationgenomics/cpg-flow/commit/2f63d3d0d08ffed5eb5b3b58f5d44e0fb3135464))

- **tests/hail/stages.py,tests/hail/workflow.py,Dockerfile**: Fixed some bugs, and refactored
  dockerfile for more accurate paths
  ([`41d86e6`](https://github.com/populationgenomics/cpg-flow/commit/41d86e62639b1752397e8f4eff220023a8ce55c3))

- **tests/hail/workflow.py**: Add import to run_cpg_flow
  ([`a48b8dc`](https://github.com/populationgenomics/cpg-flow/commit/a48b8dcedd7dda713fce5977e0f9f73de54c4a58))

- **tests/hail/workflow.py**: Better logging for config
  ([`b67dab4`](https://github.com/populationgenomics/cpg-flow/commit/b67dab4e0bec1df6b63606bd2294b6a91c7b492a))

- **tests/hail/workflow.py**: Change shebang venv path
  ([`96c31b9`](https://github.com/populationgenomics/cpg-flow/commit/96c31b972c7390dd29b19ad02a54f5edfbbceb41))

- **tests/hail/workflow.py**: Fixed config compilation
  ([`20d56ce`](https://github.com/populationgenomics/cpg-flow/commit/20d56ceb528e2dc6652db27a13ed794943f443d7))

- **tests/hail/workflow.py**: Revert stages import
  ([`d998be7`](https://github.com/populationgenomics/cpg-flow/commit/d998be748d36f5ffd6eb6aa83a09877ba483020b))

- **tests/hail/workflow.py**: Standardise shebang
  ([`b405406`](https://github.com/populationgenomics/cpg-flow/commit/b4054060698dbb523165be9213227db7471079c8))

- **tests/hail/workflow.py**: Switch back shebang
  ([`71de065`](https://github.com/populationgenomics/cpg-flow/commit/71de0655a96362188184b32bdc2c251d8dcbc85b))

- **tests/hail/workflow.py**: Temp removal of last 2 stages
  ([`c3d607d`](https://github.com/populationgenomics/cpg-flow/commit/c3d607d14793977345c97b63dbcbac54b6876fd5))


## v0.1.0-alpha.8 (2024-11-15)

### Bug Fixes

- **package.yaml**: Add verbose logging
  ([`6fca5fb`](https://github.com/populationgenomics/cpg-flow/commit/6fca5fb4688840f38322db90eafb8183b9f5b835))

- **package.yaml**: Deploy key to exempt action from br protection rules
  ([`5683a10`](https://github.com/populationgenomics/cpg-flow/commit/5683a10b95daa9a772360d75912572cac8dc9c9e))

- **package.yaml**: Fix setup step add git clone
  ([`21c1400`](https://github.com/populationgenomics/cpg-flow/commit/21c1400a6083df40dffa66b9a642bf3f7d8892f4))

- **package.yaml**: Push to pypi not testpypi
  ([`3a59082`](https://github.com/populationgenomics/cpg-flow/commit/3a59082568d6cf2d4394714020c6eb7101ea8ba3))

- **package.yaml**: Remove redundant checkout step
  ([`0634f44`](https://github.com/populationgenomics/cpg-flow/commit/0634f445361bf050d6243d142411c8738601c9e7))

- **package.yaml**: Use bot token
  ([`99814f6`](https://github.com/populationgenomics/cpg-flow/commit/99814f61d5f91bed00c49bf954da4c13b247a574))

- **package.yaml**: Use github token in setup step
  ([`8601d62`](https://github.com/populationgenomics/cpg-flow/commit/8601d62983cdac7b6a70429ac1d1c1c0aa4cf0f2))

- **package.yaml,pyproject.toml**: Add ignore token for push
  ([`517d522`](https://github.com/populationgenomics/cpg-flow/commit/517d522fdfad4c4042f0dd4a472655ff0697c4b9))

- **pyproject.toml,uv.lock**: Rm unused dev
  ([`26c9361`](https://github.com/populationgenomics/cpg-flow/commit/26c93615ed4a53ca8c239f57d98b99666dcaf6c6))

### Chores

- Merge pull request #15 from populationgenomics/pypi-deploy
  ([`20b4886`](https://github.com/populationgenomics/cpg-flow/commit/20b48861685b2927186f69fa6338cec4eeb5f1c3))

fix(package.yaml): deploy key to exempt action from br protection rules

- Merge pull request #16 from populationgenomics/pypi-deploy
  ([`13a9f7d`](https://github.com/populationgenomics/cpg-flow/commit/13a9f7d737e1a73b86cca0c62c7c6c5c8aadf91a))

Pypi deploy

### Refactoring

- **.dummy**: Remove file, check token permissions
  ([`a5a36df`](https://github.com/populationgenomics/cpg-flow/commit/a5a36df0760595a421f606dae431ebfd770aa37f))

- **.dummy**: Test push to alpha using BOT_ACCESS_TOKEN
  ([`8284ac1`](https://github.com/populationgenomics/cpg-flow/commit/8284ac14890432ba0182aec0f2fb1feb2f41f278))

- **.dummy**: Test token
  ([`fc48eb5`](https://github.com/populationgenomics/cpg-flow/commit/fc48eb52dcd4bc8a409cf229b7a9c2ed10288939))

- **.dummy**: Test token
  ([`ec00646`](https://github.com/populationgenomics/cpg-flow/commit/ec006467788e26482fd06c639c649c38feaae597))


## v0.1.0-alpha.7 (2024-11-12)

### Bug Fixes

- **./,.github/workflows/**: Get package.yaml working
  ([`c1992f7`](https://github.com/populationgenomics/cpg-flow/commit/c1992f7595684e0c6ae4852358ae09526e557fe0))


## v0.1.0-alpha.6 (2024-11-12)

### Bug Fixes

- **./,.github/workflows/**: Fix package.yaml build command
  ([`e41138c`](https://github.com/populationgenomics/cpg-flow/commit/e41138c72fcf14bda795756f0c584f429cae37fd))

- **.dummy,package.yaml**: Trigger release, use venv in workflow
  ([`36a4057`](https://github.com/populationgenomics/cpg-flow/commit/36a405714c1eea6684c6308f001a7bbeddae0b31))

- **Makefile,pyproject.toml**: Debug ci-build command
  ([`cdf2fcf`](https://github.com/populationgenomics/cpg-flow/commit/cdf2fcfe567ec0de7d7dc8fa3109cc6b28b744ad))

- **Makefile,pyproject.toml**: Update build system
  ([`759ef2d`](https://github.com/populationgenomics/cpg-flow/commit/759ef2dcacee15050d49fe006ff3f4815375f1b3))

- **package.yaml**: Add git auth
  ([`601669c`](https://github.com/populationgenomics/cpg-flow/commit/601669cbe7363dd56636d5ba96c345854e72e557))

- **package.yaml**: Fix package.yaml manual semantic command
  ([`f733c90`](https://github.com/populationgenomics/cpg-flow/commit/f733c90b050a012515284dc985d116b972744c71))

- **package.yaml,.pypirc**: Run semantic release manually
  ([`f872765`](https://github.com/populationgenomics/cpg-flow/commit/f8727656dd072635f87dde02f9b835cd9083c61b))

- **package.yaml,pyproject.toml**: Rm uv, base build with version fix
  ([`559d16b`](https://github.com/populationgenomics/cpg-flow/commit/559d16b10797927caee58cd1bf4245269271eac7))

- **pyproject.toml**: Fix build command
  ([`37c43ec`](https://github.com/populationgenomics/cpg-flow/commit/37c43ec53d87948dc7db984d51d58dba92b1fafa))


## v0.1.0-alpha.5 (2024-11-12)

### Bug Fixes

- **.dummy**: Fix forces a release
  ([`6e34931`](https://github.com/populationgenomics/cpg-flow/commit/6e349310bf2b470952bcedcce28b47ae01cb8d8d))

### Build System

- **pyproject.toml**: Fix project version
  ([`ddac37c`](https://github.com/populationgenomics/cpg-flow/commit/ddac37c3e53afd0a69b1f63abccb2cf239a36ec3))


## v0.1.0-alpha.4 (2024-11-12)

### Bug Fixes

- **pyproject.toml**: Remove dynamic version
  ([`4dcc2b9`](https://github.com/populationgenomics/cpg-flow/commit/4dcc2b9aa219c9a2e3ba041db71f20800c5b17a6))

- **pyproject.toml**: Remove dynamic version
  ([`9beca1f`](https://github.com/populationgenomics/cpg-flow/commit/9beca1fa8d22edf373b998c7e6cddcfb41c5e11a))


## v0.1.0-alpha.3 (2024-11-12)

### Bug Fixes

- **.dummy**: Fix commit to trigger release
  ([`e8a15a1`](https://github.com/populationgenomics/cpg-flow/commit/e8a15a1a2c5eec19c656a1832338ff736208db14))

### Continuous Integration

- **package.yaml**: Add verbose to pypi upload
  ([`a431fa6`](https://github.com/populationgenomics/cpg-flow/commit/a431fa67a09e41a2f2527a128d264dfb007411ba))


## v0.1.0-alpha.2 (2024-11-12)

### Bug Fixes

- **.dummy**: Add dummy file to trigger fix change
  ([`83546d3`](https://github.com/populationgenomics/cpg-flow/commit/83546d3d19108a9f089379e61e6de03b14002f7f))

### Continuous Integration

- **package.yaml**: Add contents write to package workflow
  ([`366efd1`](https://github.com/populationgenomics/cpg-flow/commit/366efd1896d9142beb23c2cb4f59aef4add35bc8))

- **package.yaml**: Upload to testpypi and fix gh permissions
  ([`0a253d3`](https://github.com/populationgenomics/cpg-flow/commit/0a253d3499729a788bc047edbe32bc0d3b75bab1))


## v0.1.0-alpha.1 (2024-11-12)

### Bug Fixes

- Rename cpg_workflow to cpg_flow
  ([`b387b3c`](https://github.com/populationgenomics/cpg-flow/commit/b387b3c1ff6d9ac1726b50e52ddca00abc2522e9))

- **pyproject.toml**: Switch back to 3.10 for prod pipes, add deps fix
  ([`1a0e214`](https://github.com/populationgenomics/cpg-flow/commit/1a0e2144901697029f1196cc8bedc9ab7979542e))

- **src/cpg_flow/,tests/,tests/assets/**: Debugging test_cohort.py
  ([`238ab67`](https://github.com/populationgenomics/cpg-flow/commit/238ab67fb36ce771d4efef9898180cab1a7ff026))

- **src/cpg_flow/targets/**: Fix circular import issue
  ([`ca793b1`](https://github.com/populationgenomics/cpg-flow/commit/ca793b1af01d568b3058abfce1b2431c9b7f3c66))

- **test.yaml**: Fix path to tests folder
  ([`199b168`](https://github.com/populationgenomics/cpg-flow/commit/199b1684974159b7afa1b5c6e33decdecaad4505))

- **test.yaml**: Revert to 3.10
  ([`69e4f14`](https://github.com/populationgenomics/cpg-flow/commit/69e4f14d8f9dd1341021ce6ddad1a30542797ef5))

- **tests/,tests/assets/,tests/stages/**: Fix test mocks and files
  ([`aae8755`](https://github.com/populationgenomics/cpg-flow/commit/aae87550ff1b6f410a6b3d193079b3a8b40171c4))

- **tests/stages/__init__.py**: Fix file to prod-pipes #959 version
  ([`91b875e`](https://github.com/populationgenomics/cpg-flow/commit/91b875ebebc9251a8b435ef34996b82bc76b5896))

- **workflow.py**: Fix circular import error
  ([`8de184f`](https://github.com/populationgenomics/cpg-flow/commit/8de184fa88db81aee52ba3c5ebcc7b3f646f2907))

### Build System

- **.github/renovate-config.json**: Removed merge commit msg debris
  ([`3f845a1`](https://github.com/populationgenomics/cpg-flow/commit/3f845a16fb849e3979ece711f1040ffe22f47866))

- **.github/workflows/renovate.yaml**: Attempting to fix the code checkout
  ([`3f326ba`](https://github.com/populationgenomics/cpg-flow/commit/3f326baf904b1226bcc36454e4afefff5ab48903))

- **.github/workflows/renovate.yaml**: Fix how the workflow dispatch call works
  ([`8190250`](https://github.com/populationgenomics/cpg-flow/commit/8190250a39ff05b9b1135ad8f7310722d7848f79))

- **.github/workflows/renovate.yaml**: Fix how the workflow dispatch call works
  ([#11](https://github.com/populationgenomics/cpg-flow/pull/11),
  [`951c3b0`](https://github.com/populationgenomics/cpg-flow/commit/951c3b0a711c2d1f1d4582f7871f7b743f17bb86))

- **Dockerfile**: Added a skeleton Dockerfile
  ([`b2ee7bb`](https://github.com/populationgenomics/cpg-flow/commit/b2ee7bb89c530060b09f94538b4b0f8181c7865b))

- **Makefile**: Create makefile for building and installing dependencies
  ([`b8ab07b`](https://github.com/populationgenomics/cpg-flow/commit/b8ab07bc6133a054bb9ed531fc055fc0f31f3a90))

- **Makefile,README.md**: Update dev instructions and init in Makefile
  ([`ff111d8`](https://github.com/populationgenomics/cpg-flow/commit/ff111d831c4aa3527fe47bc9d38b14988dcabd24))

- **pre-commit**: Add commitlint
  ([`09c6915`](https://github.com/populationgenomics/cpg-flow/commit/09c691512273b6ebd519c83da756f4dd0fffe096))

- **pyproject.toml**: Allow chore tag option
  ([`a85e24b`](https://github.com/populationgenomics/cpg-flow/commit/a85e24b7b8fe1f5034f0b65df8f228b7650b4a23))

- **pyproject.toml**: Bumped hail to 0.2.133
  ([`785adb5`](https://github.com/populationgenomics/cpg-flow/commit/785adb56be57d322afc7b6fc34d867c9d771cb93))

- **pyproject.toml**: Remove unused mypy options
  ([`61147e5`](https://github.com/populationgenomics/cpg-flow/commit/61147e563953eb01c156d70b161a629cc6245092))

- **pyproject.toml**: Setup ruff linting and ruff isort configs, black config
  ([`1c769f8`](https://github.com/populationgenomics/cpg-flow/commit/1c769f8795e76bdd763b6d7a707245758bf421d2))

- **pyproject.toml,uv.lock**: Add commitizen to dev deps, rm old ones
  ([`17cf760`](https://github.com/populationgenomics/cpg-flow/commit/17cf760fe81f70002786af88adee129ca8503db0))

- **pyproject.toml,uv.lock**: Add pytest_mock
  ([`b6de677`](https://github.com/populationgenomics/cpg-flow/commit/b6de67747a16c199836457cbc54e34243a90db14))

- **requirements/***: Potential fix to renovatebot detecting deps
  ([`afaafd3`](https://github.com/populationgenomics/cpg-flow/commit/afaafd3eefd20cff9078fecb88cbbcbc0bb531a6))

- **test.yaml**: Disable test workflow for now
  ([`3574ea2`](https://github.com/populationgenomics/cpg-flow/commit/3574ea2621cd5b23f1214ca0740d9e3cabbea8cc))

### Chores

- Merge main
  ([`0fb19d8`](https://github.com/populationgenomics/cpg-flow/commit/0fb19d8a3b512367c2f0f131244510e271a66006))

- Merge migration-integration into migration-03
  ([`a2054ef`](https://github.com/populationgenomics/cpg-flow/commit/a2054ef04201ce36647f61bd9a5fa47a2c383bb5))

- Merge remote
  ([`10149d5`](https://github.com/populationgenomics/cpg-flow/commit/10149d58a66244a30390065c250c1c083fbb34f8))

### Code Style

- **.pre-commit-config.yaml,-src/***: Better linting, removed black and isort from pre-commit
  ([`4f05eb1`](https://github.com/populationgenomics/cpg-flow/commit/4f05eb1ddafb6c61aa2eac0752eb909ecac2670a))

- **pyproject.toml**: Removed black and isort config, added additional ignore to ruff
  ([`5b550ee`](https://github.com/populationgenomics/cpg-flow/commit/5b550eea3510df7394f8c05d2724953cf94dd100))

- **README**: Fix title links
  ([`54e8031`](https://github.com/populationgenomics/cpg-flow/commit/54e8031cbb82b252a016d5a3a19cf6ab24e85388))

### Continuous Integration

- **./,.github/workflows/**: Fix workflows, pin python version
  ([`a9c91fb`](https://github.com/populationgenomics/cpg-flow/commit/a9c91fb03065686afd9f16f87360f3521e8cf257))

- **.github/renovate-config.json**: Selected alpha as the target branch, and switched to uv
  ([`f434110`](https://github.com/populationgenomics/cpg-flow/commit/f4341108fd87ed287a857b9c487d494e38afe1f5))

- **.github/renovate-config.json**: Use uv to manage deps
  ([`9724557`](https://github.com/populationgenomics/cpg-flow/commit/9724557eca258bb669bb0efdc1551d2700c9a851))

- **.github/workflows/docker.yaml**: Added a docker workflow that builds and pushes a docker image
  ([`4b02ff1`](https://github.com/populationgenomics/cpg-flow/commit/4b02ff11ee2baad93d717ea28bfff940d2482932))

- **.github/workflows/lint.yaml**: Added additional triggers
  ([`e0eb58e`](https://github.com/populationgenomics/cpg-flow/commit/e0eb58e31ce9ef226ee9877b75204ef7f65fa564))

- **.github/workflows/package.yaml**: Changed the package name to cpg_flow
  ([`2e54fb9`](https://github.com/populationgenomics/cpg-flow/commit/2e54fb9f41d69e39016e97afc2e1d605874317af))

- **.github/workflows/renovate.yaml,-uv.lock**: Removed push calls to the workflow
  ([`cbb5004`](https://github.com/populationgenomics/cpg-flow/commit/cbb50049d508b4997333feb909f8c92cd876032f))

- **.github/workflows/security.yaml**: Fixed requirements path
  ([`4a1ae56`](https://github.com/populationgenomics/cpg-flow/commit/4a1ae562dbc4600b717379befc269817d604acec))

- **lint.yaml**: Fix lint.yaml
  ([`55b6df4`](https://github.com/populationgenomics/cpg-flow/commit/55b6df42d0620301dc1c34b065ebc5956f1a3f37))

- **lint.yaml,test.yaml**: Rm on pull_request for test and lint
  ([`0e6a5e6`](https://github.com/populationgenomics/cpg-flow/commit/0e6a5e6484a8a7bf505f5f4e123ef7f1df85c8db))

- **package.yaml**: Add fetch-depth 0
  ([`b1500fe`](https://github.com/populationgenomics/cpg-flow/commit/b1500fef2d13444ba73b924bdb260e4886df648d))

- **package.yaml**: Fix publish action version
  ([`c17bc5e`](https://github.com/populationgenomics/cpg-flow/commit/c17bc5e160177ed132a1dbd69dabfb306c967de1))

- **package.yaml**: Remove dependent steps
  ([`aa42e8f`](https://github.com/populationgenomics/cpg-flow/commit/aa42e8ff7cc30ff60eafa6df1e0253cb0f575a16))

- **package.yaml**: Trigger package on push just for testing
  ([`1de648f`](https://github.com/populationgenomics/cpg-flow/commit/1de648f8244eed2b209d42f8d55f9ade14168347))

- **package.yaml,pyproject.toml**: Modify semantic release build command
  ([`b990638`](https://github.com/populationgenomics/cpg-flow/commit/b9906386085aed7c985332eee4360f468ce99ccf))

- **package.yaml,pyproject.toml**: Setup package.yaml workflow
  ([`89694c2`](https://github.com/populationgenomics/cpg-flow/commit/89694c21df57222d6fd19130c9733e2f02be7ee0))

- **package.yaml,test.yaml-,+6**: Debugging package.yaml
  ([`0cf28cc`](https://github.com/populationgenomics/cpg-flow/commit/0cf28cccf7ae64c75f32f0e8a57c28e2b65ff9c6))

- **security.yaml**: Add pip-audit workflow
  ([`8d6ad9e`](https://github.com/populationgenomics/cpg-flow/commit/8d6ad9ecfe2ac4a130fdc1129b358da71f774569))

PR: #909 from production-pipelines

- **security.yaml**: Fix security.yaml
  ([`70fffb1`](https://github.com/populationgenomics/cpg-flow/commit/70fffb1fd9178b7c1d0b64adb01abe858b4f46af))

- **test.yaml**: Fix test.yaml workflow
  ([`e382488`](https://github.com/populationgenomics/cpg-flow/commit/e38248833c3341182f5293fc31d4f3355a802698))

- **test.yaml,.gitignore-,+7**: Fixing test.yaml
  ([`b5f3bac`](https://github.com/populationgenomics/cpg-flow/commit/b5f3bac958de1c9f200a9ca023bb7a042698de46))

### Documentation

- **DEVELOPERS.md**: Updated dev setup instructions and Python versions
  ([`a4148ea`](https://github.com/populationgenomics/cpg-flow/commit/a4148ead36654538d093c60013de76164fe4cd01))

- **src/cpg_flow/targets/dataset.py**: Added better docs about the file
  ([`bee79ba`](https://github.com/populationgenomics/cpg-flow/commit/bee79bafc1978df0d364e32fe221d9bf87736dd5))

- **tests/README.md**: Move readme from prod pipes
  ([`ecbce2d`](https://github.com/populationgenomics/cpg-flow/commit/ecbce2d8a175b55d9ede8d8d9d427467b910f6a3))

- **tests/README.md**: Remove keep tags
  ([`2835445`](https://github.com/populationgenomics/cpg-flow/commit/283544543ee110d778ccbec6b2da9467d7a9491f))

### Features

- **Makefile,pyproject.toml,workflows**: Upgrad to using uv
  ([`02a946d`](https://github.com/populationgenomics/cpg-flow/commit/02a946dfc6cda94f185423ee00b18268a1720133))

### Refactoring

- **.files,-pyproject.toml,-__init__.py,-README.md**: Added config files and update to readme
  ([`1fd7ae6`](https://github.com/populationgenomics/cpg-flow/commit/1fd7ae69dfafc6a58435723d14a4a452822d5e0a))

- **cpg_flow/defaults.toml**: Migrate the whole file
  ([`8c36fd4`](https://github.com/populationgenomics/cpg-flow/commit/8c36fd4ceae1680d20da7a4c996356c644f48e58))

- **cpg_flow/filetypes.py**: Migrate file, update deps
  ([`1f9406d`](https://github.com/populationgenomics/cpg-flow/commit/1f9406d60c059eb248585ccb3f18c5eaf48b94a8))

- **cpg_flow/status.py**: Migrate the whole file
  ([`771b767`](https://github.com/populationgenomics/cpg-flow/commit/771b767226cd8cd5e3b0333f2e5f4fc14b187c45))

- **cpg_flow/targets/**: Add init file and simplify imports
  ([`89fe513`](https://github.com/populationgenomics/cpg-flow/commit/89fe513a65e504ca51f9d26cc8fdbdc2c959d491))

- **cpg_flow/targets/**: Add targets.py file, split by class
  ([`39db87c`](https://github.com/populationgenomics/cpg-flow/commit/39db87cd3d6d9c77b01fc2bb0d0cb9d5a6972831))

- **cpg_flow/utils.py**: Migrate the whole file
  ([`8345483`](https://github.com/populationgenomics/cpg-flow/commit/8345483a30bcaed20a374b16d479f075f100de79))

- **misc/attach_disk_test.py**: Remove file
  ([`807d886`](https://github.com/populationgenomics/cpg-flow/commit/807d886f99659c163e80e60574072e60df3b25eb))

PR#6: See Matt's comment

- **resources.py**: Migrate file, remove one unused section
  ([`38c3c9e`](https://github.com/populationgenomics/cpg-flow/commit/38c3c9e4e7a616395327e003f96c0b53394073dd))

- **src/cpg_flow**: Fixed imports from targets
  ([`2d8348b`](https://github.com/populationgenomics/cpg-flow/commit/2d8348b7f43b05a78e2f1e521b1a1daa6d271037))

- **src/cpg_flow**: Moved more stages out of the workflow file
  ([`9f67ab4`](https://github.com/populationgenomics/cpg-flow/commit/9f67ab47462932ba3e4f403e2a086ba02ac23918))

- **src/cpg_flow**: Removed some unused code and added better docs
  ([`cb64bf6`](https://github.com/populationgenomics/cpg-flow/commit/cb64bf649861a31eadeb306246b57ff0c3f4aad8))

- **src/cpg_flow/defaults.toml**: Removed unused configs
  ([`fba83dc`](https://github.com/populationgenomics/cpg-flow/commit/fba83dceb9ce7be3339234db7b5da62d82bd748f))

- **src/cpg_flow/inputs.py**: Refactor to remove infinite loop, and cleanup
  ([`06591c5`](https://github.com/populationgenomics/cpg-flow/commit/06591c52e16ca2f9178aa05ec356f9609be76415))

- **src/cpg_flow/inputs.py**: Removed dead code and fixed some method calls
  ([`49e70a3`](https://github.com/populationgenomics/cpg-flow/commit/49e70a3e4e2857e50f07fbc09c4ceb56bb9d9e79))

Migration from production-pipelines

- **src/cpg_flow/metamist.py**: Removed dead code that we no longer needed
  ([`3d54754`](https://github.com/populationgenomics/cpg-flow/commit/3d54754f038ea358c5d6e2bd790114d31f1ebc4a))

Migration from production-pipelines

- **src/cpg_flow/stage.py**: Split the Stage class into its own file
  ([`4dad84e`](https://github.com/populationgenomics/cpg-flow/commit/4dad84e738529bf46a5eb50eb4ddec4b02499100))

Migration from production-pipelines

- **src/cpg_flow/targets**: Switched filenames to snake case and refactored linting
  ([`4345a82`](https://github.com/populationgenomics/cpg-flow/commit/4345a82c826b88cb0ff2e7be159fd6b2ac779c4a))

- **src/cpg_flow/workflow.py**: Removed the Stage class and other related classes from this file
  ([`941272d`](https://github.com/populationgenomics/cpg-flow/commit/941272dd58d4781c6ca85b3d7b1f85cec1125d1b))

- **test/__init__.py**: Move to new tests folder
  ([`74d1f18`](https://github.com/populationgenomics/cpg-flow/commit/74d1f187e01753a6e6718c28f1cd4a81717c0cf7))

- **utils.py**: Move cpg_workflows/batch.py into utils
  ([`28733a5`](https://github.com/populationgenomics/cpg-flow/commit/28733a52e35f1e033cb4b52e1f0a247704fa7f1a))

### Testing

- **cpg_flow/__init__.py,test_status.py**: Add test, fix stage imports
  ([`ec45f3b`](https://github.com/populationgenomics/cpg-flow/commit/ec45f3b18c18c6944827723c2f137253049d5f96))

- **misc/attach_disk_test.py**: Moved from production-pipelines
  ([`38ab29a`](https://github.com/populationgenomics/cpg-flow/commit/38ab29a2bdc3b494f0a4f124f729ff7cc3504ef1))

- **src/cpg_flow/,tests/**: Fix imports, add test first last stage
  ([`0501661`](https://github.com/populationgenomics/cpg-flow/commit/05016612cd9c0fc6f2c63aa4cf498b35bce7195f))

- **src/cpg_flow/,tests/**: Fix tests in cpg flow
  ([`0682555`](https://github.com/populationgenomics/cpg-flow/commit/0682555ba66479d7f1ed0358da726a862a45a7d4))

- **test.yaml,src/cpg_flow/inputs.py-,+4**: Fix cpg-flow tests, try ci
  ([`aadef8b`](https://github.com/populationgenomics/cpg-flow/commit/aadef8b2882f0d8b0b94cb04f4c4d5a1b5def2ce))

- **test/__init__.py**: Moved from production-pipelines
  ([`49ee73b`](https://github.com/populationgenomics/cpg-flow/commit/49ee73b0903c383da51faadd6df10c1ab4230746))

- **test/stages/__init__.py**: Copy over test stages init
  ([`8636c6d`](https://github.com/populationgenomics/cpg-flow/commit/8636c6da5b28c52f959f2c4dd8399af8a82fa6ab))

- **test_first_last_stages.py**: Add test
  ([`9e9870d`](https://github.com/populationgenomics/cpg-flow/commit/9e9870decd8aa7d24d2b2ffce00e0204eb98fb2f))

- **test_force_stages.py**: Add test
  ([`9cc2a54`](https://github.com/populationgenomics/cpg-flow/commit/9cc2a5459c4f55fc8dc5f7995be64d0fb5ba1592))

- **test_last_stages.py**: Add test
  ([`63ebc43`](https://github.com/populationgenomics/cpg-flow/commit/63ebc436ad29cd36403f3c34c017f527c5de67d5))

- **test_metamist.py**: Add test, remove unused import, fix deps
  ([`bf4dbe4`](https://github.com/populationgenomics/cpg-flow/commit/bf4dbe42bac5afc062b6fb67a7e9990ad1cbd206))

- **test_only_stages.py**: Add test
  ([`8fe01dc`](https://github.com/populationgenomics/cpg-flow/commit/8fe01dc3b7edf094b9adabb1c02173f6c81e2b2a))

- **test_skip_stages.py**: Add test
  ([`bc665da`](https://github.com/populationgenomics/cpg-flow/commit/bc665dacc68a0d2446ed37134a6d3077bba59abd))

- **test_skip_stages_fail.py**: Add test
  ([`108b52e`](https://github.com/populationgenomics/cpg-flow/commit/108b52edac54f92374e5b1e537c43eb8507e57d9))

- **test_stage_types.py**: Add test, add helper functions
  ([`ff6eb2c`](https://github.com/populationgenomics/cpg-flow/commit/ff6eb2cd1225c9e6cb3e51ccb2fddb938984be37))

- **tests/,tests/assets/test_cohort/**: Refactor test_cohort.py
  ([`e4dca3f`](https://github.com/populationgenomics/cpg-flow/commit/e4dca3f5a7068b1fa5ea773ec4ed8d0b51588e20))

- **tests/conftest.py**: Add conftest to try to get tests working
  ([`d8e6d64`](https://github.com/populationgenomics/cpg-flow/commit/d8e6d64c1500dcd8f6d9dcb1e902971005676450))

- **tests/test_cohort.py**: Add test, cpg_workflow -> cpg_flow
  ([`e78f1f4`](https://github.com/populationgenomics/cpg-flow/commit/e78f1f427bd1b2aed6769d60ef3a9808682102eb))

- **tests/test_multicohort.py**: Add test, cpg_workflow -> cpg_flow
  ([`b28140d`](https://github.com/populationgenomics/cpg-flow/commit/b28140df021ccf060938b9668da90aa1df258b45))

- **tests/test_workflow.py**: Add test, cpg_workflow -> cpg_flow
  ([`6028ef0`](https://github.com/populationgenomics/cpg-flow/commit/6028ef0861cf7b07f03aab8aaeed00f45bcc6811))
