# Changelog

## 0.1.0-alpha.7 (2025-05-05)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* **api:** api update ([1c4cb2a](https://github.com/sullyai/sullyai-python/commit/1c4cb2a355cbbb18905e963974374de72e72c38e))

## 0.1.0-alpha.6 (2025-04-24)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Bug Fixes

* **pydantic v1:** more robust ModelField.annotation check ([35b7fb9](https://github.com/sullyai/sullyai-python/commit/35b7fb9d7ccf668fd043ef1a9b26e67eaa314ef7))


### Chores

* broadly detect json family of content-type headers ([3477834](https://github.com/sullyai/sullyai-python/commit/34778348143b37d0937dad81c5d5043687cc98df))
* **ci:** add timeout thresholds for CI jobs ([e611549](https://github.com/sullyai/sullyai-python/commit/e6115494293145b19d6c08a26dbdbcd3a60f9c8e))
* **ci:** only use depot for staging repos ([38a5ab4](https://github.com/sullyai/sullyai-python/commit/38a5ab43196d5c4482f5990059e7a48d02f66040))
* **internal:** codegen related update ([3d5c7ea](https://github.com/sullyai/sullyai-python/commit/3d5c7ea34300a1b0fdc5caf1ae1e4acae6e6db7e))
* **internal:** fix list file params ([220314c](https://github.com/sullyai/sullyai-python/commit/220314c7708ccced412a9f3f6b44eca63bfc77b6))
* **internal:** import reformatting ([ee6c5f5](https://github.com/sullyai/sullyai-python/commit/ee6c5f540cfa2d1311c6ae5c422e4e900a420d6d))
* **internal:** refactor retries to not use recursion ([9d3f457](https://github.com/sullyai/sullyai-python/commit/9d3f457ca729d30315f44ea1ed5e1028c8cb5252))
* **internal:** update models test ([6d5f6ee](https://github.com/sullyai/sullyai-python/commit/6d5f6ee09f35343d00b9e45ef6c882fa4bb8395b))

## 0.1.0-alpha.5 (2025-04-17)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** manual updates ([f79216b](https://github.com/sullyai/sullyai-python/commit/f79216bdd6008821b3999786b7981e628b60e443))

## 0.1.0-alpha.4 (2025-04-17)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Bug Fixes

* **client:** send all configured auth headers ([#20](https://github.com/sullyai/sullyai-python/issues/20)) ([dfba406](https://github.com/sullyai/sullyai-python/commit/dfba406bf81aab6de85671f7a43917bcf3f51a3a))
* **perf:** optimize some hot paths ([edfb8c1](https://github.com/sullyai/sullyai-python/commit/edfb8c1a69b0539b4a3a5fe10bea8f9528e579d6))
* **perf:** skip traversing types for NotGiven values ([7c65999](https://github.com/sullyai/sullyai-python/commit/7c65999995d97828971b73c1ec16f40df575af23))


### Chores

* **client:** minor internal fixes ([13c30ec](https://github.com/sullyai/sullyai-python/commit/13c30ec08268481f4185ef550e3f900f26ebe980))
* **internal:** base client updates ([0e838b2](https://github.com/sullyai/sullyai-python/commit/0e838b2193187b81ccf3e937dbe63a8f6595341f))
* **internal:** bump pyright version ([d9a1544](https://github.com/sullyai/sullyai-python/commit/d9a1544a1614f8c720322989e432119e2743ce42))
* **internal:** expand CI branch coverage ([9230e0b](https://github.com/sullyai/sullyai-python/commit/9230e0b69b429ffdaa501dc0631e5ca05c7e4150))
* **internal:** reduce CI branch coverage ([41c7753](https://github.com/sullyai/sullyai-python/commit/41c7753a24ae6cc6f427ab5a45bdf413d4535e05))
* **internal:** slight transform perf improvement ([#22](https://github.com/sullyai/sullyai-python/issues/22)) ([654e7a1](https://github.com/sullyai/sullyai-python/commit/654e7a1f26429787401ee17e42605ecdc96ea152))
* **internal:** update pyright settings ([710964f](https://github.com/sullyai/sullyai-python/commit/710964f01c5dc1acdbe3716737ad5c518a89cdf9))
* slight wording improvement in README ([#24](https://github.com/sullyai/sullyai-python/issues/24)) ([34fdf54](https://github.com/sullyai/sullyai-python/commit/34fdf545225208c6bcbd686f031b1e33cf6bd811))
* **tests:** improve enum examples ([#23](https://github.com/sullyai/sullyai-python/issues/23)) ([e6d8300](https://github.com/sullyai/sullyai-python/commit/e6d8300119ae8f9112f12c1ca59dc30a58fc9a48))


### Documentation

* remove private imports from datetime snippets ([11d21d1](https://github.com/sullyai/sullyai-python/commit/11d21d11679ca613ee3eacbb6ab63beb701992f2))

## 0.1.0-alpha.3 (2025-04-04)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Chores

* fix typos ([#17](https://github.com/sullyai/sullyai-python/issues/17)) ([a9501e3](https://github.com/sullyai/sullyai-python/commit/a9501e3d767d6c51a26e769c9e57f017d97712e9))
* **internal:** remove trailing character ([#19](https://github.com/sullyai/sullyai-python/issues/19)) ([9d2f872](https://github.com/sullyai/sullyai-python/commit/9d2f872f8651d30a26df4344b6864dab592c1558))

## 0.1.0-alpha.2 (2025-03-17)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/sullyai/sullyai-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** manual updates ([#8](https://github.com/sullyai/sullyai-python/issues/8)) ([54f0497](https://github.com/sullyai/sullyai-python/commit/54f04979e0e876fe190fadfe68bb8cecd6237a72))


### Bug Fixes

* **ci:** ensure pip is always available ([#14](https://github.com/sullyai/sullyai-python/issues/14)) ([1ccc95c](https://github.com/sullyai/sullyai-python/commit/1ccc95cf1670b34f962f0b6958f767161d3fdcac))
* **ci:** remove publishing patch ([#15](https://github.com/sullyai/sullyai-python/issues/15)) ([588422e](https://github.com/sullyai/sullyai-python/commit/588422e4b4b9fc1aab561ea746aa7f33e72dbb1f))
* **internal:** fix auth logic with multiple auth methods ([87c827f](https://github.com/sullyai/sullyai-python/commit/87c827f116450eeb00d8403e63ebabcd9480aa84))
* **types:** handle more discriminated union shapes ([#13](https://github.com/sullyai/sullyai-python/issues/13)) ([600f99e](https://github.com/sullyai/sullyai-python/commit/600f99e19f925090e1c84a84b5924dbf042949a5))


### Chores

* **internal:** bump rye to 0.44.0 ([#12](https://github.com/sullyai/sullyai-python/issues/12)) ([c42f1af](https://github.com/sullyai/sullyai-python/commit/c42f1afce0777f34dcbafb05945f36f1a3c147b3))
* **internal:** codegen related update ([#11](https://github.com/sullyai/sullyai-python/issues/11)) ([a375b35](https://github.com/sullyai/sullyai-python/commit/a375b35378ff93d9fad2c10b15f4f95c82931f2e))
* **internal:** remove extra empty newlines ([#10](https://github.com/sullyai/sullyai-python/issues/10)) ([75b5335](https://github.com/sullyai/sullyai-python/commit/75b5335faab4995df79c5a210d7a6cb7dc0565c1))

## 0.1.0-alpha.1 (2025-03-11)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/sullyai/sullyai-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** api update ([#4](https://github.com/sullyai/sullyai-python/issues/4)) ([c17774d](https://github.com/sullyai/sullyai-python/commit/c17774da22f1390cf4abb6545b54d46c65565da8))
* **api:** api update ([#6](https://github.com/sullyai/sullyai-python/issues/6)) ([b1b23b0](https://github.com/sullyai/sullyai-python/commit/b1b23b061e778fa80846e7c2fb400c72c14f1b67))
* **api:** manual updates ([#5](https://github.com/sullyai/sullyai-python/issues/5)) ([1f43b70](https://github.com/sullyai/sullyai-python/commit/1f43b70f4900c587c41cf6baa2da5d77ae519062))


### Chores

* go live ([#1](https://github.com/sullyai/sullyai-python/issues/1)) ([0b58e83](https://github.com/sullyai/sullyai-python/commit/0b58e833a7d5d818b0f21d6c206c476affdb0056))
* update SDK settings ([#3](https://github.com/sullyai/sullyai-python/issues/3)) ([fbd61f1](https://github.com/sullyai/sullyai-python/commit/fbd61f12cb82075dab7772cf44e09b408c0b5ead))
