"""
    Developed at: ISTerre
    By: Lou MARILL
"""

import shutil
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

########################################################################
def plot(self, color='blue', title='', name_fig='', path_fig ='.',
         time_period=None, y_lim=None, size_fig=[20, 12], width_line=1.,
         size_marker=.5, acc=False, warn=True, save_model=False, byp_code=None):
    """
    Plot Gts raw data and model in dN, dE, dU

    Parameters
    ----------
    color : str, optional
        Color of the time series points.
        The default is 'blue'.
    title : str, optional
        Figure title.
        The default is '': the title will be the station code (|self.code|).
    name_fig : str, optional
        Name of the file to save the figure.
        The default is '': the figure's name will be the station code.
    path_fig : str, optional
        Path to save the figure.
        The default is '.'.
    time_period : None, list or np.ndarray, optional
        Inital and final time of the time period plot on the figure.
        The default is None: all the time period of Gts.
    y_lim : None, list or np.ndarray, optional
        Y-axe limits for the 3 subplots (dN, dE, dU).
        The default is None: between the smaller and the higher value for each
                             subplot.
    size_fig : list or np.ndarray, optional
        Size of the figure. Determine also the size of the text within.
        The default is [20, 12].
    width_line : int or float, optional
        Width of the Jps events lines.
        The default is 1..
    size_marker : int or float, optional
        Size of the marker for the time series data.
        The default is .5.
    acc : bool, optional
        Add "Quadratic model" if true.
        The default is False.
    warn : True, optional
        Print warning if true.
        The default is True.
    save_model : bool, optional
        Save synthetic model to a file.
        The default is False.
    byp_code : str, optional
        Code of the by-product
        The default is None.

    Raises
    ------
    ValueError
        If |time_period|, |y_lim| or |size_fig| is list and cannot be convert
        to np.ndarray.
        If |time_period| or |size_fig| is np.ndarray and has not exactly 2
        positive values.
        If |time_period|, |y_lim| or |size_fig| values are not int or float.
        If |y_lim| is np.ndarray and not 3x2 np.ndarray.
        If |width_line| or |size_marker| is not positive.
    TypeError
        If any parameter does not have the right type.
    WARNING
        If |acc| is not bool: |acc| set to False.

    """
    
    ######################################################################
    def _check_param(self, color, title, name_fig, path_fig, time_period,
                     y_lim, size_fig, width_line, size_marker, acc, warn, save_model, byp_code):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, adapt_bool
        
        # Change type
        # |time_period|
        if isinstance(time_period, list):
            (time_period, err_time) = list2ndarray(time_period)
            if err_time:
                raise ValueError(('Time period list must be convertible into '
                                  'np.ndarray (or time_period can be None or '
                                  'np.ndarray): |time_period=%s|.')
                                 % str(time_period))
        # |y_lim|
        if isinstance(y_lim, list):
            (y_lim, err_y) = list2ndarray(y_lim)
            if err_y:
                raise ValueError(('Y-axe limits list must be convertible into '
                                  'np.ndarray (or Y-axe limits can be None or '
                                  'np.ndarray): |y_lim=%s|.') % str(y_lim))
        # |y_lim|
        if isinstance(size_fig, list):
            (size_fig, err_fig) = list2ndarray(size_fig)
            if err_fig:
                raise ValueError(("Figure's size list must be convertible "
                                  "into np.ndarray (or figure's size can be "
                                  "np.ndarray): |size_fig=%s|.")
                                 % str(size_fig))
        
        # Check
        # |self|
        self.check_gts()
        # |color|
        if not isinstance(color, str):
            raise TypeError('Color must be str: |type(color)=%s|.'
                            % type(color))
        # |title|
        if not isinstance(title, str):
            raise TypeError('Title must be str: |type(title)=%s|.'
                            % type(title))
        # |name_fig|
        if not isinstance(name_fig, str):
            raise TypeError("Figure's name must be str: |type(name_fig)=%s|."
                            % type(name_fig))
        # |path_fig|
        if not isinstance(path_fig, str):
            raise TypeError("Figure's path must be str: |type(path_fig)=%s|."
                            % type(path_fig))
        # |time_period|
        if time_period is not None:
            if not isinstance(time_period, np.ndarray):
                raise TypeError(('Time period must be None, list or '
                                 'np.ndarray: |type(time_period)=%s|.')
                                % type(time_period))
            if time_period.size == 2:
                time_period = time_period.reshape(-1)
            if time_period.shape[0] != 2:
                raise ValueError(('Time period must be None, 2-value list or '
                                  '2-value np.ndarray: '
                                  '|time_period.shape[0]=%d|.')
                                 % time_period.shape[0])
            if time_period.dtype not in ['int', 'float']:
                raise ValueError(('Time period must be None, list of int, '
                                  'list of float, int np.ndarray or float '
                                  'np.ndarray: |time_period.dtype=%s|.')
                                 % time_period.dtype)
            if (time_period[0] < self.time[0, 0]
                or time_period[1] > self.time[-1, 0]):
                raise ValueError(('Time period must be None, or values must '
                                  'be within |self.time| period: '
                                  '|time_period=%s| and '
                                  '|self.time[[0, -1], 0]=%s|.')
                                 %(str(time_period),
                                   str(self.time[[0, -1], 1])))
        # |y_lim|
        if y_lim is not None:
            if not isinstance(y_lim, np.ndarray):
                raise TypeError(('Y-axe limits must be None, list or '
                                 'np.ndarray: |type(y_lim)=%s|.')
                                % type(y_lim))
            if y_lim.ndim != 2:
                raise ValueError(('Y-axe limits must be None, list of lists '
                                  'or 2D np.ndarray: |y_lim.ndim=%d|.')
                                 % y_lim.ndim)
            if y_lim.shape[1] != 2:
                raise ValueError(('Y-axe limits must be None, list of 2-value '
                                  'lists or 2-column np.ndarray: '
                                  '|y_lim.shape[1]=%d|.')
                                 % y_lim.shape[1])
            if y_lim.shape[0] != 3:
                raise ValueError(('Y-axe limits must be None, list of 3 '
                                  'lists, or 3-line np.ndarray: '
                                  '|y_lim.shape[0]=%d|.') % y_lim.shape[0])
            if y_lim.dtype not in ['int', 'float']:
                raise ValueError(('Y-axe limits must be None, list of int, '
                                  'list of float, int np.ndarray or float '
                                  'np.ndarray: |y_lim.dtype=%s|.')
                                 % y_lim.dtype)
        # |size_fig|
        if not isinstance(size_fig, np.ndarray):
            raise TypeError(("Figure's size must be list or np.ndarray: "
                             "|type(size_fig)=%s|.") % type(size_fig))
        if size_fig.size == 2:
            size_fig = size_fig.reshape(-1)
        if size_fig.shape[0] != 2:
            raise ValueError(("Figure's size must be 2-value list or 2-value "
                              "np.ndarray: |size_fig.shape[0]=%d|.")
                             % size_fig.shape[0])
        if size_fig.dtype not in ['int', 'float']:
            raise ValueError(("Figure's size must be list of int, list of "
                              "float, int np.ndarray or float np.ndarray: "
                              "|size_fig.dtype=%s|.") % size_fig.dtype)
        if (size_fig <= 0).any():
            raise ValueError(("Figure's size must be list of positive values "
                              "or positive np.ndarray: |size_fig=%s|.")
                             % str(size_fig))
        # |width_line|
        if not isinstance(width_line, (int, float)):
            raise TypeError(("Line's width must be int or float: "
                             "|type(width_line)=%s|.") % type(width_line))
        if width_line <= 0:
            raise ValueError("Line's width must be positive: |width_line=%g|."
                             % width_line)
        # |size_marker|
        if not isinstance(size_marker, (int, float)):
            raise TypeError(("Marker's size must be int or float: "
                             "|type(size_marker)=%s|.") % type(size_marker))
        if size_marker <= 0:
            raise ValueError(("Marker's size must be positive: "
                              "|size_marker=%g|.") % size_marker)
        
        # Adapt
        # |acc|
        (acc, warn_acc) = adapt_bool(acc)
        # |warn|
        (warn, _) = adapt_bool(warn, True)
        
        # Warning
        if warn and warn_acc:
            print('[WARNING] from method [plot] in [%s|' % __name__)
            print('/t|acc| parameter set to False because |type(acc)!=bool|!')
            print("\t'Quadratic model' will not be added to the figure title.")
            print()
        
        # Return
        return time_period, y_lim, size_fig, acc
    ######################################################################
    
    # Check parameters
    time_period, y_lim, size_fig, acc = _check_param(self, color, title,
                                                     name_fig, path_fig,
                                                     time_period, y_lim,
                                                     size_fig, width_line,
                                                     size_marker, acc, warn, save_model, byp_code)
    
    # To disable display and avoid associated warning 
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import matplotlib
        matplotlib.use('Agg')
    
    # Import
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    from os import makedirs
    from os.path import exists
    # import param_itsa as pm
    
    # Initialisation
    # Gts on |time_period| 
    if time_period is not None:
        ts = self.select_data((self.time[:, 0]>time_period[0])
                              & (self.time[:,0]<time_period[1]))
        ts.jps = ts.jps.select_ev((ts.jps.dates[:, 0]>time_period[0])
                                  & (ts.jps.dates[:,0]<time_period[1]))
    else:
        ts = self.copy()
        
    # Synthetic time series
    if ts.G is not None:
        synt = np.dot(ts.G, ts.MOD[:, :3])
    else:
        synt = np.zeros((ts.data.shape[0], 3))
    idx_nonan = np.unique(np.where(~np.isnan(ts.data))[0])
    synt[:idx_nonan[0]] = np.nan
    synt[idx_nonan[-1]+1:] = np.nan
    if save_model:
        folder_res = Path(path_fig)
        # Cherche le répertoire parent nommé "rringg_env" et prend son parent
        for parent in folder_res.parents:
            if parent.name == "PLOTS":
                folder_res = str(parent.parent)
                break

        folder_out = f"{folder_res}/OUTPUT_FILES" #os.path.join(folder_res, 'OUTPUT_FILES')
        # folder_out = os.path.join(pm.folder_res, 'OUTPUT_FILES')
        folder_pos = f"{folder_out}/TS_DATA" #os.path.join(folder_out, 'TS_DATA')
        synt_ts = np.insert(synt, 0, ts.time[:, 0], axis=1)
        data_np = ts.data[:, 0:3] 
        data_ts = np.insert(data_np, 0, ts.time[:, 0], axis=1)
        # print("folder_pos ......", folder_pos)
        if not exists(os.path.join(folder_pos, 'MODEL')):
            makedirs(os.path.join(folder_pos, 'MODEL'))
        if byp_code:
            np.savetxt(os.path.join(folder_pos, 'MODEL', f"{ts.code}_{byp_code}_model.txt"), synt_ts)
            np.savetxt(os.path.join(folder_pos, 'MODEL', f"{ts.code}_{byp_code}_data.txt"), data_ts)
        else:
            np.savetxt(os.path.join(folder_pos, 'MODEL', f"{ts.code}_model.txt"), synt_ts)
            np.savetxt(os.path.join(folder_pos, 'MODEL', f"{ts.code}_data.txt"), data_ts)
    # Figure title
    if title == '':
        title = 'Station '+ts.code
    if acc:
        title = title+' - Quadratic model'
    # Figure name
    if name_fig == '':
        name_fig = ts.code
    name_fig = name_fig+'.png'
    # Path to save the figure
    if path_fig != '.':
        if not exists(path_fig):
            makedirs(path_fig)
    # Y-axis limits
    if y_lim is None:
        y_min = np.c_[np.nanmin(ts.data[:, :3], axis=0),
                      np.nanmin(synt, axis=0)]
        y_max = np.c_[np.nanmax(ts.data[:, :3], axis=0),
                      np.nanmax(synt, axis=0)]
        y_lim = np.c_[np.min(y_min, axis=1),  np.max(y_max, axis=1)]
        y_lim += np.array([-1, 1])*np.abs(np.diff(y_lim))*.05
    for k in range(y_lim.shape[0]):
        if np.diff(y_lim[k, :]) == 0:
            if y_lim[k, 0] == 0:
                y_lim[k, 0] = -1
                y_lim[k, 1] = 1
            elif y_lim[k, 0] > 0:
                y_lim[k, :] += np.array([-1, 1])
    # X-axis limits
    x_lim = [ts.time[0, 0]-.05, ts.time[-1, 0]+.05]
    if ts.jps.shape() > 0:
        x_lim[0] = min(x_lim[0], ts.jps.dates[0, 0]-.05)

    # Create figure
    # Change all font size
    plt.rc('font', **{'size' : size_fig[0]/1.2})
    # Subplot
    (fig, axes) = plt.subplots(3, sharex=True, figsize=size_fig)
    # Title
    fig.suptitle(title, fontsize=size_fig[0]*1.2, fontweight='bold')
    # Enable minor ticks 
    plt.minorticks_on()

    #_vline_jps(jps, axes, color, label, width_line, alpha=.2):

    # Jps event lines
    if ts.jps.shape() > 0:
        # Swarms
        axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='W'), axes,
                          'lime', 'Swarm of earthquakes', width_line)
        # SSEs
        axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='S'), axes,
                          'darkturquoise', 'SSEs', width_line)
        # Unknown phenomena
        axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='U'), axes,
                          'black', 'Unknown phenomenon', width_line)
        # Antenna changes
        axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='A'), axes,
                          'magenta', 'Antenna change', width_line)

        #print('Antenna change', ts.jps.select_ev(ts.jps.type_ev=='A'))

        # Earthquakes without post-seismic
        axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='E'), axes,
                          'gold',
                          'Earthquake with Mw>=%.1f' % ts.jps.mag_min,
                          width_line)

        # Earthquakes with post-seismic
        if ts.jps.mag_spe is None:
            axes = _vline_jps(ts.jps.select_ev(ts.jps.type_ev=='P'), axes,
                              'goldenrod', (('Earthquake with post-seismic '
                                          'transient (Mw>=%.1f)')
                                         % ts.jps.mag_post),
                              2*width_line)
        else:
            # Earthquakes with normal post-seismic
            axes = _vline_jps(ts.jps.select_ev((ts.jps.type_ev=='P') &
                                               ((ts.jps.mag<ts.jps.mag_spe) |
                                                (ts.jps.dates[:, 1]
                                                 <= ts.time[idx_nonan[0],
                                                            1]))),
                              axes, 'goldenrod',
                              ('Earthquake with post-seismic transient '
                               '(Mw>=%.1f)') % ts.jps.mag_post,
                              2*width_line)
            # Earthquakes with special post-seismic
            axes = _vline_jps(ts.jps.select_ev((ts.jps.type_ev=='P') &
                                               (ts.jps.mag>=ts.jps.mag_spe) &
                                               (ts.jps.dates[:, 1]
                                                > ts.time[idx_nonan[0], 1])),
                              axes, 'darkgoldenrod',
                              ('Earthquake with special post-seismic '
                               'transient (Mw>=%.1f)') % ts.jps.mag_spe,
                              2*width_line)
        # Legend
        axes[0].legend(loc='best', fontsize=size_fig[0]/1.5)

        text_info=[]
        # Jps magnitude
        jps_wmag = ts.jps.select_ev(ts.jps.mag>0)
        if jps_wmag.shape() > 0:
            amp = y_lim[0, 1]-y_lim[0, 0]
            group_idxjps = [[0]]
            for idx in range(1, jps_wmag.shape()):
                if (jps_wmag.dates[idx, 1]
                    - jps_wmag.dates[group_idxjps[-1][0], 1] 
                    < ts.data.shape[0]/50):
                    group_idxjps[-1].append(idx)
                else:
                    group_idxjps += [[idx]]
            for g in range(len(group_idxjps)):
                for idx in range(len(group_idxjps[g])):
                    tilt = y_lim[0, 1]+amp*.1*(idx+1/3)
                    axes[0].text(jps_wmag.dates[group_idxjps[g][idx], 0], tilt,
                                  '%.1f' % jps_wmag.mag[group_idxjps[g][idx]],
                                  horizontalalignment='center')

                    text_info.append([jps_wmag.dates[group_idxjps[g][idx], 0], tilt, '%.1f' % jps_wmag.mag[group_idxjps[g][idx]]])

    # Time series
    y_labels = ['North [mm]', 'East [mm]', 'Up [mm]']
    
    # if str(Path(path_fig).name) == "ANALYSIS":
    #     combined = np.hstack([ts.time[:, [0]], ts.data[:, 0:3], synt])
    #     np.savetxt(f"{path_fig}/{ts.code}_model.txt", combined)

    for sub in range(len(axes)):

        if 'f18_data' in name_fig:
            print('xlim',x_lim)
            print('ylim',y_lim[sub, :])

        df = pd.DataFrame(ts.time[:, 0], columns = ['date'])
        df['data'] = ts.data[:, sub]
        df.dropna(inplace=True)
        df['index'] = [i for i in range(len(df))]
        df.set_index('index', inplace=True)


        df2 = pd.DataFrame(ts.time[:, 0], columns = ['date'])
        df2['model'] = synt[:, sub]
        df2.dropna(inplace=True)
        df2['index'] = [i for i in range(len(df2))]
        df2.set_index('index', inplace=True)



        max_offset = (df['data'].diff()).abs().max()

        # print(synt[:, [0,1,2]])
        # np.savetxt(os.path.join(folder_pos, 'MODEL', f"{ts.code}_model.txt"), synt_ts)
        
        # synt_ts = np.insert(synt, 0, ts.time[:, 0], axis=1)a
        # data_np = ts.data[:, 0:3] 
        # data_ts = np.insert(data_np, 0, ts.time[:, 0], axis=1)
        
        # np.hstack([ts.time[:, [0]], ts.data[:, 0:3], synt])

        if max_offset >= 10000 :

            idx_max = df['data'][(df['data'].diff()).abs() == (df['data'].diff()).abs().max()].index[0]
            idx_mod = df2['model'][(df2['model'].diff()).abs() == (df2['model'].diff()).abs().max()].index[0]

            date_offset = df['date'].loc[idx_max]

            top = df['data'].loc[idx_max]
            low = df['data'].loc[idx_max -1 ]

            direction = top - low

            for i in range(len(ts.data[:, sub])):
                if round(ts.data[:, sub][i], 3) == round(df['data'].loc[idx_max], 3):
                    index =  i

            for j in range(len(synt[:, sub])):
                if round(synt[:, sub][j], 3) == round(df2['model'].loc[idx_mod], 3):
                    index2 =  j


            if top < low:
                top = df['data'].loc[idx_max -1]
                low = df['data'].loc[idx_max]
            #print(top, low)
            gap = str(round(abs(top - low)/1000, 1)) + ' m'

            ax = axes[sub]

            divider = make_axes_locatable(ax)
            ax2 = divider.new_vertical(size="100%", pad=0.2)
            fig.add_axes(ax2)

            for line in ax.get_lines():
                ax2.axvline(line.get_xdata()[0], color=line.get_color(), label=line.get_label(), linewidth=line.get_linewidth())

            if direction > 0 :
                ax.scatter(ts.time[:index, 0], ts.data[:index, sub], size_marker, color)
                ax.plot(ts.time[:index2, 0], synt[:index2, sub], 'red', linewidth=width_line*2)
                ax.set_ylim(mk_ylim(ts.data[:index, sub], synt[:index2, sub]))

                ax.spines['top'].set_visible(False)
                ax2.scatter(ts.time[index:, 0], ts.data[index:, sub], size_marker, color)
                ax2.plot(ts.time[index2:, 0], synt[index2:, sub], 'red', linewidth=width_line*2)
                ax2.set_ylabel(y_labels[sub])
                ax2.yaxis.set_label_coords(-.07, -0)
                ylim_ax2 = mk_ylim(ts.data[index:, sub], synt[index2:, sub])
                ax2.set_ylim(ylim_ax2)

            else:
                ax.scatter(ts.time[index:, 0], ts.data[index:, sub], size_marker, color)
                ax.plot(ts.time[index2:, 0], synt[index2:, sub], 'red', linewidth=width_line*2)
                ax.set_ylim(mk_ylim(ts.data[index:, sub], synt[index2:, sub]))

                ax.spines['top'].set_visible(False)
                ax2.scatter(ts.time[:index, 0], ts.data[:index, sub], size_marker, color)
                ax2.plot(ts.time[:index2, 0], synt[:index2, sub], 'red', linewidth=width_line*2)
                ax2.set_ylabel(y_labels[sub])
                ax2.yaxis.set_label_coords(-.07, -0)
                ylim_ax2 = mk_ylim(ts.data[:index, sub], synt[:index2, sub])
                ax2.set_ylim(ylim_ax2)

            ax2.text(date_offset, ylim_ax2[1] + (ylim_ax2[1] - ylim_ax2[0])*0.15*(1/3), gap, horizontalalignment='center')

            if sub == 0:
                idx = 0
                prev=0
                for i in range(len(text_info)):

                    if abs(text_info[i][0] - prev) < (1/50)*(x_lim[1] - x_lim[0]) or abs(text_info[i][0] - date_offset) < (1/50)*(x_lim[1] - x_lim[0]):
                        idx += 1
                    else:
                        idx = 0
                    tilt = ylim_ax2[1] + (ylim_ax2[1] - ylim_ax2[0])*0.15*(idx + 1/3)
                    ax2.text(text_info[i][0], tilt, text_info[i][2], horizontalalignment='center')
                    prev = text_info[i][0]

            #ax2.text(date_offset, ylim_ax2[1] + (ylim_ax2[1] - ylim_ax2[0])*0.15*(1/3), gap, horizontalalignment='center')

            ax2.tick_params(bottom=False, labelbottom=False)
            ax2.spines['bottom'].set_visible(False)

            ax.grid(True, which='both', linestyle=':')
            ax2.grid(True, which='both', linestyle=':')
            ax.set_xlim(x_lim)
            ax2.set_xlim(x_lim)

            d = 0.0075

            kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
            ax2.plot((-d, +d), (-d, +d), **kwargs)
            ax2.plot((1 - d, 1 + d), (-d, +d), **kwargs)

            kwargs.update(transform=ax.transAxes)
            ax.plot((-d, +d), (1 - d, 1 + d), **kwargs)
            ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
        else:
            axes[sub].scatter(ts.time[:, 0], ts.data[:, sub], size_marker, color)
            axes[sub].plot(ts.time[:, 0], synt[:, sub], 'red', linewidth=width_line*2)
            axes[sub].set_ylim(y_lim[sub, :])
        axes[sub].set_ylabel(y_labels[sub])
        axes[sub].grid(True, which='both', linestyle=':')
    axes[2].set_xlabel('Time [decimal year]')
    axes[2].set_xlim(x_lim)

    if max_offset < 10000 :
        plt.tight_layout(pad=0.8)

    # if str(Path(path_fig).name) == "ANALYSIS" :
    #     # print(synt)
    #     if "_data" in name_fig:
    #         combined = np.hstack([ts.time[:, [0]], ts.data[:, 0:3], synt[:, 0:3]])
    #         np.savetxt(f"{path_fig}/{ts.code}_model.txt", combined)

    # Save figure
    fig.savefig(path_fig+name_fig)
    plt.close(fig)
    
    if str(Path(path_fig).name) == "ANALYSIS" :
        shutil.copy(f"{path_fig}/{name_fig}", f"{str((Path(path_fig).parent).parent)}/{name_fig}")
        # print(synt)
        if "_data" in name_fig:
            combined = np.hstack([ts.time[:, [0]], ts.data[:, 0:3], synt[:, 0:3]])
            np.savetxt(f"{path_fig}/{ts.code}_model.txt", combined)
            shutil.copy(f"{path_fig}/{ts.code}_model.txt", f"{str((Path(path_fig).parent).parent)}/{ts.code}_model.txt")

