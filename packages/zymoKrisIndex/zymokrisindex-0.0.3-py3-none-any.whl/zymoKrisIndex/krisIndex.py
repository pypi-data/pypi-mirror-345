import bz2
from pydantic import BaseModel, Field
import pydantic_core
import statistics
import typing
import dataclasses
import random
import mpire
import os

"""
    A library for calculating the kris index of a given sequence.  The kris index is a measure of compressibility for
    a given sequence.
    
    Parameters
    ----------
    SHOW_PROGRESS : bool
        Whether or not to show a progress bar during parallel processing.
    VERIFY_ALPHABET : bool
        Whether or not to verify that the alphabet of a supplied sequence is valid relative to the expected set of 
        characters.
    HARD_ALPHABET_VERIFICATION : bool
        Whether or not to raise an error if the alphabet verification of a sequence fails.
    CASE_SENSITIVE_ALPHABET : bool
        Whether or not to treat the incoming sequences as having case sensitivity.  If false, the sequence will be
        converted to upper case.

    Notes
    -----
        You will most likely want to interact with this by first creating a `KrisScoreCalculator` object.
        Following that, you can use the `calculateKrisIndex` method to calculate the kris index of a given sequence.
        For parallel processing, use `calculateKrisIndexParallel` instead to speed up the calculation on a list of
        sequences.
    """

SHOW_PROGRESS = False
VERIFY_ALPHABET = False
HARD_ALPHABET_VERIFICATION = False
CASE_SENSITIVE_ALPHABET = False


class CharacterSet(BaseModel):
    """
        Stores a set of possible characters for generating and analyzing sequences.

        Parameters
        ----------
        characters : set
            The set of possible characters.  Ideally this should be a set of single character strings,
            but pydantic will try to turn anything it can into such a data structure.

        Notes
        -----
        Provides a lot of functionality around character sets, even potentially allowing their use as dictionary keys.
        """
    characters: typing.FrozenSet[typing.Annotated[str, 1]]

    def __len__(self):
        return len(self.characters)

    def __contains__(self, character):
        return character in self.characters

    def __iter__(self):
        return iter(self.characters)

    def __getitem__(self, index):
        return list(self.characters)[index]

    def __repr__(self):
        return str(self.characters)

    def __str__(self):
        return "".join(sorted(self.characters))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return str(self) <= str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def homopolymers(self, length:int) -> typing.List[str]:
        """
        Generate a list of all homopolymers of the character set.

        Parameters
        ----------
        length : int
            The length of the homopolymers to generate.

        Returns
        -------
        homopolymerList : List[str]
            A list of all possible homopolymers of a given length from the character set.
        """
        homopolymerList = []
        for character in self.characters:
            homopolymerList.append(character * length)
        return homopolymerList

    def randomers(self, length:int, count:int=10000) -> typing.List[str]:
        """
        Generate a list of random sequences of a given length and alphabet.

        Parameters
        ----------
        length : int
            The length of the sequences to generate.
        count : int
            The number of sequences to generate. Defaults to 10000.

        Returns
        -------
        randomerList : List[str]
            A list of random sequences of a given length from the character set.
        """
        charTuple = tuple(self.characters)
        randomerList = []
        for i in range(count):
            randomerList.append("".join(random.choices(charTuple, k=length)))
        return randomerList


@dataclasses.dataclass
class PrebuiltCharacterSets:
    """Prebuilt character sets for common single-letter bio alphabets."""
    dna = CharacterSet(characters = frozenset({"A", "C", "G", "T"}))
    rna = CharacterSet(characters = frozenset({"A", "C", "G", "U"}))
    amino = CharacterSet(characters = frozenset({"A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"}))


class KmerStatistics(BaseModel):
    """
        Data structure for storing kmer statistics for a given alphabet at a given length.

        Parameters
        ----------
        mean : float
            The mean kris value for sequences of the given alphabet and length. Stored as the percent of overhead length
        standardDeviation : float
            The standard deviation of the kris values for sequences of the given alphabet and length.
            Stored as the standard deviation of the kris values as a percent of overhead length
        overhead : float
            The average length of all possible homopolymers from the given character set when compressed.
            This should be the compressed size of the most compressible sequence of that length.
            The kris value for a given sequence is calculated as the compressed length of the sequence
            minus the overhead.

        Notes
        -----
        Keep an eye on these values when dealing with very short sequences. Mean kris values close to 1, standard
        deviations close to 0, and z statistics that are small indicate sequences where the compressibility differences
        between the most compressible and least compressible sequence are potentially too small to be useful.
        """
    mean: float = Field(ge=1)
    standardDeviation: float = Field(ge=0)
    overhead: float = Field(ge=1)

    @property
    def zStatistic(self):
        """
        A z-statistic is analogous to the z-score, and counts how many standard deviations are between the mean length
        of a compressed random sequence and the mean compressed length of all possible homopolymers.

        Returns
        -------
        zStatistic : float
            The calculated z-statistic.
        """
        if self.standardDeviation == 0:
            return 0
        meanLength = self.mean * self.overhead
        absoluteStdev = self.standardDeviation * meanLength
        return (meanLength - self.overhead) / absoluteStdev

    def __str__(self):
        return "m=%.1f, s=%.3f, o=%.1f, z=%.1f" % (self.mean, self.standardDeviation, self.overhead, self.zStatistic)

    def __repr__(self):
        return str(self)


