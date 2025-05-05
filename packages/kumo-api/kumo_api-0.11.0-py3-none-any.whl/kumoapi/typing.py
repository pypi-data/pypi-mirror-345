from kumoapi.common import StrEnum


class Stype(StrEnum):
    r"""The semantic type of a column.

    A semantic type denotes the semantic meaning of a column, and determines
    the preprocessing that is applied to the column. Semantic types can be
    passed to methods in the SDK as strings (*e.g.* ``"numerical"``).

    .. note::

        For more information about how to select a semantic type, please
        refer to https://docs.kumo.ai/docs/column-preprocessing.

    Attributes:
        numerical: A numerical column. Typically integers or floats.
        categorical: A categorical column. Typically boolean or string values
            typically a single token in length.
        multicategorical: A multi-categorical column. Typically a concatenation
            of multiple categories under a single string representation.
        ID: A column holding IDs. Typically numerical values used to uniquely
            identify different entities.
        text: A text column. String values typically multiple tokens in length,
            where the actual language content of the value has semantic
            meaning.
        timestamp: A date/time column.
        sequence: A column holding sequences/embeddings. Consists of lists of
            floats, all of equal length, and are typically the output of
            another AI model
        image: A column holding image URLs.
    """
    numerical = 'numerical'
    categorical = 'categorical'
    multicategorical = 'multicategorical'
    ID = 'ID'
    text = 'text'
    timestamp = 'timestamp'
    sequence = 'sequence'
    image = 'image'
    unsupported = 'unsupported'


class Dtype(StrEnum):
    r"""The data type of a column.

    A data type represents how the data of a column is physically stored. Data
    types can be passed to methods in the SDK as strings (*e.g.* ``"int"``).

    Attributes:
        bool: A boolean column.
        int: An integer column.
        float: An floating-point column.
        date: A column holding a date.
        time: A column holding a timestamp.
        floatlist: A column holding a list of floating-point values.
        intlist: A column holding a list of integers.
        binary: A column containing binary data.
        stringlist: A column containing list of strings.
    """
    bool = 'bool'
    int = 'int'
    byte = 'byte'
    int16 = 'int16'
    int32 = 'int32'
    int64 = 'int64'
    float = 'float'
    float32 = 'float32'
    float64 = 'float64'
    string = 'string'
    date = 'date'
    time = 'time'
    timedelta = 'timedelta'
    floatlist = 'floatlist'
    intlist = 'intlist'
    stringlist = 'stringlist'
    binary = 'binary'
    unsupported = 'unsupported'


class ColStatType(StrEnum):
    # Any:
    COUNT = 'COUNT'
    NUM_NA = 'NUM_NA'
    NA_FRACTION = 'NA_FRACTION'
    INVALID_FRACTION = 'INVALID_FRACTION'

    # Numerical, Temporal
    MIN = 'MIN'
    MAX = 'MAX'

    # Numerical:
    MEAN = 'MEAN'
    QUANTILES = 'QUANTILES'
    QUANTILE25 = 'QUANTILE25'
    MEDIAN = 'MEDIAN'
    QUANTILE75 = 'QUANTILE75'
    STD = 'STD'
    KURTOSIS = 'KURTOSIS'
    HISTOGRAM = 'HISTOGRAM'
    # num irrational entries (which are included in NA count and treated as NA)
    NUM_IRRATIONAL = 'NUM_IRRATIONAL'

    # Categorical:
    # NUM_UNIQUE and NUM_UNIQUE_MULTI count empty strings / NA values as their
    # own category. CATEGORY_COUNTS and MULTI_CATEGORY_COUNTS do not include
    # empty strings / NA values as their own category.
    NUM_UNIQUE = 'NUM_UNIQUE'
    NUM_UNIQUE_MULTI = 'NUM_UNIQUE_MULTI'
    CATEGORY_COUNTS = 'CATEGORY_COUNTS'
    MULTI_CATEGORY_COUNTS = 'MULTI_CATEGORY_COUNTS'

    UNIQUE_FRACTION = 'UNIQUE_FRACTION'

    # The separator to use for the multi-categorical column:
    MULTI_CATEGORIES_SEPARATOR = 'MULTI_CATEGORIES_SEPARATOR'

    # Strings:
    STRING_AVG_LEN = 'STRING_AVG_LEN'
    STRING_MAX_LEN = 'STRING_MAX_LEN'
    STRING_AVG_TOKENS = 'STRING_AVG_TOKENS'
    STRING_MAX_TOKENS = 'STRING_MAX_TOKENS'
    STRING_GLOVE_OVERLAP = 'STRING_GLOVE_OVERLAP'
    STRING_AVG_NON_CHAR = 'STRING_AVG_NON_CHAR'
    STRING_ARR_MIN_LEN = 'STRING_ARR_MIN_LEN'
    STRING_ARR_MAX_LEN = 'STRING_ARR_MAX_LEN'

    # Sequence:
    SEQUENCE_MAX_LENGTH = 'SEQUENCE_MAX_LENGTH'
    SEQUENCE_MIN_LENGTH = 'SEQUENCE_MIN_LENGTH'
    SEQUENCE_MEAN = 'SEQUENCE_MEAN'
    SEQUENCE_STD = 'SEQUENCE_STD'


class TimeUnit(StrEnum):
    r"""Defines the unit of a time."""
    SECONDS = 'seconds'
    MINUTES = 'minutes'
    HOURS = 'hours'
    DAYS = 'days'
    WEEKS = 'weeks'
    MONTHS = 'months'
