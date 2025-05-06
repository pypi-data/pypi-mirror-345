import matplotlib.pyplot as plt
from timeseries import TimeseriesTable

class TimeseriesVisualizer:
    """
    A class for visualizing timeseries data using various plotting methods.

    Attributes
    ----------
    data : TimeseriesTable
        The timeseries data to be visualized.
    """

    def __init__(self, data: TimeseriesTable):
        """
        Initialize the TimeseriesVisualizer with a TimeseriesTable.

        Parameters
        ----------
        data : TimeseriesTable
            The timeseries data to be visualized.
        """
        self.data = data

    def subplotpad(self, top=0.1, left=0.1, vspace=0.1, hspace=0.1, right=0.05, bottom=0.1):
        """
        Adjust subplot positions.

        Parameters:
            top: Top margin (default: 0.11)
            left: Left margin (default: 0.075)
            vspace: Vertical space between subplots (default: 0.065)
            hspace: Horizontal space between subplots (default: 0.07)
            right: Right margin (default: 0.02)
            bottom: Bottom margin (default: 0.04)
        """
        # Get all axes (subplots) in the current figure, sorted top-left to bottom-right
        axes = sorted(plt.gcf().get_axes(), key=lambda ax: (-ax.get_position().y0, ax.get_position().x0))

        # Number of columns, and rows
        ncols = len({ax.get_position().x0 for ax in axes})
        nrows = len({ax.get_position().y0 for ax in axes})

        # Calculate width and height of each subplot
        width = (1 - left - hspace * (ncols - 1) - right) / ncols
        height = (1 - top - vspace * (nrows - 1) - bottom) / nrows

        # Adjust positions of each subplot
        for isub, ax in enumerate(axes):
            irow, icol = divmod(isub, ncols)  # Row and column indices
            left_pos = left + icol * (width + hspace)
            bottom_pos = 1 - top - (irow + 1) * height - irow * vspace
            ax.set_position([left_pos, bottom_pos, width, height])

    def subplots(self, save_path: str, variables: list[str] = None, start_date: str = "", end_date: str = "", is_percent: bool = False):
        """
        Creates a plot of multiple timeseries data in separate subplots.

        Parameters
        ----------
        save_path : str
            The path to save the plot.
        variables : list[str], optional
            A list of variables to plot. If None, all variables in the data are plotted.
        start_date : str, optional
            The start date for the plot.
        end_date : str, optional
            The end date for the plot.
        is_percent : bool, optional
            Whether to format the y-axis as percentages.

        Notes
        -----
        - Plot titles and axis labels can be adjusted with varialbe.set_label() and variable.set_percent().
        """
        # Use all variables if none are provided
        if variables is None:
            variables = list(self.data.df.columns)
        
        # Default to the full range of the data if no start or end dates are provided
        if not start_date:
            start_date = self.data.df.index[0]
        if not end_date:
            end_date = self.data.df.index[-1]

        # Determine the number of columns based on the number of variables
        num_vars = len(variables)
        if num_vars > 6: # three columns
            num_cols = 3
        elif num_vars >= 3: # two columns
            num_cols = 2
        else: # single column
            num_cols = 1
        num_rows = (num_vars + num_cols - 1) // num_cols  # Calculate the number of rows needed

        # Create subplots for each variable
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(6.5, 4))

        # Make the axes iterable even if there is only one subplot
        if num_vars > 1:
            axs = axs.flatten()
        else:
            axs = [axs]

        for idx, ax in enumerate(axs):
            # Stop plotting if all variables have been plotted
            if idx >= num_vars:
                ax.set_visible(False)
                continue
            
            # Plot each variable in its respective subplot
            ax.plot(self.data[variables[idx]][start_date:end_date])
            # Set the title using the variable label
            ax.set_title(self.data[variables[idx]].label)
            # Format the y-axis based on the is_percent flag
            if self.data[variables[idx]].is_percent or is_percent:
                ax.yaxis.set_major_formatter('{x:.0f}%')
            else:
                ax.yaxis.set_major_formatter('{x:.0f}')
            # Add grid and adjust subplot layout
            ax.grid()
            ax.autoscale(tight=True)
            ax.margins(y=0.05)  # Add padding to y-axis
            # Remove years from x-axis for inner plots
            if idx < num_vars - num_cols:
                ax.set_xticklabels([])

        # Optimize layout and save the plot
        plt.tight_layout()
        self.subplotpad()
        plt.savefig(save_path)
        plt.close()

    def two_vars(self, save_path: str, x_var: str, y_var: str, title: str = "", start_date: str = "", end_date: str = "", x_is_percent: bool = False, y_is_percent: bool = False):
        """
        Plot two variables against each other in one graph.

        Parameters
        ----------
        save_path : str
            The path to save the plot.
        x_var : str
            The variable for the x-axis.
        y_var : str
            The variable for the y-axis.
        title : str, optional
            The title of the plot.
        start_date : str, optional
            The start date for the plot.
        end_date : str, optional
            The end date for the plot.
        x_is_percent : bool, optional
            Whether to format the x-axis as percentages.
        y_is_percent : bool, optional
            Whether to format the y-axis as percentages.
        
        Notes
        -----
        - Plot titles and axis labels can be adjusted with varialbe.set_label() and variable.set_percent().
        """
        # Determine the overlap of the two variables in the specified date range
        if not start_date:
            start_date = max(self.data.df[x_var].index[0], self.data.df[y_var].index[0])
        if not end_date:
            end_date = min(self.data.df[x_var].index[-1], self.data.df[y_var].index[-1])

        # Create the plot
        fig, ax = plt.subplots(figsize=(6.5, 4))
        ax.scatter(self.data.df[x_var][start_date:end_date], self.data.df[y_var][start_date:end_date])

        # Set title and labels
        ax.set_title(title if title else f"{x_var} vs {y_var}")
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        # Format axes based on percentage flags
        if self.data[x_var].is_percent or x_is_percent:
            ax.xaxis.set_major_formatter('{x:.0f}%')
        else:
            ax.xaxis.set_major_formatter('{x:.0f}')
        if self.data[y_var].is_percent or y_is_percent:
            ax.yaxis.set_major_formatter('{x:.0f}%')
        else:
            ax.yaxis.set_major_formatter('{x:.0f}')
        # Add grid and adjust layout
        ax.grid()
        ax.autoscale(tight=True)
        ax.margins(x=0.05, y=0.05) # Add padding to x and y axes
        plt.savefig(save_path)
        plt.close()

    def multi_lines(self, save_path: str, variables: list[str], title: str, start_date: str = "", end_date: str = "", is_percent: bool = False):
        """
        Plot multiple variables on one graph.

        Parameters
        ----------
        save_path : str
            The path to save the plot.
        variables : list[str], optional
            A list of variables to plot.
            Default: [], plot all variables.
        title : str
            The title of the plot.
        start_date : str, optional
            The start date for the plot.
        end_date : str, optional
            The end date for the plot.
        is_percent : bool, optional
            Whether to format the y-axis as percentages.
        """
        # Default to the full range of the data if no start or end dates are provided
        if not start_date:
            start_date = min(self.data.df[var].index[0] for var in variables)
        if not end_date:
            end_date = max(self.data.df[var].index[-1] for var in variables)
        
        # Check for variables
        if len(variables) == 0:
            for var in self.data:
                variables.append(var)

        # Create the plot
        fig, ax = plt.subplots(figsize=(6.5, 4))

        # Define line styles to cycle through
        line_styles = [('red', '-'), ('blue', '--'), ('darkgreen', '-.'), ('black', ':')]
        # plot data, use default styles if insufficient predefined types
        if len(variables) <= len(line_styles):
            for idx, var in enumerate(variables):
                ax.plot(self.data.df[var][start_date: end_date], color=line_styles[idx][0], linestyle=line_styles[idx][1], label=var)
        else:
            for idx, var in enumerate(variables):
                ax.plot(self.data.df[var][start_date: end_date], label=var)  
   
        # Set title and format y-axis
        ax.set_title(title)
        ax.yaxis.set_major_formatter('{x:.0f}%' if is_percent else '{x:.0f}')
        # Add grid, legend, and adjust layout
        ax.grid()
        ax.autoscale(tight=True)
        ax.legend()
        plt.savefig(save_path)
        plt.close()

    def plot_individual(self, save_path: str, variables: list[str] = [], start_date: str = "", end_date: str = "", is_percent: bool = False):
        """
        Generate individual figures for the variables specified in the data.

        Parameters
        ----------
        save_path : str
            The path to save the plot. Figures saved as f"{save_path}_{variable_name}.png".
        variables : list[str], optional
            A list of variables to plot. 
            Default: [] (plot all variables).
        start_date : str, optional
            The start date for the plot.
            Default: "" (full range).
        end_date : str, optional
            The end date for the plot.
            Default: "" (full range).
        is_percent : bool, optional
            Whether to format the y-axis as percentages.
            Default: False (format as integers).
        """
        # Use all variables if none are provided
        if len(variables) == 0:
            variables = list(self.data.df.columns)

        # Create a plot for each variable
        for var in variables:
             # Default to the full range of the data if no start or end dates are provided
            if not start_date:
                series_start = self.data[var].index[0]
            if not end_date:
                series_end = self.data[var].index[-1]

            # Create the plot
            fig, ax = plt.subplots(figsize=(6.5, 4))
            ax.plot(self.data[var][series_start: series_end])
            ax.set_title(self.data[var].label)
            
            # Format the y-axis based on the is_percent flag
            if self.data[var].is_percent or is_percent:
                ax.yaxis.set_major_formatter('{x:.0f}%')
            else:
                ax.yaxis.set_major_formatter('{x:.0f}')

            # Add grid and adjust layout
            ax.grid()
            ax.autoscale(tight=True)
            ax.margins(y=0.05)

            # Save and close the figure
            save_path = str(save_path)
            if not save_path.endswith('/'):
                save_path += '/'
            if not save_path.endswith('.png'):
                save_path += '.png'
            if not save_path.endswith(f"{var}.png"):
                save_path = save_path.replace('.png', f"{var}.png")
            plt.savefig(f"{save_path}")
            plt.close()