class KmerStatTable(BaseModel):
    """
        Fundamentally a dictionary used to store kmer statistics for a given alphabet and length.

        Parameters
        ----------
        kmerStats : Dict[int, KmerStatistics]

        Notes
        -----
        This behaves like a dictionary, but the keys must be integers greater than 0.
        """
    kmerStats: typing.Optional[typing.Dict[typing.Annotated[int, Field(gt=0)], KmerStatistics]] = Field(default_factory=dict)

    def __getitem__(self, length: int):
        if length not in self.kmerStats:
            raise KeyError("Length key not found")
        return self.kmerStats[length]

    def __setitem__(self, length: int, value: KmerStatistics):
        if type(length) is not int:
            raise TypeError("Length key must be an integer")
        if length < 1:
            raise ValueError("Length key must be greater than 0")
        self.kmerStats[length] = value

    def __contains__(self, length: int):
        return length in self.kmerStats


def calculateKrisValue(sequence: str, overhead: float) -> float:
    """
    Calculate a kris value for a given sequence.  The kris value is calculated as the compressed length of the sequence
    divided by the overhead length.  This means that the kris value is the length of the compressed sequence given as
    a percentage of the most compressible sequences of the same length (homopolymers).

    Parameters
    ----------
    sequence : str
        The sequence to calculate a kris value for.
    overhead : float
        The overhead to use in calculating the kris value.

    Returns
    -------
    krisValue : float
        The calculated kris value.

    Notes
    -----
    This is a very low-level function. Generally you should be using `calculateKrisScore` or `calculateKrisIndex` instead.
    """
    compressedSequence = bz2.compress(bytes(sequence, "utf-8"))
    return len(compressedSequence)/overhead



def calculateKrisScore(sequence: str, overhead: float, mean: float) -> float:
    """
    Calculate a kris score for a given sequence.  The kris value is a measure of the kris value of the given sequence
    minus the mean kris value for random sequences of the same length.

    Parameters
    ----------
    sequence : str
        The sequence to calculate a kris score for.
    overhead : float
        The overhead to use in calculating the kris value.
    mean : float
        The mean kris value to subtract from the kris value.

    Returns
    -------
    krisScore : float
        The calculated kris score.

    Notes
    -----
    This is a very low-level function. Generally you should be using `calculateKrisIndex` instead.
    """
    krisValue = calculateKrisValue(sequence, overhead)
    return krisValue - mean


def calculateKrisIndex(sequence: str, kmerStatistics: KmerStatistics) -> float:
    """
    Calculate a kris index for a given sequence and kmer statistics.  The kris index is a measure of the kris score for
    the given sequence divided by the standard deviation of the kris scores for random sequences of the same length.
    At its essence, this says how many standard deviations more or less compressible the sequence is from the mean
    compressibility of random sequences of the same length.  Positive values indicate high complexity, while negative
    values indicate low complexity.

    Parameters
    ----------
    sequence : str
        The sequence to calculate a kris index for.
    kmerStatistics : KmerStatistics
        The kmer statistics to use for calculating the kris index.

    Returns
    -------
    krisIndex : float
        The calculated kris index.

    Notes
    -----
    This is a very low-level function. Generally you should be using `KrisScoreCalculator` instead
    for the full "batteries included" experience.  That class will maintain cached and potentially preloaded kmer
    statistics for you as well as parallelizing the calculation of kris scores if you have a large number of sequences.
    """
    krisScore = calculateKrisScore(sequence, kmerStatistics.overhead, kmerStatistics.mean)
    return krisScore / kmerStatistics.standardDeviation


