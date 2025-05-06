class Constants:
    """
    A class to hold constant mappings and scales used throughout the application.

    Attributes
    ----------
    freq_map : dict
        A dictionary mapping time frequencies to their corresponding pandas resample codes.
        Keys are:
            'quarterly' -> 'Q'
            'monthly' -> 'M'
            'yearly' -> 'Y'
    agg_map : dict
        A dictionary mapping aggregation methods to their corresponding pandas aggregation functions.
        Keys are:
            'lastvalue' -> 'last'
            'mean' -> 'mean'
            'sum' -> 'sum'
            'min' -> 'min'
            'max' -> 'max'
    ANNSCALE_MAP : dict
        A dictionary mapping time frequencies to their corresponding annualization scales.
        Keys are:
            'daily' -> 36500
            'weekly' -> 5200
            'monthly' -> 1200
            'quarterly' -> 400
            'yearly' -> 100
            'annual' -> 100
    """

    freq_to_n = ['H', 'D', 'M', 'Q', 'Y']
    agg_map = {
        'lastvalue': 'last',
        'last': 'last',
        'mean': 'mean',
        'average': 'mean',
        'sum': 'sum',
        'min': 'min',
        'max': 'max'
    }
    
    # group similar date formats
    year_like = ['Y', 'YE', 'yearly', 'annual']
    quarter_like = ['Q', 'QE', 'QE-DEC', 'quarterly', 'QS', 'QS-OCT', 'QS', 'QS-NOV']
    month_like = ['M', 'ME', 'monthly', 'MS']
    week_like = ['W', 'W-SUN', 'weekly']
    day_like = ['D', 'daily']

    # return annualization scale
    def annscale_map(freq: str):
        """
        A function to return the annualization scale of a given frequency.

        Parameters
        ----------
        freq : str
            The frequency of the data to be annualized.

        Returns
        -------
        int
            The annualization scale of the given frequency.

        Raises
        ------
        ValueError
            If the given frequency is not recognized
        """
        if freq in Constants.year_like:
            return 100
        elif freq in Constants.quarter_like: # quarterly
            return 400
        elif freq in Constants.month_like: # monthly
            return 1200
        elif freq in Constants.week_like:
            return 5200
        elif freq in Constants.day_like:
            return 36500
        else:
            raise ValueError(f"Frequency {freq} not recognized.")

    