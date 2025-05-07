# PDKMaster based GF180MCU PDK

This is pre-alpha development of PDKMaster based PDK for open source GF180MCU process.
Proper README still needs to be written.

# Versions

* [v0.0.11](https://gitlab.com/Chips4Makers/c4m-pdk-gf180mcu/-/commits/v0.0.11):
  Update for API changes for PDKMaster v0.12.0
* [v0.0.10](https://gitlab.com/Chips4Makers/c4m-pdk-gf180mcu/-/commits/v0.0.10):
  * build setup improvements
  * update dependencies
* [v0.0.9](https://gitlab.com/Chips4Makers/c4m-pdk-gf180mcu/-/commits/v0.0.9):
  * use common doit support from PDKMaster and pdkmaster.io.klayout
  * signoff related fixes
* [v0.0.8](https://gitlab.com/Chips4Makers/c4m-pdk-gf180mcu/-/commits/v0.0.8):
  * some build fixes
  * Rename StdCell3V3Lib to StdCellLib for consistency with other PDKs
  * provide scaled down cell with dimensions not based on lambda rules. More tight rules for logic voltage cells was possible by dedicated rules for mosfets with thick oxide.
* [v0.0.7](https://gitlab.com/Chips4Makers/c4m-pdk-gf180mcu/-/commits/v0.0.7):
  * Improved module load time though lazy library creation
  * In exported klayout technology use layer properties from upstream

No release notes for v0.0.6 or older. It mimiced the development of the Sky130 and IHPSG13G2 development up to that but with only a standard cell library.

## Project Arrakeen subproject

This project is part of Chips4Makers' [project Arrakeen](https://gitlab.com/Chips4Makers/c4m-arrakeen). It shares some common guide lines and regulations:

* [Contributing.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/Contributing.md)
* [LICENSE.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/LICENSE.md): license of release code
* [LICENSE_rationale.md](https://gitlab.com/Chips4Makers/c4m-arrakeen/-/blob/redtape_v1/LICENSE_rationale.md)