def calculateKmerOverhead(alphabet: CharacterSet, length: int) -> float:
    """
    Calculate the overhead value for sequences of a given length and alphabet.

    The overhead value is the average length of the compressed homopolymers of the
    given length and alphabet.  It is used as a divisor in calculating a kris value.

    This value takes into account both the bytes added as part of the compression algorithm and the minimum length
    possible for the compressed data through the use of homopolymers.

    Parameters
    ----------
    alphabet : CharacterSet
        The set of characters to use for generating the homopolymers.
    length : int
        The length of the homopolymers to generate.

    Returns
    -------
    overhead : float
        The calculated overhead value.
    """
    homopolymers = alphabet.homopolymers(length)
    compressedHomopolymers = [bz2.compress(bytes(homopolymer, "utf-8")) for homopolymer in homopolymers]
    compressedHomopolymerLengths = [len(compressedHomopolymer) for compressedHomopolymer in compressedHomopolymers]
    return statistics.mean(compressedHomopolymerLengths)


class _ParallelKrisValueCalculator:
    """This class is used internally to parallelize the calculation of kris values.  You are likely looking for something else."""
    def __init__(self, overhead: float):
        """
        Initialize a ParallelKrisValueCalculator with a given overhead.

        Parameters
        ----------
        overhead : float
            The overhead to use when calculating kris values.

        """
        self.overhead = overhead

    def calculateKrisValue(self, sequence: str) -> float:
        return calculateKrisValue(sequence, self.overhead)


def calculateRandomerDistribution(alphabet: CharacterSet, length: int, count: int=10000, overhead: float=None) -> typing.Tuple[float, float]:
    """
    Calculate the mean and standard deviation of the distribution of kris values
    for random sequences of a given length and alphabet.

    :param alphabet: The CharacterSet to use for generating random sequences.
    :param length: The length of the sequences to generate.
    :param count: The number of random sequences to generate. Defaults to 10000.
    :param overhead: The overhead value to use for calculating kris values. If None,
                     the overhead is calculated for the appropriate sequence length
                     on the fly.
    :return: A tuple of two floats, the mean and standard deviation of the kris
             values for the generated sequences.
    """
    randomers = alphabet.randomers(length, count)
    if overhead is None:
        overhead = calculateKmerOverhead(alphabet, length)
    krisValueCalculator = _ParallelKrisValueCalculator(overhead)
    with mpire.WorkerPool() as pool:
        if SHOW_PROGRESS:
            print("Calculating randomer distribution for length %s" % length)
        krisValues = pool.map(krisValueCalculator.calculateKrisValue, randomers, progress_bar=SHOW_PROGRESS)
    return statistics.mean(krisValues), statistics.stdev(krisValues)


def calculateKmerStatistics(charset: CharacterSet, length: int, count: int=10000) -> KmerStatistics:
    """
    Calculate kmer statistics for a given character set and length.

    Parameters
    ----------
    charset : CharacterSet
        The alphabet to use for generating random sequences.
    length : int
        The length of the sequences to generate.
    count : int
        The number of random sequences to generate.

    Returns
    -------
    kmerStatistics : KmerStatistics
        The kmer statistics for the given alphabet and length.

    Notes
    -----
    The kmer statistics are calculated by generating a large number of random sequences
    of the given length and alphabet, calculating the kris value for each sequence,
    and then calculating the mean and standard deviation of the resulting distribution.
    """
    overhead = calculateKmerOverhead(charset, length)
    mean, standardDeviation = calculateRandomerDistribution(charset, length, overhead=overhead, count=count)
    return KmerStatistics(mean=mean, standardDeviation=standardDeviation, overhead=overhead)


class Alphabet(BaseModel):
    """
        This important class is what stores both the character set and cached kmer statistics for different lengths

        Parameters
        ----------
        characterSet : CharacterSet
            This is the data structure defining all possible characters that can be used.
        kmerStatistics : KmerStatistics
            The table kmer statistics for the given alphabet at different lengths.

        Notes
        -----
        Commonly used alphabets can have their kmer statistics precalculated and stored in a JSON to avoid redundant calculations
        """
    characterSet: CharacterSet
    kmerStatistics: typing.Optional[KmerStatTable] = Field(default_factory=KmerStatTable)

    def __contains__(self, item):
        if type(item) is int:
            return item in self.kmerStatistics
        elif type(item) is str:
            if len(item) == 1:
                return item in self.characterSet
            else:
                raise ValueError("Character lookup must be of length 1")
        else:
            raise TypeError("Character lookup must be of type int or a 1 character string")

    def __getitem__(self, length: int) -> KmerStatistics:
        if type(length) is not int:
            raise TypeError("Length key must be an integer")
        if length in self.kmerStatistics:
            return self.kmerStatistics[length]
        else:
            if length < 1:
                raise ValueError("Length key must be greater than 0")
        kmerStatistics = calculateKmerStatistics(self.characterSet, length)
        self.kmerStatistics[length] = kmerStatistics
        return kmerStatistics

    def dump(self) -> str:
        """
        Dumps the object to a JSON-formatted string.

        Returns
        -------
        str
            A JSON-formatted string representing the object.
        """
        return self.model_dump_json()

    @classmethod
    def load(cls, jsonStr: str) -> "Alphabet":
        """
        Loads an Alphabet object from a JSON-formatted string.

        Parameters
        ----------
        jsonStr : str
            A JSON-formatted string representing the object.

        Returns
        -------
        Alphabet
            An Alphabet object created from the JSON-formatted string.
        """
        return cls.model_validate(pydantic_core.from_json(jsonStr))


