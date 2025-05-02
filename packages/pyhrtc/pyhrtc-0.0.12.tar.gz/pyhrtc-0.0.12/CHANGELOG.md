# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added

### Fixed

## [0.0.12]

### Added

- `py.typed` file to acknowledge that this module is typed
- `Matching.matched()` now takes a `from_side` argument indicating whether the agent
    being passed in is from the left (and the matches should be from the right) or
    vice-versa. This is useful when there are agents on both sides with the same
    identifier.

### Fixed

## [0.0.11]

### Added

### Fixed

- Fixed spacing in typing for `Matching.blocking_pairs()`

## [0.0.10]

### Added

- `Matching.blocking_pairs()` - an iterator over blocking pairs in a matching. Also
    reworked `Matching.is_stable()` to use this iterator

### Fixed

## [0.0.9]

### Added

- Update stability checks to allow agents to have arbitrary "capacity rules". These can
    be implemented by sub-classing Agent and overloading the `Agent.could_admit()`
    function.

### Fixed

- Move all the scripts into a `scripts/` directory

## [0.0.8]

### Added

- Matchings
- Stability checking of matchings

## [0.0.4]

### Added
- This changelog
- Ability to constrain size of final stable matching in IP models
- Function to calculate weight of given matching

### Fixed
- Documentation for the (not necessarily stable) max weight and max size
  algorithms

## [0.0.3]

### Added
- Ability to have dummy variables in IP models

### Fixed
- Fixes to use objective in IP models correctly
## [0.0.2]

### Added
- IP models

## [0.0.1]

###Added
- Initial work
