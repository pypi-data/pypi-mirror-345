# KRIS Index

*The beauty of science is to make things simple*.  
A basic principle of information theory is that compressibility or reducibility of a piece of information is inverse in proportion to its information content or entropy.
At the same time, the Burrows-Wheeler transform (BWT) is a compression algorithm that is so effective on genomic sequence that it underlies many fundamental bioinformatic applications.
It also underlies the BZIP2 compression program.  Using this knowledge, we have developed the K-mer Reducible Information Statistic (KRIS) index, a new tool for analyzing the entropy/complexity/information content
of genomic reads or k-mers.  This system is designed to process k-mers efficiently and in a highly parallel manner to provide a fast filtering system that can be incorporated into bioinformatic pipelines.
While the obvious application of this system is to filter out low-complexity, low-information reads (and we do recommend it for that), we would also encourage you to keep these low-scoring reads to test how they are
handled by your favorite bioinformatic pipelines as a useful benchmark.  Additionally, this program can be used on reference genome-derived k-mers to identify high- and low-information content regions.

The mission of this application is identical to the [ZymoBIOMICS](https://www.zymoresearch.com/pages/zymobiomics-portfolio) mission: improvement of all aspects of microbiome research..

#### Publication
Please watch this spot for the preprint and eventual publication

## Quick Start Guide

#### Installation
```
pip3 install zymoKrisIndex
```

#### Usage
```
import zymoKrisIndex

sequence = "ATGCATGCATGCATGC" # Creating an arbitrary sequence

sequenceList = [sequence, sequence, sequence, sequence, sequence, sequence, sequence, sequence, sequence, sequence, ...]  # Creating a list of arbitrary sequences

dnaKris = zymoKrisIndex.KrisIndexCalculator()

krisIndex = dnaKris.calculateKrisIndex(sequence)  # returns the KRIS index as a float

krisIndices = dnaKris.calculateKrisIndexParallel(sequenceList)  # returns a list of KRIS indices

rnaKris = zymoKrisIndex.KrisIndexCalculator(zymoKrisIndex.RNA1000ALPHABET)  # Instantiates a KrisIndexCalculator with an RNA alphabet

proteinKris = zymoKrisIndex.KrisIndexCalculator(zymoKrisIndex.AMINO1000ALPHABET)  # Instantiates a KrisIndexCalculator with n amino acid alphabet
```


### Prerequisites

This application requires Python 3.10 or later.  It is also dependent on the Pydantic, bz2, and mpire packages.

### Installation

Installation of this package can be done using pip3 as shown above.

### API Reference

The API reference is available [API.md](API.md).

## Contributing

We welcome and encourage contributions to this project from the microbiomics community and will happily accept and acknowledge input (and possibly provide some free kits as a thank you).  We aim to provide a positive and inclusive environment for contributors that is free of any harassment or excessively harsh criticism. Our Golden Rule: *Treat others as you would like to be treated*.

## Versioning

We use a modification of [Semantic Versioning](https://semvar.org) to identify our releases.

Release identifiers will be *major.minor.patch*

Major release: Newly required parameter or other change that is not entirely backwards compatible
Minor release: New optional parameter
Patch release: No changes to parameters

## Authors

- **Michael M. Weinstein** - *Project Lead, Programming and Design* - [michael-weinstein](https://github.com/michael-weinstein)
- **Kyle McClary** - *Testing, Code Review* - [kylezymo](https://github.com/kylezymo)
- **Shuiquan Tang** - *Design* - [shuiquantang](https://github.com/shuiquantang)

See also the list of [contributors](contributors) who participated in this project.

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details.
This license restricts the usage of this application for non-open sourced systems. Please contact the authors for questions related to relicensing of this software in non-open sourced systems.

## Acknowledgments

We would like to thank the following, without whom this would not have happened:
* The Python Foundation
* The staff at Zymo Research
* The IMMSA bioinformatics interest group who suggested making this a full project
* Our customers

---------------------------------------------------------------------------------------------------------------------
## Microbial Dark Matter Symposium
If you are reading this, you are also probably interested in pushing the limits of microbiome research
and being able to study what we know is there, but cannot yet see. If so, the Microbial Dark Matter Symposium
is for you!

This symposium will emerging technologies, case studies, and practical applications in:

- Microbial Dark matter in Metagenomics to Explore Microbial Frontiers
- Exploring Microbial Dark Matter in Extreme and Low Biomass Environments
- Understanding Microbial Communities in the Built Environment
- Bioinformatics Tools for Large-Scale Exploration of Hidden Microbial Life
- Novel Methods for Cultivating ‘Unculturable’ Microbes

### [Register Here](https://www.microbial-dark-matter-symposium.com/)

---------------------------------------------------------------------------------------------------------------------

#### If you like this software, please let us know at info@zymoresearch.com.
#### Please support our continued development of free and open-source microbiomics applications by checking out the latest microbiomics offerings from [ZymoBIOMICS](https://www.zymoresearch.com/pages/zymobiomics-portfolio)
