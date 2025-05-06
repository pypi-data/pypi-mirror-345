from _typeshed import Incomplete

class Database:
    """Database(fname=None)

    Database for storing objects using keys. These keys can be
    strings (restricted similar to Python variable names) or
    ssdf structs.

    When a filename is given, the database is loaded from that file (if
    it exists) and save() will save the database to this file.

    Objects to store should be classes natively supported by SSDF,
    or SSDF-compatible classes (i.e. classes
    that implement the __to_ssdf__ and __from_ssdf__ methods). See
    the documentation of SSDF for more information.

    """

    _fname: Incomplete
    _db: Incomplete
    _lastkey: str
    def __init__(self, fname: Incomplete | None = None) -> None: ...
    @property
    def db(self):
        """Get the underlying ssdf struct."""
    def set(self, key, object, save_now: bool = True) -> None:
        """set(key, object, save_now=True)

        Add an object to the database, using the given key.
        If save_now is True, will save the database to disk now.

        """
    def get(self, key):
        """get(key)

        Get the stored object using the given key. Returns None if no
        object is stored under the given key.

        """
    def save(self, fname: Incomplete | None = None) -> None:
        """save(fname=None)

        Save the results to disk now. If fname is not given, the last used
        fname is used. If there is no fname available, will raise a runtime
        error.

        """
    def _key2key(self, key):
        """_key2key(key)

        Get real key from given key.

        """
    def _hasher(self, object):
        """_hasher(object)

        Create a hash string from the given object. This object can be
        a string, dict or ssdf struct.

        """

NAME_SERIES_PARAMS: str
NAME_SERIES_RESULTS: str

class Experiment:
    """Experiment(params, database=None)

    Base class to perform experiments.

    This class enables users to do experiments. It uses the concept of
    series to enable sweeping different parameters. It can use a
    database to store and reuse experiment results.

    This class promotes the separation between the experiment and its
    quantitative analysis. The get_result() method, can be used to
    obtain the raw experiment results, which can then be processed
    before displaying them.


    Series
    ------
    When doing an experiment, one deals with statistics. Therefore an
    experiment should often be performed multiple times. Further, when
    testing an algorithm, one often wants to see how a specific parameter
    of the algorithm affects the performance.

    Therefore, one often wants to run a series of experiments. Sometimes
    one wants to run a series of series of experiments, and sometimes,
    one even wants to run a series of series of series of experiments ...

    This class uses the notion of series. Each series has a number, starting
    from zero. Series 0 simply means that the experiment is performed
    multiple times (while varying a parameter). Series 1 means that series 0
    is performed multiple times (while varying another parameter). Series 2
    means that series 1 is performed multiple times, etc.

    The number of series is limited by the maximum recursion depth of Python.

    In pseudocode:
    {{{
    for parameter_changes in series2:
        for parameter_changes in series1:
            for parameter_changes in series0:
                experiment()
    }}}


    Parameters
    ----------
    This class uses an ssdf struct to store the experiment parameters. Which
    parameter is changed in a series, and what values that parameter should
    take in that series, can be set using set_series_params().


    Buffering
    ---------
    This class can make use of a Database instance. When set, it will store
    all results produced by the experiment() method. This way, when an
    experiment is repeated with the same parameters, the experiment results
    can be obtained from the database.

    The database's save() method is called at the end of each series 1.
    Note that in order to use a database, the results produced by experiment()
    must be SSDF compatible, and if the result is a custom class, this class
    needs to be registered to SSDF.


    Usage
    -----
    To use this class, subclass it and implement the following methods:
      * experiment() - This method accepts one argument (a params struct)
        and should return a result object.
      * quantify_results() - To process the results, making them ready for
        presentation (using get_result()).
      * show_results() - Show the results (using quantift_results()).

    The quantify_results() and show_results() are not required to run the
    experiments, but function as a guide to process the experiment results.

    To run a single experiment with the given parameters, use do_experiment().
    To do a series of experiments, use do_experiment_series().

    There is an example at the bottom of the file (experiment.py) that defines
    this class.

    """

    _params: Incomplete
    _one_result: Incomplete
    _database: Incomplete
    _database_overwrite: bool
    _save_next_result: bool
    def __init__(self, params, database: Incomplete | None = None) -> None: ...
    def set_database(self, database: Incomplete | None = None) -> None:
        """set_database(database)

        Set the database to use to buffer experiment results. Call
        without arguments to disable using a database.

        Special database attrinutes
        ---------------------------
        The attribute _database_overwrite can be used to overwrite the
        database (for example when you changed your algoritm).

        The attribute _save_next_result can be set to False in experiment()
        to signal that the result that it produces should not be stored.
        This variable is reset each time before experiment() is called.

        """
    @property
    def params(self):
        """Get the original parameters as given during initialization."""
    def _get_list_member(self, name, series_nr, clear: bool = False):
        """_get_list_member(name, series_nr, clear=False)

        Return a list instance that is a member of this class,
        corresponding with the given name and series_nr. This method
        enables ad hoc creation of members as needed (since we do not
        know how many levels the user wants).

        """
    def set_series_params(self, series_nr, param, values) -> None:
        """set_series_params(seriesNr, param, values)

        Set which parameter to vary for the given series, and what values
        should be iterated.

        """
    def get_series_params(self, series_nr):
        """get_series_params(seriesNr)

        Get which parameter is varied for the given series, and what
        values are iterated.
        Returns a tuple (param, values).

        Raises a RuntimeError if no series params have been defined for the
        given series_nr.

        """
    def do_experiment_series(self, series_nr, params: Incomplete | None = None):
        """do_experiment_series(series_nr)

        Perform a series of experiments.

        Returns a list of results (which may contain lists of results, etc.).
        The results can also be accesed using the get_result() method.

        """
    def do_experiment(self, params: Incomplete | None = None):
        """do_experiment()

        Perform a single experiment.
        The resulting result is stored returned. The result can also be
        accesed using the get_result() method.

        """
    def get_result(self, *args):
        """get_result(series0_index, series1_index, series2_index, ...)

        Get the result (as returned by the overloaded experiment()) for the
        given series indices.

        If not arguments are given, returns the last result. If one index
        is given, returns the result corresponding to the last series 0. etc.

        None can be given for up to one series index, in which case a list
        of results is returned corresponding to the range of values given
        in set_series_params().

        """
    def experiment(self, params) -> None:
        """experiment(params)

        This is the method that needs to be implemented in order for
        the experiment to do what you want.

        """
    def quantify_results(self) -> None:
        """quantify_results()

        Implement this method to perform post-processing, to quantify
        the results. This might not be necessary in all situations.

        Hint
        ----
        When implementing this method, use get_result() to obtain results
        and return them in a way that allows easy representation.

        """
    def show_results(self) -> None:
        """show_results()

        Implement this method to show the results.

        Hint
        ----
        When implementing this method, use quantify_results() to obtain
        results ready for displaying and then dispay the result as
        appropriate.

        """