##############################################################
def _vline_jps(jps, axes, color, label, width_line, alpha=.2):
    """
    Display vertical line at Jps dates

    Parameters
    ----------
    jps : Jps
        Jps catalog.
    axes : TYPE
        Axes of the figure on which vertical lines are displayed.
    color : str
        Color of the vertical lines.
    label : str
        Label of all (these) vertical lines.
    width_line : float
        Width of the vertical lines.

    Returns
    -------
    axes : np.ndarray
        Axes of the figure on which vertical lines are displayed.

    """

    from itsa.lib.astrotime import mjd2decyear

    if jps.shape() > 0:
        for sub in range(len(axes)):
            if any(jps.dur>0):
                for idx in range(jps.shape()):
                    end_date = mjd2decyear(jps.dates[idx, 1]+jps.dur[idx])
                    axes[sub].axvspan(jps.dates[idx, 0], end_date, color=color,
                                      alpha=alpha)
            axes[sub].axvline(jps.dates[0, 0], color=color, label=label,
                              linewidth=width_line)
            for idx in range(1, jps.shape()):
                axes[sub].axvline(jps.dates[idx, 0], color=color,
                                  linewidth=width_line)
    return axes

##############################################################

def mk_ylim(raw_data, model_data):
    # Y-axis limits
    y_min = np.c_[np.nanmin(raw_data),
                  np.nanmin(model_data)]
    y_max = np.c_[np.nanmax(raw_data),
                  np.nanmax(model_data)]

    y_lim = np.c_[np.min(y_min, axis=1),  np.max(y_max, axis=1)]
    y_lim += np.array([-1, 1])*np.abs(np.diff(y_lim))*.05
    for k in range(y_lim.shape[0]):
        if np.diff(y_lim[k, :]) == 0:
            if y_lim[k, 0] == 0:
                y_lim[k, 0] = -1
                y_lim[k, 1] = 1
            elif y_lim[k, 0] > 0:
                y_lim[k, :] += np.array([-1, 1])
    return y_lim[0]
