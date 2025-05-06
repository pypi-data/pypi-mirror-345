"""
    Developed at: ISTerre
    By: Lou MARILL
"""


#############################################################################
def save_byp(ts, vel=False, seas=False, ant=False, co=False, sw=False,
              sse=False, post=False, names=False, disp=False, outdir_pos='.',
              outdir_fig='.', add_key='', replace=False, warn=True):
    """
    Save (and display) Gts analysis by-product

    Parameters
    ----------
    ts : Gts
        Gts from which extract by-product to save.
    vel : bool, list or np.ndarray, optional
        Correct velocity (and acceleration) trend if true.
        The default is False.
    seas : bool, list or np.ndarray, optional
        Correct seasonal variations if true.
        The default is False.
    ant : bool, list or np.ndarray, optional
        Correct antenna changes if true.
        The default is False.
    co : bool, list or np.ndarray, optional
        Correct co-seismic jumps if true.
        The default is False.
    sw : bool, list or np.ndarray, optional
        Correct swarms if true.
        The default is False.
    sse : bool, list or np.ndarray, optional
        Correct SSEs if true.
        The default is False.
    post : bool, list or np.ndarray, optional
        Correct post-seismic effects if true.
        The default is False.
    names : str, list or np.ndarray, optional
        Folder names to save by-product.
        The default is False.
    disp : bool, list or np.ndarray, optional
        Display by-product figures if true.
        The default is False.
    outdir_pos : str, optional
        Output directory for pos files.
        The default is '.'.
    outdir_fig : str, optional
        Output directory for figures.
        The default is '.'.
    add_key : str, optional
        Output file name will be '|self.code|_add_key.pos' if |add_key|
        is not empty.
        The default is '': output file will be '|self.code|.pos'.
    replace : bool, optional
        Replace existing file with the same name in the output directory by the
        writen file if true.
        The default is False.
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    GtsError
        If |GMOD_names| is None
    ValueError
        If |vel|, |seas|, |ant|, |co|, |sw|, |sse|, |post|, or |disp| values
        are not all bool.
        If |names| values are not all str.
        If |vel|, |seas|, |ant|, |co|, |sw|, |sse|, |post|, |names| and |disp|
        do not have the same length.
    WARNING
        If |replace| is not bool: |replace| set to False.

    """
    
    ####################################################################
    def _check_param(ts, vel, seas, ant, co, sw, sse, post, names, disp,
                     outdir_pos, outdir_fig, add_key, replace, warn):
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import adapt_shape, adapt_bool
        from itsa.gts.Gts import Gts
        from itsa.gts.errors import GtsError
        
        # Adapt shape
        (names, vel, seas, ant,
         co, sw, sse, post, disp) = adapt_shape([names, vel, seas, ant,
                                                 co, sw, sse, post, disp])
        if not isinstance(names, np.ndarray):
            names = np.array([names])
            vel = np.array([vel])
            seas = np.array([seas])
            ant = np.array([ant])
            co = np.array([co])
            sw = np.array([sw])
            sse = np.array([sse])
            post = np.array([post])
            disp = np.array([disp])
        
        # Check
        # |ts|
        if not isinstance(ts, Gts):
            raise TypeError('Time series must be Gts object: |type(ts)=%s|.'
                            % type(ts))        
        if ts.GMOD_names is None:
            raise GtsError(('Gts %s |GMOD_name| must be populated to write '
                            '|G| text file (look at [make_GMOD_names] in '
                            '[itsa.gts.lib.format.GMODfiles]).'))
        ts.check_gts()
        # |vel|
        if not isinstance(vel, np.ndarray):
            raise TypeError(('Velocity correction must be bool, list or '
                             'np.ndarray: |type(vel)=%s|.') % type(vel))
        if (vel.dtype != bool
            and not (vel.dtype == int and np.isin(vel, [0, 1]).all())):
            raise ValueError(('Velocity correction must be bool, list of bool '
                              'or bool np.ndarray: |vel.dtype=%s|.')
                             % vel.dtype)
        # |seas|
        if not isinstance(seas, np.ndarray):
            raise TypeError(('Seasonal correction must be bool, list or '
                             'np.ndarray: |type(seas)=%s|.') % type(seas))
        if (seas.dtype != bool
            and not (seas.dtype == int and np.isin(seas, [0, 1]).all())):
            raise ValueError(('Seasonal correction must be bool, list of bool '
                              'or bool np.ndarray: |seas.dtype=%s|.')
                             % seas.dtype)
        # |ant|
        if not isinstance(ant, np.ndarray):
            raise TypeError(('Antenna correction must be bool, list or '
                             'np.ndarray: |type(ant)=%s|.') % type(ant))
        if (ant.dtype != bool
            and not (ant.dtype == int and np.isin(ant, [0, 1]).all())):
            raise ValueError(('Antenna correction must be bool, list of bool '
                              'or bool np.ndarray: |ant.dtype=%s|.')
                             % ant.dtype)
        # |co|
        if not isinstance(co, np.ndarray):
            raise TypeError(('Co-seismic correction must be bool, list or '
                             'np.ndarray: |type(co)=%s|.') % type(co))
        if (co.dtype != bool
            and not (co.dtype == int and np.isin(co, [0, 1]).all())):
            raise ValueError(('Co-seismic correction must be bool, list of '
                              'bool or bool np.ndarray: |co.dtype=%s|.')
                             % co.dtype)
        # |sw|
        if not isinstance(sw, np.ndarray):
            raise TypeError(('Swarm correction must be bool, list or '
                             'np.ndarray: |type(sw)=%s|.') % type(sw))
        if (sw.dtype != bool
            and not (sw.dtype == int and np.isin(sw, [0, 1]).all())):
            raise ValueError(('Swarm correction must be bool, list of bool '
                              'or bool np.ndarray: |sw.dtype=%s|.')
                             % sw.dtype)
        # |sse|
        if not isinstance(sse, np.ndarray):
            raise TypeError(('SSE correction must be bool, list or '
                             'np.ndarray: |type(sse)=%s|.') % type(sse))
        if (sse.dtype != bool
            and not (sse.dtype == int and np.isin(sse, [0, 1]).all())):
            raise ValueError(('SSE correction must be bool, list of bool '
                              'or bool np.ndarray: |sse.dtype=%s|.')
                             % sse.dtype)
        # |post|
        if not isinstance(post, np.ndarray):
            raise TypeError(('Post-seismic correction must be bool, list or '
                             'np.ndarray: |type(post)=%s|.') % type(post))
        if (post.dtype != bool
            and not (post.dtype == int and np.isin(post, [0, 1]).all())):
            raise ValueError(('Post-seismic correction must be bool, list of '
                              'bool or bool np.ndarray: |post.dtype=%s|.')
                             % post.dtype)
        # |names|
        if not isinstance(names, np.ndarray):
            raise TypeError(('Names must be str, list or np.ndarray: '
                             '|type(names=%s|.') % type(names))
        if names.dtype != str and 'U' not in str(names.dtype):
            raise ValueError(('Names must be str, list of str or str '
                              'np.ndarray: |names.dtype=%s|.') % names.dtype)
        # |disp|
        if not isinstance(disp, np.ndarray):
            raise TypeError(('Display must be bool, list or np.ndarray: '
                             '|type(disp)=%s|.') % type(disp))
        if (disp.dtype != bool
            and not (disp.dtype == int and np.isin(disp, [0, 1]).all())):
            raise ValueError(('Display must be bool, list of bool or bool '
                              'np.ndarray: |disp.dtype=%s|.') % disp.dtype)
        # |outdir_pos|
        if not isinstance(outdir_pos, str):
            raise TypeError(('Pos file output directory must be str: '
                             '|type(outdir_pos)=%s|.') % type(outdir_pos))
        # |outdir_fig|
        if not isinstance(outdir_fig, str):
            raise TypeError(('Figure output directory must be str: '
                             '|type(outdir_fig)=%s|.') % type(outdir_fig))
        # |add_key|
        if not isinstance(add_key, str):
            raise TypeError(('Key name to add must be str: '
                             '|type(add_key)=%s|.') % type(add_key))
        
        # Check dimensions
        vel = vel.reshape(-1)
        seas = seas.reshape(-1)
        ant = ant.reshape(-1)
        co = co.reshape(-1)
        sw = sw.reshape(-1)
        sse = sse.reshape(-1)
        post = post.reshape(-1)
        names = names.reshape(-1)
        disp = disp.reshape(-1)
        # |vel|
        if len(vel) != len(names):
            raise ValueError(('Velocity correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(vel)=%d| and '
                              '|len(names)=%d|.') % (len(vel), len(names)))
        # |seas|
        if len(seas) != len(names):
            raise ValueError(('Seasonal correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(seas)=%d| and '
                              '|len(names)=%d|.') % (len(seas), len(names)))
        # |ant|
        if len(ant) != len(names):
            raise ValueError(('Antenna correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(ant)=%d| and '
                              '|len(names)=%d|.') % (len(ant), len(names)))
        # |co|
        if len(co) != len(names):
            raise ValueError(('Co-seismic correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(co)=%d| and '
                              '|len(names)=%d|.') % (len(co), len(names)))
        # |sw|
        if len(sw) != len(names):
            raise ValueError(('Swarm correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(sw)=%d| and '
                              '|len(names)=%d|.') % (len(sw), len(names)))
        # |sse|
        if len(sse) != len(names):
            raise ValueError(('SSE correction must be bool or have the '
                              'same number of values (list or np.ndarray) '
                              'then |names|: |len(sse)=%d| and '
                              '|len(names)=%d|.') % (len(sse), len(names)))
        # |post|
        if len(post) != len(names):
            raise ValueError(('Post-seismic correction must be bool or have '
                              'the same number of values (list or np.ndarray) '
                              'then |names|: |len(post)=%d| and '
                              '|len(names)=%d|.') % (len(post), len(names)))
        # |disp|
        if len(disp) != len(names):
            raise ValueError(('Display must be bool or have the same number '
                              'of values (list or np.ndarray) then |names|: '
                              '|len(disp)=%d| and |len(names)=%d|.')
                             % (len(disp), len(names)))
            
        # Adapt
        # |replace|
        (replace, warn_replace) = adapt_bool(replace)
        # |warn|
        (warn, _) = adapt_bool(warn, True)
        
        # Warning
        if warn and warn_replace:
            print('[WARNING] from method [save_byp] in [%s]' % __name__)
            print('\t|replace| set to False because |type(replace)!=bool|!')
            print('\tNo file will be replaced in the output directory!')
            
        # Return
        return vel, seas, ant, co, sw, sse, post, names, disp, replace
    ####################################################################
    
    # Check parameters
    (vel, seas, ant, co, sw, sse,
     post, names, disp, replace) = _check_param(ts, vel, seas, ant, co, sw,
                                                sse, post, names, disp,
                                                outdir_pos, outdir_fig,
                                                add_key, replace, warn)

    # Import
    import os
    import numpy as np
    
    # Loop on by-product
    for b in range(len(names)):
        
        # Bool of component to keep for the by-product
        MOD_keep = ts.GMOD_names == 'Cst'
        
        # Velocity (and acceleration) trend
        if vel[b]:
            MOD_vel = np.isin(ts.GMOD_names, ['Vel', 'Acc'])
            MOD_keep = MOD_keep | MOD_vel
            
        # Seasonal variation
        if seas[b]:
            MOD_seas = np.isin(ts.GMOD_names, ['An1', 'An2', 'Sm1', 'Sm2'])
            MOD_keep = MOD_keep | MOD_seas
         
        # Jps events
        MOD_jps = np.array(list(map(lambda x: x[0]=='J', ts.GMOD_names)))
        jps_keep = np.zeros(ts.jps.shape()).astype(bool)
        
        # Antenna changes
        if ant[b]:
            MOD_ant = np.array(list(map(lambda x: x[-1]=='A', ts.GMOD_names)))
            MOD_keep = MOD_keep | (MOD_jps & MOD_ant)
            jps_ant = ts.jps.type_ev == 'A'
            jps_keep = jps_keep | jps_ant
        
        # Co-seismic jumps
        if co[b]:
            MOD_co = np.array(list(map(lambda x: np.isin(x[-1],
                                                          ['E', 'P', 'U']),
                                        ts.GMOD_names)))
            MOD_keep = MOD_keep | (MOD_jps & MOD_co)
            jps_co = np.isin(ts.jps.type_ev, ['E', 'P', 'U'])
            jps_keep = jps_keep | jps_co
            
        # Swarm
        if sw[b]:
            MOD_sw = np.array(list(map(lambda x: x[-1]=='W', ts.GMOD_names)))
            MOD_keep = MOD_keep | (MOD_jps & MOD_sw)
            jps_sw = ts.jps.type_ev == 'W'
            jps_keep = jps_keep | jps_sw
            
        # SSE
        if sse[b]:
            MOD_sse = np.array(list(map(lambda x: x[-1]=='S', ts.GMOD_names)))
            MOD_keep = MOD_keep | (MOD_jps & MOD_sse)
            jps_sse = ts.jps.type_ev == 'S'
            jps_keep = jps_keep | jps_sse
            
        # Post-seismic effect
        if post[b]:
            MOD_post = np.array(list(map(lambda x: len(x)>11, ts.GMOD_names)))
            MOD_keep = MOD_keep | (MOD_jps & MOD_post)
            jps_post = ts.jps.type_ev == 'P'
            jps_keep = jps_keep | jps_post
            
        # Create new Gts
        ts_res = ts.copy(data_xyz=False, data_neu=False)
        ts_res.data[:, :3] = ts.data[:, :3]-np.dot(ts.G[:, MOD_keep],
                                                   ts.MOD[MOD_keep, :3])
        
        # Display new Gts?
        if disp[b]:
            # Raw data + Model
            # New Gts
            ts_byp = ts.copy(data_xyz=False, data_neu=False)
            # |G| and |MOD|
            ts_byp.G = ts.G[:, MOD_keep]
            ts_byp.MOD = ts.MOD[MOD_keep, :]
            ts_byp.GMOD_names = ts.GMOD_names[MOD_keep]
            # Jps
            ts_byp.jps = ts.jps.select_ev(jps_keep)
            if co[b] and not post[b]:
                ts_byp.jps.type_ev[ts_res.jps.type_ev=='P'] = 'E'
            # Display
            if not np.isin('Acc', ts_byp.GMOD_names):
                ts_byp.plot(title=('Station '+ts_byp.code+' - '+names[b]
                                   +' - Model'),
                            name_fig=ts_byp.code+'_data',
                            path_fig=outdir_fig+names[b]+os.sep, save_model=True, byp_code=names[b])
            else:
                ts_byp.plot(title=('Station '+ts_byp.code+' - '
                                   +names[b].split('_')[0]+' - Model'),
                            name_fig=ts_byp.code+'_data',
                            path_fig=outdir_fig+names[b]+os.sep, acc=True, save_model=True, byp_code=names[b])
            # Residuals
            # Jps
            ts_res.jps = ts_byp.jps.copy()
            # Re-initialisation of |G| and |MOD|
            ts_res.G = None
            # Display
            name_fig = ts_res.code+'_res'
            if add_key != '':
                name_fig += '_'+add_key
            if not np.isin('Acc', ts_byp.GMOD_names):
                ts_res.plot('green',
                            title=('Station '+ts_res.code+' - '+names[b]
                                   +' - Residuals'),
                            name_fig=name_fig,
                            path_fig=outdir_fig+names[b]+os.sep, size_marker=1)
            else:
                ts_res.plot('green',
                            title=('Station '+ts_res.code+' - '
                                   +names[b].split('_')[0]+' - Residuals'),
                            name_fig=name_fig,
                            path_fig=outdir_fig+names[b]+os.sep, size_marker=1,
                            acc=True)
        
        # Save residual Gts in PBO pos
        ts_res.write_PBOpos(outdir_pos+names[b], add_key=add_key,
                            replace=replace, warn=warn)
