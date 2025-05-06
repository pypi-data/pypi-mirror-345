# CHANGELOG


## v2.8.0-rc.2 (2025-05-05)

### Bug Fixes

- Add psutil as dependency
  ([`23cf77e`](https://github.com/crypticorn-ai/api-client/commit/23cf77ea002a2d6f8e31cd858a2dcc1890b8d8c1))

- Centralize cors middleware
  ([`e5aa2d6`](https://github.com/crypticorn-ai/api-client/commit/e5aa2d60254076848530a6d5b9a349058ee45ac7))

- Run logging configuration in init of the library
  ([`8b725e1`](https://github.com/crypticorn-ai/api-client/commit/8b725e18154d184c8593b8de086b0a789b6e180c))

### Features

- Provide lifespan event for fastapi apps to configure logging on startup
  ([`9a2e1c4`](https://github.com/crypticorn-ai/api-client/commit/9a2e1c45d87ad1581c0e1646689eba6ca0876564))


## v2.8.0-rc.1 (2025-05-04)

### Features

- Add router with admin endpoints
  ([`0d38178`](https://github.com/crypticorn-ai/api-client/commit/0d381784f91cab776ca1ee3b8407433dae4421c3))

- Configure formatted logging
  ([`f8c35e9`](https://github.com/crypticorn-ai/api-client/commit/f8c35e900bcf4a279cc8e046e58935ec5c5c62ee))


## v2.7.5 (2025-05-04)

### Bug Fixes

- Log errors and exceptions
  ([`578d6d3`](https://github.com/crypticorn-ai/api-client/commit/578d6d3176e07a7d4cb87e79617d67ab2e1d62de))

### Build System

- Include changelog in build
  ([`a78acb7`](https://github.com/crypticorn-ai/api-client/commit/a78acb7a18a957cfefa8e64ce593b13ddcd4fae7))


## v2.7.4 (2025-05-04)

### Bug Fixes

- Include cli templates in build
  ([`8d46b4c`](https://github.com/crypticorn-ai/api-client/commit/8d46b4c6bc6bd413a86d1661a4ae9647ed66755c))

### Documentation

- Update README and add license
  ([`1876008`](https://github.com/crypticorn-ai/api-client/commit/187600869b9248aef2b66e881711ddfb96a01538))


## v2.7.3 (2025-05-03)

### Bug Fixes

- Fixes attribute bug in http exception handling
  ([`a90b593`](https://github.com/crypticorn-ai/api-client/commit/a90b593bfa3e08a1703a7e2e1fc8a7bb8ac456e3))


## v2.7.2 (2025-05-03)

### Bug Fixes

- Add write:pay:now to default scopes
  ([`8375248`](https://github.com/crypticorn-ai/api-client/commit/83752484e3570a1f39eacda4223100d7f3fbadd0))


## v2.7.1 (2025-05-02)

### Bug Fixes

- Use pydantic instead of json response in api wrappers
  ([`ddd623b`](https://github.com/crypticorn-ai/api-client/commit/ddd623b28cb542ae6dd1bab02044c682cac206af))


## v2.7.0 (2025-05-01)

### Features

- Add download functionality for hive download data endpoint
  ([`ee09d17`](https://github.com/crypticorn-ai/api-client/commit/ee09d177a28f3879e549eb3044c24b5e6197a528))


## v2.6.0 (2025-04-30)

### Features

- Add admin flag on auth verify response and user by username endpoint
  ([`3f27fba`](https://github.com/crypticorn-ai/api-client/commit/3f27fba655e15a42a947ad1c67bcf4319c3daed6))

- Add common pagination query parameters
  ([`4157137`](https://github.com/crypticorn-ai/api-client/commit/415713725541bb4a180f11de12fea2c3071c5f55))

- Add common webscoket error handling
  ([`334a450`](https://github.com/crypticorn-ai/api-client/commit/334a45054797616fdd8bb917381e189bb64e4678))

### Testing

- Add api key generation and remove duplicate tests
  ([`d60a890`](https://github.com/crypticorn-ai/api-client/commit/d60a89071fe7bc25025fbdf2298cb560d9fbdfb8))


## v2.5.3 (2025-04-29)

### Bug Fixes

- Use ExceptionContent in throw utilities
  ([`b38ebf1`](https://github.com/crypticorn-ai/api-client/commit/b38ebf1443d1df126f7e1014b5c25f1e17f56fdc))


## v2.5.2 (2025-04-29)

### Bug Fixes

- Only allow type ApiError in throw utility functions
  ([`7604342`](https://github.com/crypticorn-ai/api-client/commit/7604342baa6dd2bee816ae446dfcc08edb298ddb))

### Build System

- Clean generated code before regenerating
  ([`b563024`](https://github.com/crypticorn-ai/api-client/commit/b56302497e79e2a64e7403d15a0f3d3bd3233b63))


## v2.5.1 (2025-04-27)

### Bug Fixes

- Integrate exception handling in auth handler
  ([`b7835ef`](https://github.com/crypticorn-ai/api-client/commit/b7835efef54adbd021ecce27c002c5e5501cb99c))

### Build System

- Exclude shared classes and enums from openapi to reduce duplication upon client generation
  ([`1987864`](https://github.com/crypticorn-ai/api-client/commit/1987864392397d7ee74ddb9ecbfb61c6d83134dc))

### Continuous Integration

- Run codecov workflow on push and pull request
  ([`cf2bc16`](https://github.com/crypticorn-ai/api-client/commit/cf2bc165d04b855839812ea626a3647b17a91458))

### Refactoring

- Improve sub package registration in ApiClient to reduce redundance
  ([`bdea044`](https://github.com/crypticorn-ai/api-client/commit/bdea044a6bc5180daed59b9a504866d2f519ae05))

- Integrate custom exception handling in auth handler
  ([`3f997e2`](https://github.com/crypticorn-ai/api-client/commit/3f997e23c1493296deaab23063b709d08702d5af))

### Testing

- Add jwt generation function
  ([`c2bc90f`](https://github.com/crypticorn-ai/api-client/commit/c2bc90fb878656642787755330a99c6b9056f14c))

- Update exception assertions with latest changes auth handler
  ([`4c220e5`](https://github.com/crypticorn-ai/api-client/commit/4c220e5bd31d1a7fd64d0f302044acfd4d4927e9))


## v2.5.0 (2025-04-26)


## v2.5.0-rc.5 (2025-04-26)

### Features

- Add details field to `ExceptionContent` to support additional details about the error
  ([`3ae6bc5`](https://github.com/crypticorn-ai/api-client/commit/3ae6bc57ae4e1e8a23c46511cdc5bf9c1eadc40d))

### Refactoring

- Rename exception class names
  ([`7f50e11`](https://github.com/crypticorn-ai/api-client/commit/7f50e114ceee596dcf3e25d3decfe78c849ad22e))


## v2.5.0-rc.4 (2025-04-26)

### Bug Fixes

- Remove wrong media type from `exception_response`
  ([`34920f0`](https://github.com/crypticorn-ai/api-client/commit/34920f0a51eded25e64324654d711e8716ee707c))


## v2.5.0-rc.3 (2025-04-26)

### Bug Fixes

- Fixes TypeError bug in deprecated decorator
  ([`4344581`](https://github.com/crypticorn-ai/api-client/commit/4344581f2737377334d2ab0203c8872e0acdfadb))

### Features

- Add exception handler and improve custom exception
  ([`64c05ea`](https://github.com/crypticorn-ai/api-client/commit/64c05eafd011556b49786034d58a4de264438bfd))


## v2.5.0-rc.2 (2025-04-25)

### Bug Fixes

- Enforce stricter types on Http Exception and improve descriptions and doc string
  ([`0941780`](https://github.com/crypticorn-ai/api-client/commit/094178099ca1d01d763f41cce6ac898cbc77a9a3))


## v2.5.0-rc.1 (2025-04-25)

### Build System

- Update generation script to catch fallback if local server is not running
  ([`b5e9a16`](https://github.com/crypticorn-ai/api-client/commit/b5e9a16092c836bea38657b7ddab252945696848))

### Chores

- Deprecate is_equal function
  ([`b3b3094`](https://github.com/crypticorn-ai/api-client/commit/b3b309428dc078673a5b1718a7075855bce0c098))

### Features

- Add custom Http Exception class with shared error codes
  ([`aa0d851`](https://github.com/crypticorn-ai/api-client/commit/aa0d8515936ea65951608a9704f8d840069ac15d))


## v2.4.7 (2025-04-17)

### Bug Fixes

- Raise custom WebsockeError in ws auth dependencies
  ([`94f8b62`](https://github.com/crypticorn-ai/api-client/commit/94f8b62593d3f44785b11812102c3a4ab9195073))

### Performance Improvements

- Make pandas an optional dependency to decrease package size
  ([`cb942c7`](https://github.com/crypticorn-ai/api-client/commit/cb942c74d5d7836f9cab1beb2b1d5ee6a9be4d4e))


## v2.4.6 (2025-04-13)

### Bug Fixes

- Fixes config override bug
  ([`58c096b`](https://github.com/crypticorn-ai/api-client/commit/58c096b98a738c2c318768bae9f28ddb100fe127))

### Documentation

- Extend usage section
  ([`2887872`](https://github.com/crypticorn-ai/api-client/commit/28878720eeb0ad7461165402c5521258c1c7dc0e))


## v2.4.5 (2025-04-13)

### Bug Fixes

- Fixes fallback bug with pydantic
  ([`70d1257`](https://github.com/crypticorn-ai/api-client/commit/70d125723c7e707f765892270e6aa6977b5b25a5))


## v2.4.4 (2025-04-12)

### Bug Fixes

- Auth fixes on auth module
  ([`7c3ed5d`](https://github.com/crypticorn-ai/api-client/commit/7c3ed5d460e464939716361014514baff50d380d))

### Documentation

- Update advanced usage section
  ([`1c804bf`](https://github.com/crypticorn-ai/api-client/commit/1c804bf6eddceb19c31a553c1ff98b31fdd8cbc0))


## v2.4.3 (2025-04-12)

### Bug Fixes

- Fix utils import
  ([`29cc346`](https://github.com/crypticorn-ai/api-client/commit/29cc346c2ff835f8732644fbe21aadf62153c1d0))


## v2.4.2 (2025-04-12)

### Bug Fixes

- Add global utils and add http error mapping
  ([`c3ce565`](https://github.com/crypticorn-ai/api-client/commit/c3ce565446535038f196f65b9fdf276a6ce71563))


## v2.4.1 (2025-04-12)

### Bug Fixes

- Add market metrics scopes
  ([`2dc0b4f`](https://github.com/crypticorn-ai/api-client/commit/2dc0b4f1761d5bae07c946448a820d1fc9814288))

### Documentation

- Update structure section
  ([`cc77abc`](https://github.com/crypticorn-ai/api-client/commit/cc77abc19b5813e335356f4539654e04b8ba2014))


## v2.4.0 (2025-04-12)

### Features

- Add enum fallbacks, enum validation mixin and enum tests
  ([`63bd61c`](https://github.com/crypticorn-ai/api-client/commit/63bd61cd826f9de1aec40d5f877d82126b59fbf8))

- Start cli support for initializing files from templates
  ([`5411d12`](https://github.com/crypticorn-ai/api-client/commit/5411d12704605e6d6af46477ff74e1ac44abd259))


## v2.3.0 (2025-04-11)

### Features

- Add exchange and market enums
  ([`8ad2d7d`](https://github.com/crypticorn-ai/api-client/commit/8ad2d7dc982261f3e710c3e61755ea9613d982c3))


## v2.2.3 (2025-04-11)

### Bug Fixes

- Update error codes
  ([`3121fb0`](https://github.com/crypticorn-ai/api-client/commit/3121fb0bb4d05a6d62083d806fbc636761254448))


## v2.2.2 (2025-04-09)

### Bug Fixes

- Refactor generated model name by partial_model and add to init file
  ([`e663848`](https://github.com/crypticorn-ai/api-client/commit/e6638483bdeb01121749b579268493c7c67227dc))


## v2.2.1 (2025-04-09)

### Bug Fixes

- Add pydantic decorator that makes all fields of a model optional
  ([`1ae4432`](https://github.com/crypticorn-ai/api-client/commit/1ae44325194be3ca86eb72be5d3edc2442dd00cc))


## v2.2.0 (2025-04-09)

### Bug Fixes

- Fix import issues (fixes #22) and add auth module to main client
  ([`7f3f7c2`](https://github.com/crypticorn-ai/api-client/commit/7f3f7c2120af053b916aaa045444331998986f7d))

### Documentation

- Update README with configuration and response type sections
  ([`a9fbccf`](https://github.com/crypticorn-ai/api-client/commit/a9fbccfed254573d3e62332901704f39d8a6777f))

### Features

- Add module based configuration options for the client
  ([`553400c`](https://github.com/crypticorn-ai/api-client/commit/553400c642d3da4459daa4fa9b56588e9f519581))


## v2.1.6 (2025-04-08)

### Bug Fixes

- Add market metrics module
  ([`2954702`](https://github.com/crypticorn-ai/api-client/commit/29547025a0226bca1b9da9cfff5c89d3ed30f497))


## v2.1.5 (2025-04-08)

### Bug Fixes

- Update auth and trade module
  ([`df936b6`](https://github.com/crypticorn-ai/api-client/commit/df936b6eb76179a3eac6d7997c82ef30e74de860))


## v2.1.4 (2025-04-08)

### Bug Fixes

- Refactor api errors
  ([`885a20e`](https://github.com/crypticorn-ai/api-client/commit/885a20ec839dcf14fb4ec8d946cea76dcb15a65e))


## v2.1.3 (2025-04-08)

### Bug Fixes

- Use SecurityScopes class instead of list[Scope]
  ([`b41c718`](https://github.com/crypticorn-ai/api-client/commit/b41c718acc108e05b307abb399137c2fc30e56fd))


## v2.1.2 (2025-04-08)

### Bug Fixes

- Allow scopes to be set as strings
  ([`600babb`](https://github.com/crypticorn-ai/api-client/commit/600babb87c93aeecdc42aa19ebff1076a76404ea))


## v2.1.1 (2025-04-08)

### Bug Fixes

- Remove three unused scopes
  ([`3167308`](https://github.com/crypticorn-ai/api-client/commit/3167308b3df0c68b8e4c134841b437f40315a8e9))


## v2.1.0 (2025-04-07)

### Features

- Add api key authorization and websocket auth support
  ([`adeb8bd`](https://github.com/crypticorn-ai/api-client/commit/adeb8bdf42ed3da1b63b430f291e920e97d62d14))

### Refactoring

- Rename scopes and make requirements more strict
  ([`abf53a6`](https://github.com/crypticorn-ai/api-client/commit/abf53a6de46703a3ac2b0c66c101ec58ae8928f2))


## v2.0.1 (2025-04-06)

### Bug Fixes

- Refactor Scopes and Exception handling in auth client
  ([`8e9a64a`](https://github.com/crypticorn-ai/api-client/commit/8e9a64aa091cc3c840230ad2a7167c98426ae5c9))

### Build System

- Fix ci syntax and ssh errors
  ([`9ecfaa4`](https://github.com/crypticorn-ai/api-client/commit/9ecfaa4f09dfa4ae1667f9c1b9307d2623288f5f))

- Separate ci and update package config and deps
  ([`5367f2a`](https://github.com/crypticorn-ai/api-client/commit/5367f2a79028ed1f5e2c05ddded91a9ddbd0d9fa))

- Update ci
  ([`799fd96`](https://github.com/crypticorn-ai/api-client/commit/799fd962529b0120b290c3f5c253e9050b40a41b))

### Documentation

- Update Readme
  ([`39825b1`](https://github.com/crypticorn-ai/api-client/commit/39825b1506c2d5663ae8eecc6f73f8d6bed5692e))


## v2.0.0 (2025-04-06)

### Build System

- Add psr build_command
  ([`b661846`](https://github.com/crypticorn-ai/api-client/commit/b6618464c7d7727d34ab4a448f2e0104fcf4f3cc))

- Fix ci-cd
  ([`6edcb36`](https://github.com/crypticorn-ai/api-client/commit/6edcb3611673f191ec482e9d40614c7c2d2b59f3))

- Fix signing error in ci
  ([`0dcbf22`](https://github.com/crypticorn-ai/api-client/commit/0dcbf22892dbc17297cf9b91b35d62ec205a76ea))

- Fixes pypi packages dir
  ([`a25a458`](https://github.com/crypticorn-ai/api-client/commit/a25a4580c6a656e30d55b52c837480b833cb9aab))

- Update ci cd and configure PSR
  ([`e5d6fa5`](https://github.com/crypticorn-ai/api-client/commit/e5d6fa5d2ff4355f59fd4c92e4b9bed77fcae2d8))

BREAKING CHANGE: add several more backend api clients and restructure the modules


## v1.0.0 (2024-11-27)

### Continuous Integration

- Trigger workflow on PRs and changes to public folder (close #4)
  ([`08b9317`](https://github.com/crypticorn-ai/api-client/commit/08b931780ac872c6034883cd5ab83d2c7b380414))

### Features

- Add get Economics News
  ([`81575b1`](https://github.com/crypticorn-ai/api-client/commit/81575b18a7c925c5dafe18bd9e15807a282134e3))

- Add get Economics News
  ([`ccbfb7a`](https://github.com/crypticorn-ai/api-client/commit/ccbfb7a3d857ff5d531ec06f3b9df05b63f8dbf3))

- Add get Economics News
  ([`bc6574d`](https://github.com/crypticorn-ai/api-client/commit/bc6574dcadcdc9d05e860fde0aa285a4e7dcba32))
