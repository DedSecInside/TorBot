# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Statistics related stuff in igraph
"""

import math

__all__ = (
    "FittedPowerLaw",
    "Histogram",
    "RunningMean",
    "mean",
    "median",
    "percentile",
    "quantile",
    "power_law_fit",
)


class FittedPowerLaw:
    """Result of fitting a power-law to a vector of samples

    Example:

        >>> result = power_law_fit([1, 2, 3, 4, 5, 6])
        >>> result                   # doctest:+ELLIPSIS
        FittedPowerLaw(continuous=False, alpha=2.42..., xmin=3.0, L=-7.54..., \
D=0.21..., p=0.993...)
        >>> print(result)            # doctest:+ELLIPSIS
        Fitted power-law distribution on discrete data
        <BLANKLINE>
        Exponent (alpha)  = 2.42...
        Cutoff (xmin)     = 3.000000
        <BLANKLINE>
        Log-likelihood    = -7.54...
        <BLANKLINE>
        H0: data was drawn from the fitted distribution
        <BLANKLINE>
        KS test statistic = 0.21...
        p-value           = 0.993...
        <BLANKLINE>
        H0 could not be rejected at significance level 0.05
        >>> result.alpha             # doctest:+ELLIPSIS
        2.42...
        >>> result.xmin
        3.0
        >>> result.continuous
        False
    """

    def __init__(self, continuous, alpha, xmin, L, D, p):
        self.continuous = continuous
        self.xmin = xmin
        self.alpha = alpha
        self.L = L
        self.D = D
        self.p = p

    def __repr__(self):
        return "%s(continuous=%r, alpha=%r, xmin=%r, L=%r, D=%r, p=%r)" % (
            self.__class__.__name__,
            self.continuous,
            self.alpha,
            self.xmin,
            self.L,
            self.D,
            self.p,
        )

    def __str__(self):
        return self.summary(significance=0.05)

    def summary(self, significance=0.05):
        """Returns the summary of the power law fit.

        @param significance: the significance level of the Kolmogorov-Smirnov test
          used to decide whether the input data could have come from the fitted
          distribution
        @return: the summary as a string
        """
        result = [
            "Fitted power-law distribution on %s data"
            % ("discrete", "continuous")[bool(self.continuous)]
        ]
        result.append("")
        result.append("Exponent (alpha)  = %f" % self.alpha)
        result.append("Cutoff (xmin)     = %f" % self.xmin)
        result.append("")
        result.append("Log-likelihood    = %f" % self.L)
        result.append("")
        result.append("H0: data was drawn from the fitted distribution")
        result.append("")
        result.append("KS test statistic = %f" % self.D)
        result.append("p-value           = %f" % self.p)
        result.append("")
        if self.p < significance:
            result.append("H0 rejected at significance level %g" % significance)
        else:
            result.append(
                "H0 could not be rejected at significance " "level %g" % significance
            )

        return "\n".join(result)


class Histogram:
    """Generic histogram class for real numbers

    Example:

        >>> h = Histogram(5)     # Initializing, bin width = 5
        >>> h << [2,3,2,7,8,5,5,0,7,9]     # Adding more items
        >>> print(h)
        N = 10, mean +- sd: 4.8000 +- 2.9740
        [ 0,  5): **** (4)
        [ 5, 10): ****** (6)
    """

    def __init__(self, bin_width=1, data=None):
        """Initializes the histogram with the given data set.

        @param bin_width: the bin width of the histogram.
        @param data: the data set to be used. Must contain real numbers.
        """
        self._bin_width = float(bin_width)
        self._bins = None
        self._min, self._max = None, None
        self._running_mean = RunningMean()
        self.clear()

        if data:
            self.add_many(data)

    def _get_bin(self, num, create=False):
        """Returns the bin index corresponding to the given number.

        @param num: the number for which the bin is being sought
        @param create: whether to create a new bin if no bin exists yet.
        @return: the index of the bin or C{None} if no bin exists yet and
          {create} is C{False}."""
        if len(self._bins) == 0:
            if not create:
                result = None
            else:
                self._min = int(num / self._bin_width) * self._bin_width
                self._max = self._min + self._bin_width
                self._bins = [0]
                result = 0
            return result

        if num >= self._min:
            binidx = int((num - self._min) / self._bin_width)
            if binidx < len(self._bins):
                return binidx
            if not create:
                return None
            extra_bins = binidx - len(self._bins) + 1
            self._bins.extend([0] * extra_bins)
            self._max = self._min + len(self._bins) * self._bin_width
            return binidx

        if not create:
            return None

        extra_bins = int(math.ceil((self._min - num) / self._bin_width))
        self._bins[0:0] = [0] * extra_bins
        self._min -= extra_bins * self._bin_width
        self._max = self._min + len(self._bins) * self._bin_width
        return 0

    @property
    def n(self):
        """Returns the number of elements in the histogram"""
        return len(self._running_mean)

    @property
    def mean(self):
        """Returns the mean of the elements in the histogram"""
        return self._running_mean.mean

    @property
    def sd(self):
        """Returns the standard deviation of the elements in
        the histogram"""
        return self._running_mean.sd

    @property
    def var(self):
        """Returns the variance of the elements in the histogram"""
        return self._running_mean.var

    def add(self, num, repeat=1):
        """Adds a single number to the histogram.

        @param num: the number to be added
        @param repeat: number of repeated additions
        """
        num = float(num)
        binidx = self._get_bin(num, True)
        self._bins[binidx] += repeat
        self._running_mean.add(num, repeat)

    def add_many(self, data):
        """Adds a single number or the elements of an iterable to the histogram.

        @param data: the data to be added"""
        try:
            iterator = iter(data)
        except TypeError:
            iterator = iter([data])
        for x in iterator:
            self.add(x)

    __lshift__ = add_many

    def clear(self):
        """Clears the collected data"""
        self._bins = []
        self._min, self._max = None, None
        self._running_mean = RunningMean()

    def bins(self):
        """Generator returning the bins of the histogram in increasing order

        @return: a tuple with the following elements: left bound, right bound,
          number of elements in the bin"""
        x = self._min
        for elem in self._bins:
            yield (x, x + self._bin_width, elem)
            x += self._bin_width

    def __plot__(self, backend, context, **kwds):
        """Plotting support"""
        from igraph.drawing import DrawerDirectory

        drawer = DrawerDirectory.resolve(self, backend)(context)
        drawer.draw(self, **kwds)

    def to_string(self, max_width=78, show_bars=True, show_counts=True):
        """Returns the string representation of the histogram.

        @param max_width: the maximal width of each line of the string
          This value may not be obeyed if it is too small.
        @param show_bars: specify whether the histogram bars should be shown
        @param show_counts: specify whether the histogram counts should be
          shown. If both I{show_bars} and I{show_counts} are C{False},
          only a general descriptive statistics (number of elements, mean and
          standard deviation) is shown.
        """

        if self._min is None or self._max is None:
            return "N = 0"

        # Determine how many decimal digits should we use
        if int(self._min) == self._min and int(self._bin_width) == self._bin_width:
            number_format = "%d"
        else:
            number_format = "%.3f"
        num_length = max(len(number_format % self._min), len(number_format % self._max))
        number_format = "%" + str(num_length) + number_format[1:]
        format_string = "[%s, %s): %%s" % (number_format, number_format)

        # Calculate the scale of the bars on the histogram
        if show_bars:
            maxval = max(self._bins)
            if show_counts:
                maxval_length = len(str(maxval))
                scale = maxval // (max_width - 2 * num_length - maxval_length - 9)
            else:
                scale = maxval // (max_width - 2 * num_length - 6)
            scale = max(scale, 1)

        result = ["N = %d, mean +- sd: %.4f +- %.4f" % (self.n, self.mean, self.sd)]

        if show_bars:
            # Print the bars
            if scale > 1:
                result.append("Each * represents %d items" % scale)
            if show_counts:
                format_string += " (%d)"
                for left, right, cnt in self.bins():
                    result.append(
                        format_string % (left, right, "*" * (cnt // scale), cnt)
                    )
            else:
                for left, right, cnt in self.bins():
                    result.append(format_string % (left, right, "*" * (cnt // scale)))
        elif show_counts:
            # Print the counts only
            for left, right, cnt in self.bins():
                result.append(format_string % (left, right, cnt))

        return "\n".join(result)

    def __str__(self):
        return self.to_string()


class RunningMean:
    """Running mean calculator.

    This class can be used to calculate the mean of elements from a
    list, tuple, iterable or any other data source. The mean is
    calculated on the fly without explicitly summing the values,
    so it can be used for data sets with arbitrary item count. Also
    capable of returning the standard deviation (also calculated on
    the fly)
    """

    def __init__(self, items=None, n=0.0, mean=0.0, sd=0.0):
        """RunningMean(items=None, n=0.0, mean=0.0, sd=0.0)

        Initializes the running mean calculator.

        There are two possible ways to initialize the calculator.
        First, one can provide an iterable of items; alternatively,
        one can specify the number of items, the mean and the
        standard deviation if we want to continue an interrupted
        calculation.

        @param items: the items that are used to initialize the
          running mean calcuator. If C{items} is given, C{n},
          C{mean} and C{sd} must be zeros.
        @param n: the initial number of elements already processed.
          If this is given, C{items} must be C{None}.
        @param mean: the initial mean. If this is given, C{items}
          must be C{None}.
        @param sd: the initial standard deviation. If this is given,
          C{items} must be C{None}."""
        if items is not None:
            if n != 0 or mean != 0 or sd != 0:
                raise ValueError("n, mean and sd must be zeros if items is not None")
            self.clear()
            self.add_many(items)
        else:
            self._nitems = float(n)
            self._mean = float(mean)
            if n > 1:
                self._sqdiff = float(sd) ** 2 * float(n - 1)
                self._sd = float(sd)
            else:
                self._sqdiff = 0.0
                self._sd = 0.0

    def add(self, value, repeat=1):
        """RunningMean.add(value, repeat=1)

        Adds the given value to the elements from which we calculate
        the mean and the standard deviation.

        @param value: the element to be added
        @param repeat: number of repeated additions
        """
        repeat = int(repeat)
        self._nitems += repeat
        delta = value - self._mean
        self._mean += repeat * delta / self._nitems
        self._sqdiff += (repeat * delta) * (value - self._mean)
        if self._nitems > 1:
            self._sd = (self._sqdiff / (self._nitems - 1)) ** 0.5

    def add_many(self, values):
        """RunningMean.add(values)

        Adds the values in the given iterable to the elements from
        which we calculate the mean. Can also accept a single number.
        The left shift (C{<<}) operator is aliased to this function,
        so you can use it to add elements as well:

          >>> rm=RunningMean()
          >>> rm << [1,2,3,4]
          >>> rm.result               # doctest:+ELLIPSIS
          (2.5, 1.290994...)

        @param values: the element(s) to be added
        @type values: iterable"""
        try:
            iterator = iter(values)
        except TypeError:
            iterator = iter([values])
        for value in iterator:
            self.add(value)

    def clear(self):
        """Resets the running mean calculator."""
        self._nitems, self._mean = 0.0, 0.0
        self._sqdiff, self._sd = 0.0, 0.0

    @property
    def result(self):
        """Returns the current mean and standard deviation as a tuple"""
        return self._mean, self._sd

    @property
    def mean(self):
        """Returns the current mean"""
        return self._mean

    @property
    def sd(self):
        """Returns the current standard deviation"""
        return self._sd

    @property
    def var(self):
        """Returns the current variation"""
        return self._sd ** 2

    def __repr__(self):
        return "%s(n=%r, mean=%r, sd=%r)" % (
            self.__class__.__name__,
            int(self._nitems),
            self._mean,
            self._sd,
        )

    def __str__(self):
        return "Running mean (N=%d, %f +- %f)" % (self._nitems, self._mean, self._sd)

    __lshift__ = add_many

    def __float__(self):
        return float(self._mean)

    def __int__(self):
        return int(self._mean)

    def __complex__(self):
        return complex(self._mean)

    def __len__(self):
        return int(self._nitems)


def mean(xs):
    """Returns the mean of an iterable.

    Example:

        >>> mean([1, 4, 7, 11])
        5.75

    @param xs: an iterable yielding numbers.
    @return: the mean of the numbers provided by the iterable.

    @see: RunningMean() if you also need the variance or the standard deviation
    """
    return RunningMean(xs).mean


def median(xs, sort=True):
    """Returns the median of an unsorted or sorted numeric vector.

    @param xs: the vector itself.
    @param sort: whether to sort the vector. If you know that the vector is
      sorted already, pass C{False} here.
    @return: the median, which will always be a float, even if the vector
      contained integers originally.
    """
    if sort:
        xs = sorted(xs)

    mid = int(len(xs) / 2)
    if 2 * mid == len(xs):
        return float(xs[mid - 1] + xs[mid]) / 2
    else:
        return float(xs[mid])


def percentile(xs, p=(25, 50, 75), sort=True):
    """Returns the pth percentile of an unsorted or sorted numeric vector.

    This is equivalent to calling quantile(xs, p/100.0); see L{quantile}
    for more details on the calculation.

    Example:

        >>> round(percentile([15, 20, 40, 35, 50], 40), 2)
        26.0
        >>> for perc in percentile([15, 20, 40, 35, 50], (0, 25, 50, 75, 100)):
        ...     print("%.2f" % perc)
        ...
        15.00
        17.50
        35.00
        45.00
        50.00

    @param xs: the vector itself.
    @param p: the percentile we are looking for. It may also be a list if you
      want to calculate multiple quantiles with a single call. The default
      value calculates the 25th, 50th and 75th percentile.
    @param sort: whether to sort the vector. If you know that the vector is
      sorted already, pass C{False} here.
    @return: the pth percentile, which will always be a float, even if the vector
      contained integers originally. If p is a list, the result will also be a
      list containing the percentiles for each item in the list.
    """
    if hasattr(p, "__iter__"):
        return quantile(xs, (x / 100.0 for x in p), sort)
    return quantile(xs, p / 100.0, sort)


def power_law_fit(data, xmin=None, method="auto", p_precision=0.01):
    """Fitting a power-law distribution to empirical data

    @param data: the data to fit, a list containing integer values
    @param xmin: the lower bound for fitting the power-law. If C{None},
      the optimal xmin value will be estimated as well. Zero means that
      the smallest possible xmin value will be used.
    @param method: the fitting method to use. The following methods are
      implemented so far:

        - C{continuous}, C{hill}: exact maximum likelihood estimation
          when the input data comes from a continuous scale. This is
          known as the Hill estimator. The statistical error of
          this estimator is M{(alpha-1) / sqrt(n)}, where alpha is the
          estimated exponent and M{n} is the number of data points above
          M{xmin}. The estimator is known to exhibit a small finite
          sample-size bias of order M{O(n^-1)}, which is small when
          M{n > 100}. igraph will try to compensate for the finite sample
          size if n is small.

        - C{discrete}: exact maximum likelihood estimation when the
          input comes from a discrete scale (see Clauset et al among the
          references).

        - C{auto}: exact maximum likelihood estimation where the continuous
          method is used if the input vector contains at least one fractional
          value and the discrete method is used if the input vector contains
          integers only.
    @param p_precision: desired precision of the p-value calculation. The
      precision ultimately depends on the number of resampling attempts. The
      number of resampling trials is determined by 0.25 divided by the square
      of the required precision. For instance, a required precision of 0.01
      means that 2500 samples will be drawn.

    @return: a L{FittedPowerLaw} object. The fitted C{xmin} value and the
      power-law exponent can be queried from the C{xmin} and C{alpha}
      properties of the returned object.

    @newfield ref: Reference
    @ref: MEJ Newman: Power laws, Pareto distributions and Zipf's law.
      Contemporary Physics 46, 323-351 (2005)
    @ref: A Clauset, CR Shalizi, MEJ Newman: Power-law distributions
      in empirical data. E-print (2007). arXiv:0706.1062
    """
    from igraph._igraph import _power_law_fit

    if xmin is None or xmin < 0:
        xmin = -1

    method = method.lower()
    if method not in ("continuous", "hill", "discrete", "auto"):
        raise ValueError("unknown method: %s" % method)

    force_continuous = method in ("continuous", "hill")
    return FittedPowerLaw(*_power_law_fit(data, xmin, force_continuous, p_precision))


def quantile(xs, q=(0.25, 0.5, 0.75), sort=True):
    """Returns the qth quantile of an unsorted or sorted numeric vector.

    There are a number of different ways to calculate the sample quantile. The
    method implemented by igraph is the one recommended by NIST. First we
    calculate a rank n as q(N+1), where N is the number of items in xs, then we
    split n into its integer component k and decimal component d. If k <= 1,
    we return the first element; if k >= N, we return the last element,
    otherwise we return the linear interpolation between xs[k-1] and xs[k]
    using a factor d.

    Example:

        >>> round(quantile([15, 20, 40, 35, 50], 0.4), 2)
        26.0

    @param xs: the vector itself.
    @param q: the quantile we are looking for. It may also be a list if you
      want to calculate multiple quantiles with a single call. The default
      value calculates the 25th, 50th and 75th percentile.
    @param sort: whether to sort the vector. If you know that the vector is
      sorted already, pass C{False} here.
    @return: the qth quantile, which will always be a float, even if the vector
      contained integers originally. If q is a list, the result will also be a
      list containing the quantiles for each item in the list.
    """
    if not xs:
        raise ValueError("xs must not be empty")

    if sort:
        xs = sorted(xs)

    if hasattr(q, "__iter__"):
        qs = q
        return_single = False
    else:
        qs = [q]
        return_single = True

    result = []
    for q in qs:
        if q < 0 or q > 1:
            raise ValueError("q must be between 0 and 1")
        n = float(q) * (len(xs) + 1)
        k, d = int(n), n - int(n)
        if k >= len(xs):
            result.append(xs[-1])
        elif k < 1:
            result.append(xs[0])
        else:
            result.append((1 - d) * xs[k - 1] + d * xs[k])
    if return_single:
        result = result[0]
    return result


def sd(xs):
    """Returns the standard deviation of an iterable.

    Example:

        >>> sd([1, 4, 7, 11])       #doctest:+ELLIPSIS
        4.2720...

    @param xs: an iterable yielding numbers.
    @return: the standard deviation of the numbers provided by the iterable.

    @see: RunningMean() if you also need the mean
    """
    return RunningMean(xs).sd


def var(xs):
    """Returns the variance of an iterable.

    Example:

        >>> var([1, 4, 8, 11])            #doctest:+ELLIPSIS
        19.333333...

    @param xs: an iterable yielding numbers.
    @return: the variance of the numbers provided by the iterable.

    @see: RunningMean() if you also need the mean
    """
    return RunningMean(xs).var