def read1kFile(biochars:str) -> str:
    """
    Reads the contents of the dna1000.json file distributed with this library.

    Returns
    -------
    str
        The contents of the dna1000.json file.
    """
    folder = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(folder, "%s1000.json" % biochars)
    return open(file).read()


DNA1000ALPHABET = Alphabet.load(read1kFile("dna"))
RNA1000ALPHABET = Alphabet.load(read1kFile("rna"))
AMINO1000ALPHABET = Alphabet.load(read1kFile("amino"))


class KrisIndexCalculator:
    def __init__(self, characterSet: [Alphabet, CharacterSet, typing.Iterable[str]]=DNA1000ALPHABET):
        """
        Creates a KrisScoreCalculator object.

        Parameters
        ----------
        characterSet : Alphabet or CharacterSet or Iterable[str], optional
            The character set to use for calculating kris scores.  If not provided, defaults to the DNA alphabet with
            precalculated kmer statistics for lengths 1-1000.

        Notes
        -----
        The character set is converted to an Alphabet object if it is not already one.
        """
        if type(characterSet) is Alphabet:
            self.alphabet = characterSet
        elif type(characterSet) is CharacterSet:
            self.alphabet = Alphabet(characterSet=characterSet)
        else:
            self.alphabet = Alphabet(characterSet=CharacterSet(characters=frozenset(characterSet)))

    def addKmerStatistics(self, length: int):
        """
        Pre-calculates and adds kmer statistics for a given length to the cached kmer statistics for the alphabet.

        Parameters
        ----------
        length : int
            The length of the kmer statistics to add.

        Returns
        -------
        None

        Notes
        -----
        This is useful for pre-calculating the kmer statistics you'll need to use for your kris index calculations.
        """
        _ = self.alphabet[length]  # presetting all the necessary kmer statistics, we don't actually care for the value right now

    def calculateKrisIndex(self, sequence: str) -> float:
        """
        Calculates the kris index for a given sequence.

        Parameters
        ----------
        sequence : str
            The sequence to calculate a kris index for.

        Returns
        -------
        krisIndex : float
            The calculated kris index.

        Notes
        -----
        This is more efficient for calculating a single kris index or a small number of them through iteration.
        Use `calculateKrisIndexParallel` if you have a large number of sequences.
        """
        if not CASE_SENSITIVE_ALPHABET:
            sequence = sequence.upper()
        if VERIFY_ALPHABET:
            for character in sequence:
                if character not in self.alphabet:
                    if HARD_ALPHABET_VERIFICATION:
                        raise ValueError("Sequence contains character not in alphabet: %s" % character)
                    else:
                        return -1.0
        kmerStatistics = self.alphabet[len(sequence)]
        return calculateKrisIndex(sequence, kmerStatistics)

    def calculateKrisIndexParallel(self, sequences: typing.List[str]) -> typing.List[float]:
        """
        Calculates the kris index for a given list of sequences in parallel.

        Parameters
        ----------
        sequences : List[str]
            The list of sequences to calculate a kris index for.

        Returns
        -------
        List[float]
            The calculated kris index for each sequence in the same order as the input list.

        Notes
        -----
        This method is more efficient for calculating a large number of kris indices
        through parallel processing. Use `calculateKrisIndex` if you have a single sequence
        or a small number of them to calculate.  This method will try to use all available cores.
        """
        lengthSet = set(map(len, sequences))
        for length in lengthSet:
            self.addKmerStatistics(length)
        with mpire.WorkerPool() as pool:
            if SHOW_PROGRESS:
                print("Calculating kris index for %s sequences" % len(sequences))
            return pool.map(self.calculateKrisIndex, sequences, progress_bar=SHOW_PROGRESS)


if __name__ == "__main__":
    SHOW_PROGRESS = True
    calc = KrisIndexCalculator()
    for i in range(3):
        calc.addKmerStatistics(i + 1)
        print("Got %s for length %s" % (calc.alphabet[i + 1], i + 1))
    serialized = calc.alphabet.dump()
    reloaded = Alphabet.load(serialized)
    print(reloaded[1])
    print(len(calc.alphabet.kmerStatistics.kmerStats))
