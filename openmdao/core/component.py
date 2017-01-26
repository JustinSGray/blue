"""Define the Component class."""

from __future__ import division

import numpy

from openmdao.core.system import System


class Component(System):
    """Base Component class; not to be directly instantiated."""

    INPUT_DEFAULTS = {
        'shape': (1,),
        'units': '',
        'var_set': 0,
        'indices': None,
    }

    OUTPUT_DEFAULTS = {
        'shape': (1,),
        'units': '',
        'var_set': 0,
        'lower': None,
        'upper': None,
        'ref': 1.0,
        'ref0': 0.0,
        'res_units': '',
        'res_ref': 1.0,
        'res_ref0': 0.0,
    }

    def add_input(self, name, val=1.0, shape=None, indices=None, units='', var_set=0):
        """Add an input variable to the component.

        ==================================================  ===================================
        Examples of valid calls                             Initial value / notes
        ==================================================  ===================================
        add_input('name')                                   Scalar with value 1
        add_input('name', scalar)                           Scalar with value scalar
        add_input('name', array_like)                       Array with value array_like
        add_input('name', shape=shp)                        Constant array of ones
        add_input('name', indices=inds)                     Shape inferred from inds; all ones
        add_input('name', scalar, shape=shp)                Constant array with value scalar
        add_input('name', scalar, indices=inds)             Shape inferred from inds
        add_input('name', array_like, indices=inds)         Checks shapes of array & inds match
        ==================================================  ===================================

        Args
        ----
        name : str
            name of the variable in this component's namespace.
        val : float or list or tuple or ndarray
            The initial value of the variable being added in user-defined units. Default is 1.0.
        shape : int or tuple or list or None
            Shape of this variable, only required if indices not provided and val is not an array.
            Default is None.
        indices : int or list of ints or tuple of ints or int ndarray or None
            The indices of the source variable to transfer data from.
            If val is given as an array_like object, the shapes of val and indices must match.
            A value of None implies this input depends on all entries of source. Default is None.
        units : str
            Units in which this input variable will be provided to the component during execution.
            Default is '', which means it has no units.
        var_set : hashable object
            For advanced users only. ID or color for this variable, relevant for reconfigurability.
            Default is 0.
        """
        # First, type check all arguments
        if not isinstance(name, str):
            raise TypeError('The name argument should be a string')
        if not numpy.isscalar(val) and not isinstance(val, (list, tuple, numpy.ndarray)):
            raise TypeError('The val argument should be a float, list, tuple, or ndarray')
        if shape is not None and not isinstance(shape, (int, tuple, list)):
            raise TypeError('The shape argument should be an int, tuple, or list')
        if indices is not None and not isinstance(indices, (int, list, tuple, numpy.ndarray)):
            raise TypeError('The indices argument should be an int, list, tuple, or ndarray')
        if units != '' and not isinstance(units, str):
            raise TypeError('The units argument should be a str')

        if shape is not None:
            if isinstance(shape, int):
                shape = (shape,)
            elif isinstance(shape, list):
                shape = tuple(shape)
        # Next check that shapes are consistent
        if not numpy.isscalar(val):
            val_shape = numpy.atleast_1d(val).shape
            # 1. val and shape
            if shape is not None and val_shape != shape:
                raise ValueError('The val argument is an array, but val.shape != shape.')
            # 2. val and indices
            if indices is not None and val_shape != numpy.atleast_1d(indices).shape:
                raise ValueError('The val and indices are arrays, but val.shape != indices.shape.')
        if shape is not None:
            # 3. shape and indices
            if indices is not None and shape != numpy.atleast_1d(indices).shape:
                raise ValueError('The val argument is an array, but val.shape != indices.shape.')

        metadata = {}

        # val: taken as is
        metadata['value'] = val

        # shape: if not given, infer from val (if array) or indices, else assume scalar
        if shape is not None:
            metadata['shape'] = shape
        elif not numpy.isscalar(val):
            metadata['shape'] = numpy.atleast_1d(val).shape
        elif indices is not None:
            metadata['shape'] = numpy.atleast_1d(indices).shape
        else:
            metadata['shape'] = (1,)

        # indices: None or ndarray
        if indices is None:
            metadata['indices'] = None
        else:
            metadata['indices'] = numpy.atleast_1d(indices)

        # units: taken as is
        metadata['units'] = units

        # var_set: taken as is
        metadata['var_set'] = var_set

        self._var_allprocs_names['input'].append(name)
        self._var_myproc_names['input'].append(name)
        self._var_myproc_metadata['input'].append(metadata)

    def add_output(self, name, val=1.0, shape=None, units='', res_units='',
                   lower=None, upper=None, ref=1.0, ref0=0.0,
                   res_ref=1.0, res_ref0=0.0, var_set=0):
        """Add an output variable to the component.

        ==================================================  ===================================
        Examples of valid calls                             Initial value / notes
        ==================================================  ===================================
        add_output('name')                                  Scalar with value 1
        add_output('name', scalar)                          Scalar with value scalar
        add_output('name', array_like)                      Array with value array_like
        add_output('name', shape=shp)                       Constant array of ones
        add_output('name', scalar, shape=shp)               Constant array with value scalar
        ==================================================  ===================================

        Args
        ----
        name : str
            name of the variable in this component's namespace.
        val : float or list or tuple or ndarray
            The initial value of the variable being added in user-defined units. Default is 1.0.
        shape : int or tuple or list or None
            Shape of this variable, only required if indices not provided and val is not an array.
            Default is None.
        units : str
            Units in which the output variables will be provided to the component during execution.
            Default is '', which means it has no units.
        res_units : str
            Units in which the residuals of this output will be given to the user when requested.
            Default is '', which means it has no units.
        lower : float or list or tuple or ndarray or None
            lower bound(s) in user-defined units. It can be (1) a float, (2) an array_like
            consistent with the shape arg (if given), or (3) an array_like matching the shape of
            val, if val is array_like. A value of None means this output has no lower bound.
            Default is None.
        upper : float or list or tuple or ndarray or None
            upper bound(s) in user-defined units. It can be (1) a float, (2) an array_like
            consistent with the shape arg (if given), or (3) an array_like matching the shape of
            val, if val is array_like. A value of None means this output has no upper bound.
            Default is None.
        ref : float
            Scaling parameter. The value in the user-defined units of this output variable when
            the scaled value is 1. Default is 1.
        ref0 : float
            Scaling parameter. The value in the user-defined units of this output variable when
            the scaled value is 0. Default is 0.
        res_ref : float
            Scaling parameter. The value in the user-defined res_units of this output's residual
            when the scaled value is 1. Default is 1.
        res_ref0 : float
            Scaling parameter. The value in the user-defined res_units of this output's residual
            when the scaled value is 0. Default is 0.
        var_set : hashable object
            For advanced users only. ID or color for this variable, relevant for reconfigurability.
            Default is 0.
        """
        # First, type check all arguments
        if not isinstance(name, str):
            raise TypeError('The name argument should be a string')
        if not numpy.isscalar(val) and not isinstance(val, (list, tuple, numpy.ndarray)):
            raise TypeError('The val argument should be a float, list, tuple, or ndarray')
        if shape is not None and not isinstance(shape, (int, tuple, list)):
            raise TypeError('The shape argument should be an int, tuple, or list')
        if units != '' and not isinstance(units, str):
            raise TypeError('The units argument should be a str')
        if res_units != '' and not isinstance(res_units, str):
            raise TypeError('The res_units argument should be a str')
        if lower is not None and not numpy.isscalar(lower) and \
                not isinstance(lower, (list, tuple, numpy.ndarray)):
            raise TypeError('The lower argument should be a float, list, tuple, or ndarray')
        if upper is not None and not numpy.isscalar(upper) and \
                not isinstance(upper, (list, tuple, numpy.ndarray)):
            raise TypeError('The upper argument should be a float, list, tuple, or ndarray')
        for item in [ref, ref0, res_ref, res_ref]:
            if not numpy.isscalar(item):
                raise TypeError('The %s argument should be a float' % (item.__name__))

        if shape is not None:
            if isinstance(shape, int):
                shape = (shape,)
            elif isinstance(shape, list):
                shape = tuple(shape)
        # Next check that shapes are consistent between val and shape, if necessary
        if not numpy.isscalar(val):
            if shape is not None and numpy.atleast_1d(val).shape != shape:
                raise ValueError('The val argument is an array, but val.shape != shape.')

        metadata = {}

        # val: taken as is
        metadata['value'] = val

        # shape: if not given, infer from val (if array) or indices, else assume scalar
        if shape is not None:
            metadata['shape'] = shape
        elif not numpy.isscalar(val):
            metadata['shape'] = numpy.atleast_1d(val).shape
        else:
            metadata['shape'] = (1,)

        # units, res_units: taken as is
        metadata['units'] = units
        metadata['res_units'] = res_units

        # lower, upper: check the shape if necessary
        if lower is not None and not numpy.isscalar(lower) and \
                numpy.atleast_1d(lower).shape != metadata['shape']:
            raise ValueError('The lower argument has the wrong shape')
        if upper is not None and not numpy.isscalar(upper) and \
                numpy.atleast_1d(upper).shape != metadata['shape']:
            raise ValueError('The upper argument has the wrong shape')
        metadata['lower'] = lower
        metadata['upper'] = upper

        # ref, ref0, res_ref, res_ref0: taken as is
        metadata['ref'] = ref
        metadata['ref0'] = ref0
        metadata['res_ref'] = res_ref
        metadata['res_ref0'] = res_ref0

        # var_set: taken as is
        metadata['var_set'] = var_set

        self._var_allprocs_names['output'].append(name)
        self._var_myproc_names['output'].append(name)
        self._var_myproc_metadata['output'].append(metadata)

    def _setup_vector(self, vectors, vector_var_ids, use_ref_vector):
        r"""Add this vector and assign sub_vectors to subsystems.

        Sets the following attributes:

        - _vectors
        - _vector_transfers
        - _inputs*
        - _outputs*
        - _residuals*
        - _transfers*

        \* If vec_name is 'nonlinear'

        Args
        ----
        vectors : {'input': <Vector>, 'output': <Vector>, 'residual': <Vector>}
            <Vector> objects corresponding to 'name'.
        vector_var_ids : ndarray[:]
            integer array of all relevant variables for this vector.
        use_ref_vector : bool
            if True, allocate vectors to store ref. values.
        """
        super(Component, self)._setup_vector(vectors, vector_var_ids,
                                             use_ref_vector)

        # Components must load their initial input and output values into the
        # vectors.

        # Note: It's possible for meta['value'] to not match
        #       meta['shape'], and input and output vectors are sized according
        #       to shape, so if, for example, value is not specified it
        #       defaults to 1.0 and the shape can be anything, resulting in the
        #       value of 1.0 being broadcast into all values in the vector
        #       that were allocated according to the shape.
        if vectors['input']._name is 'nonlinear':
            names = self._var_myproc_names['input']
            inputs = self._inputs
            for i, meta in enumerate(self._var_myproc_metadata['input']):
                inputs[names[i]] = meta['value']

        if vectors['output']._name is 'nonlinear':
            names = self._var_myproc_names['output']
            outputs = self._outputs
            for i, meta in enumerate(self._var_myproc_metadata['output']):
                outputs[names[i]] = meta['value']
