# Changelog

## [1.3.1] - 2024-05-18
### Added
- Info screen for hero attributes and talents.

## [1.3.0] - 2024-05-17
### Added
- Procedurally generated random maps.
- New talents for all classes.
- Monsters for the last three adventures.

### Changed
- Opened all adventures.
- Raised maximum level to 21.
- Improved talent functionality.
- Spellcasters chooce what spell to cast.

### Fixed
- Some values were not properly reset between games.

## [1.2.0] - 2024-04-15
### Added
- Magic items.
- Shop functionality.
- Volume controls.

### Changed
- Improved hero stat calculations.

## [1.1.1] - 2024-02-26
### Fixed
- Corrected versions of dependencies in setup and readme files.
- Adventure and location now resets properly when heroes are defeated.

## [1.1.0] - 2024-02-21
### Added
- Simulator.
- Sounds.
- Combat log.

### Changed
- Updated data storage to SQL database.
- Improved class balancing by implementing adjustments to specific classes that were underperforming based on simulation results. 
- Significantly expanded the adventure path, increasing its length and added content.

### Fixed
- Resolved issues with previously non-functional talents, ensuring that almost all talents now work.
- Resolved an issue where monsters were executing an additional attack during their turns, leading to unintended behavior.

## [1.0.0] - 2023-03-24
### Added
- Initial release.