# krisIndex.py API Documentation

A Python library for calculating the Kris Index—a measure of compressibility for biological sequences.

---

## Table of Contents
- [Global Parameters](#global-parameters)
- [Classes](#classes)
  - [CharacterSet](#characterset)
  - [PrebuiltCharacterSets](#prebuiltcharactersets)
  - [KmerStatistics](#kmerstatistics)
  - [KmerStatTable](#kmerstattable)
  - [Alphabet](#alphabet)
  - [KrisScoreCalculator](#krisscorecalculator)
- [Functions](#functions)
  - [calculateKrisValue](#calculatekrisvalue)
  - [calculateKrisScore](#calculatekrisscore)
  - [calculateKrisIndex](#calculatekrisindex)
  - [calculateKmerOverhead](#calculatekmeroverhead)
  - [calculateRandomerDistribution](#calculaterandomerdistribution)
  - [calculateKmerStatistics](#calculatekmerstatistics)
  - [read1kFile](#read1kfile)

---

## Global Parameters
- `SHOW_PROGRESS` (bool): Show progress bar during parallel processing.
- `VERIFY_ALPHABET` (bool): Verify that the alphabet of a sequence is valid.
- `HARD_ALPHABET_VERIFICATION` (bool): Raise error if alphabet verification fails.
- `CASE_SENSITIVE_ALPHABET` (bool): Treat sequences as case-sensitive.

---

## Classes

### CharacterSet
Stores a set of possible characters for generating/analyzing sequences.
- **Fields:**
  - `characters`: frozenset of single-character strings.
- **Methods:**
  - Implements container, iterator, and comparison methods.
  - `homopolymers(length: int) -> List[str]`: Generate all homopolymers of the set.

### PrebuiltCharacterSets
Prebuilt character sets for common bio alphabets.
- **Fields:**
  - `dna`, `rna`, `amino`: Predefined `CharacterSet` objects for DNA, RNA, and amino acids.

### KmerStatistics
Stores k-mer statistics for a given alphabet and length.
- **Fields:**
  - `mean`: Mean kris value (percent overhead).
  - `standardDeviation`: Std. dev. of kris values.
  - `overhead`: Average compressed length of homopolymers.
- **Methods:**
  - `zStatistic()`: Number of std. deviations from mean.

### KmerStatTable
Dictionary-like storage for k-mer statistics.
- **Fields:**
  - `kmerStats`: Dict[int, KmerStatistics]
- **Methods:**
  - Dict-like access for k-mer statistics by length.

### Alphabet
Stores a `CharacterSet` and cached k-mer statistics.
- **Fields:**
  - `characterSet`: CharacterSet
  - `kmerStatistics`: KmerStatTable
- **Methods:**
  - Dict-like access for statistics by length.
  - `dump()`: Export as JSON.
  - `load(jsonStr)`: Load from JSON.

### KrisScoreCalculator
Main user-facing class for kris index calculations.
- **Constructor:**
  - `characterSet`: Alphabet/CharacterSet/Iterable[str] (defaults to DNA1000ALPHABET)
- **Methods:**
  - `addKmerStatistics(length: int)`: Pre-calculate statistics for a given length.
  - `calculateKrisIndex(sequence: str)`: Calculate kris index for a sequence.
  - `calculateKrisIndexParallel(sequences: List[str])`: Parallel kris index calculation.

---

## Functions

### calculateKrisValue(sequence: str, overhead: float) -> float
Calculate kris value as compressed length divided by overhead. Low-level utility.

### calculateKrisScore(sequence: str, overhead: float, mean: float) -> float
Kris value minus mean kris value for random sequences.

### calculateKrisIndex(sequence: str, kmerStatistics: KmerStatistics) -> float
Kris score divided by std. dev. of kris scores for random sequences.

### calculateKmerOverhead(alphabet: CharacterSet, length: int) -> float
Average compressed length of all homopolymers for a given alphabet and length.

### calculateRandomerDistribution(alphabet: CharacterSet, length: int, count: int=10000, overhead: float=None) -> (float, float)
Mean and std. dev. of kris values for random sequences.

### calculateKmerStatistics(charset: CharacterSet, length: int, count: int=10000) -> KmerStatistics
Generate k-mer statistics by simulating random sequences.

### read1kFile(biochars: str) -> str
Read the contents of the distributed `dna1000.json`, `rna1000.json`, or `amino1000.json` file.

---

## Prebuilt Alphabets
- `DNA1000ALPHABET`, `RNA1000ALPHABET`, `AMINO1000ALPHABET`: Preloaded `Alphabet` objects for common bio alphabets.

---

## Usage Example
```python
from zymoKrisIndex.krisIndex import KrisScoreCalculator

calc = KrisScoreCalculator()
score = calc.calculateKrisIndex("ACGTACGTACGT")
```

For parallel processing of many sequences, use `calculateKrisIndexParallel`.

---

For further details, see docstrings in the code or the full API reference in the source file.
