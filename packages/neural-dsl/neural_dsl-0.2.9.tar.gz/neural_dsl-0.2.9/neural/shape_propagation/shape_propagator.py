import logging
import json
import time
import torch
import numpy as np
import psutil
import plotly.graph_objects as go
from graphviz import Digraph
from typing import Dict, Tuple, Optional, Any, List, Union, Callable

import sys
import os

# Add the parent directory of 'neural' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser.parser import ModelTransformer
from pretrained_models.pretrained import PretrainedModelHub
from .utils import extract_param, calculate_output_dims, detect_shape_issues, suggest_optimizations
from .utils import format_error_message, calculate_memory_usage, format_memory_size
from .layer_docs import get_layer_documentation, format_layer_documentation
from .layer_handlers import (
    handle_conv1d, handle_conv3d, handle_lstm, handle_dropout,
    handle_batch_normalization, handle_concatenate, handle_add,
    handle_global_average_pooling1d, handle_reshape, handle_permute,
    handle_zero_padding2d, handle_cropping2d
)

class PerformanceMonitor:
    def __init__(self):
        self.resource_history = []

    def monitor_resources(self):
        """Monitor CPU, memory, and GPU usage."""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        gpu_memory = 0
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / (1024 ** 3)  # GB
        io_counters = psutil.disk_io_counters()
        io_usage = (io_counters.read_bytes + io_counters.write_bytes) / (1024 ** 2)  # MB

        self.resource_history.append({
            "timestamp": time.time(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "gpu_memory": gpu_memory,
            "io_usage": io_usage
        })
        return self.resource_history[-1]


class ShapePropagator:
    # Registry for external layer handlers
    LAYER_HANDLERS = {}

    @classmethod
    def register_layer_handler(cls, layer_type):
        """Decorator to register layer handlers dynamically.

        Args:
            layer_type: Type of layer to register handler for

        Returns:
            Decorator function
        """
        def decorator(func):
            cls.LAYER_HANDLERS[layer_type] = func
            return func
        return decorator

    def __init__(self, debug=False):
        self.debug = debug
        self.shape_history = []
        self.layer_connections = []
        self.current_layer = 0
        self.execution_trace = []  # Stores nntrace logs
        self.performance_monitor = PerformanceMonitor()
        self.hub = PretrainedModelHub()
        self.issues = []  # Store detected issues
        self.optimizations = []  # Store optimization suggestions

        # Framework compatibility mappings
        self.param_aliases = {
            'Conv2D': {'filters': 'out_channels', 'kernel_size': 'kernel_size'},
            'BatchNormalization': {'axis': 'dim'},
            'Dense': {'units': 'out_features'},
            'LSTM': {'units': 'hidden_size'},
            'BatchNormalization': {'momentum': 'decay'}
        }

        # Initialize visualization
        self.dot = Digraph(comment='Neural Network Architecture')
        self.dot.attr('node', shape='record', style='filled', fillcolor='lightgrey')

    def propagate(self, input_shape: Tuple[Optional[int], ...],
              layer: Dict[str, Any],
              framework: str = 'tensorflow') -> Tuple[Optional[int], ...]:
        """Processes a layer and logs shape changes for nntrace."""
        # Validate layer has a type
        if "type" not in layer:
            raise KeyError("Layer must have a 'type' field")

        layer_type = layer["type"]
        params = layer.get("params", {})

        # Debug logging
        print(f"DEBUG: ShapePropagator.propagate - input_shape: {input_shape}, layer_type: {layer_type}")
        print(f"DEBUG: ShapePropagator.propagate - params: {params}")

        # Validate input shape
        if not input_shape:
            raise ValueError("Input shape cannot be empty")

        # Check for negative dimensions in input shape
        if any(dim is not None and dim < 0 for dim in input_shape):
            raise ValueError(f"Input shape cannot contain negative dimensions: {input_shape}")

        # Validate layer parameters based on layer type
        self._validate_layer_params(layer_type, params, input_shape)

        # Only set kernel_size for layers that need it
        if layer_type in ['Conv2D', 'MaxPooling2D']:  # Add other layers as needed
            kernel_size = params.get("kernel_size", 3)
            if isinstance(kernel_size, int):
                kernel_size = (kernel_size, kernel_size)
            elif isinstance(kernel_size, list):
                kernel_size = tuple(kernel_size)
            elif isinstance(kernel_size, dict):
                print(f"DEBUG: ShapePropagator.propagate - kernel_size is a dict: {kernel_size}")
                # If it's a dictionary with a 'value' key, use that value
                if 'value' in kernel_size:
                    kernel_size = (kernel_size['value'], kernel_size['value'])
                # Otherwise, use a default value
                else:
                    print(f"DEBUG: ShapePropagator.propagate - kernel_size dict without 'value' key, using default")
                    kernel_size = (3, 3)  # Default value
            params["kernel_size"] = kernel_size  # Ensure tuple in params

        if layer['type'] == 'TransformerEncoder':
            if framework == 'tensorflow':
                return input_shape  # Shape preserved through self-attention
            elif framework == 'pytorch':
                return (input_shape[0], input_shape[1])  # (seq_len, d_model)

        start_time = time.time()  # Measure execution time

        output_shape = self._process_layer(input_shape, layer, framework)
        prev_layer = self.current_layer - 1 if self.current_layer > 0 else None

        # Compute FLOPs, memory, compute_time, and transfer_time
        flops, mem_usage, compute_time, transfer_time = self._compute_performance(layer, input_shape, output_shape)

        # Capture nntrace log with additional timing details
        trace_entry = {
            "layer": layer_type,
            "input_shape": input_shape,
            "output_shape": output_shape,
            "flops": flops,
            "memory": mem_usage,
            "execution_time": time.time() - start_time,
            "compute_time": compute_time,
            "transfer_time": transfer_time,
        }
        self.execution_trace.append(trace_entry)

        resources = self.performance_monitor.monitor_resources()
        trace_entry.update({
            "cpu_usage": resources["cpu_usage"],
            "memory_usage": resources["memory_usage"],
            "gpu_memory": resources["gpu_memory"],
            "io_usage": resources["io_usage"]
        })

        if self.debug:
            print(f"TRACE: {trace_entry}")  # Debugging output

        self._visualize_layer(layer['type'], output_shape)  # Creates node and increments self.current_layer
        if prev_layer is not None:
            self._create_connection(prev_layer, self.current_layer - 1)  # Connect previous to current
        return output_shape

###############################
### Performance Computation ###
###############################

    def _compute_performance(self, layer: dict, input_shape: tuple, output_shape: tuple) -> tuple:
        """Compute performance metrics (FLOPs, memory usage, etc.)."""
        # Replace None with 1 to avoid NoneType math errors
        input_shape = tuple(1 if dim is None else dim for dim in input_shape)
        output_shape = tuple(1 if dim is None else dim for dim in output_shape)

        # FLOPs calculation (example for Conv2D)
        if layer['type'] == 'Conv2D':
            kernel_size = layer['params']['kernel_size']
            filters = layer['params']['filters']
            flops = np.prod(kernel_size) * np.prod(output_shape) * input_shape[-1]
        else:
            flops = 0  # Default for other layers

        # Memory usage (output tensor size in MB)
        memory_usage = np.prod(output_shape) * 4 / (1024 ** 2)  # 4 bytes per float

        # Simplified timing estimates
        compute_time = flops / 1e9  # 1 GFLOP/s
        transfer_time = memory_usage * 1e3 / 1e9  # 1 GB/s

        return flops, memory_usage, compute_time, transfer_time

##################################################
### Send execution trace data to the dashboard ###
##################################################
    def get_trace(self):
        trace = []
        for entry in self.execution_trace:
            # Check if entry is a dictionary (new format) or a tuple (old format)
            if isinstance(entry, dict):
                # New format: entry is a dictionary
                layer_type = entry.get("layer", "Unknown")
                exec_time = entry.get("execution_time", 0)
                comp_time = entry.get("compute_time", 0)
                trans_time = entry.get("transfer_time", 0)
                flops = entry.get("flops", 0)
                memory = entry.get("memory", 0)

                # Default values for missing fields
                grad_norm = 0
                dead_ratio = 0
                mean_act = 0
                anomaly = False

                # Get kernel_size from params if available
                params = entry.get("params", {})
                if not params:
                    # Try to extract kernel_size directly from the entry
                    kernel_size = entry.get("kernel_size", (1, 1))
                else:
                    kernel_size = params.get("kernel_size", (1, 1))
            else:
                # Old format: entry is a tuple
                try:
                    layer_type, exec_time, comp_time, trans_time, params, flops, memory, grad_norm, dead_ratio, mean_act, anomaly = entry
                except ValueError:
                    print(f"WARNING: Invalid trace entry format: {entry}")
                    continue

                kernel_size = params.get("kernel_size", (1, 1)) if isinstance(params, dict) else (1, 1)

            # Ensure kernel_size is a tuple
            if isinstance(kernel_size, list):
                print(f"WARNING: Converting list kernel_size {kernel_size} to tuple for {layer_type}")
                kernel_size = tuple(kernel_size)
            elif not isinstance(kernel_size, tuple):
                print(f"WARNING: Unexpected kernel_size type {type(kernel_size)} for {layer_type}, defaulting to (1, 1)")
                kernel_size = (1, 1)

            trace.append({
                "layer": layer_type, "execution_time": exec_time, "compute_time": comp_time,
                "transfer_time": trans_time, "kernel_size": kernel_size,
                "flops": flops, "memory": memory, "grad_norm": grad_norm, "dead_ratio": dead_ratio,
                "mean_activation": mean_act, "anomaly": anomaly
            })

        return trace

    def _process_layer(self, input_shape, layer, framework):
        """Process a layer and calculate its output shape.

        Args:
            input_shape: Input tensor shape
            layer: Layer definition
            framework: Framework (tensorflow or pytorch)

        Returns:
            Output tensor shape
        """
        layer_type = layer['type']
        params = self._standardize_params(layer.get('params', {}), layer_type, framework)

        # Check for registered external handlers first
        if layer_type in self.LAYER_HANDLERS:
            return self.LAYER_HANDLERS[layer_type](self, input_shape, params)

        # Then check for internal handlers
        handler_name = f"_handle_{layer_type.lower()}"
        if hasattr(self, handler_name):
            output_shape = getattr(self, handler_name)(input_shape, params)
        else:
            # Try to use imported handlers
            if layer_type == 'Conv1D':
                output_shape = handle_conv1d(input_shape, params)
            elif layer_type == 'Conv3D':
                output_shape = handle_conv3d(input_shape, params)
            elif layer_type == 'LSTM':
                output_shape = handle_lstm(input_shape, params)
            elif layer_type == 'Dropout':
                output_shape = handle_dropout(input_shape, params)
            elif layer_type == 'BatchNormalization':
                output_shape = handle_batch_normalization(input_shape, params)
            elif layer_type == 'Reshape':
                output_shape = handle_reshape(input_shape, params)
            elif layer_type == 'Permute':
                output_shape = handle_permute(input_shape, params)
            elif layer_type == 'ZeroPadding2D':
                output_shape = handle_zero_padding2d(input_shape, params)
            elif layer_type == 'Cropping2D':
                output_shape = handle_cropping2d(input_shape, params)
            elif layer_type == 'GlobalAveragePooling1D':
                output_shape = handle_global_average_pooling1d(input_shape, params)
            else:
                # Fall back to default handler
                output_shape = self._handle_default(input_shape, params)

        return output_shape

    def _standardize_params(self, params, layer_type, framework):
        # Ensure params is a dict, even if None is passed
        if params is None:
            params = {}
        standardized = {}
        aliases = self.param_aliases.get(layer_type, {})
        for k, v in params.items():
            if framework == 'pytorch' and k in aliases.values():
                standardized[aliases[k]] = v
            else:
                standardized[k] = v
        standardized.setdefault('data_format', 'channels_first' if framework == 'pytorch' else 'channels_last')
        return standardized

    def _validate_layer_params(self, layer_type, params, input_shape):
        """Validate layer parameters based on layer type."""
        # Validate based on layer type
        if layer_type == 'Conv2D':
            # Check if filters parameter exists
            if 'filters' not in params:
                raise ValueError(f"Conv2D layer requires filters parameter")

            # Check if filters is positive
            filters = params.get('filters')
            if isinstance(filters, dict):
                if 'value' in filters:
                    filters = filters['value']
            if filters is not None and isinstance(filters, (int, float)) and filters <= 0:
                raise ValueError(f"Conv2D filters must be a positive integer, got {filters}")

            # Check if kernel_size parameter exists
            if 'kernel_size' not in params:
                raise ValueError(f"Conv2D layer requires kernel_size parameter")

            # Check if kernel_size is valid
            kernel_size = params.get('kernel_size')
            if isinstance(kernel_size, dict):
                if 'value' in kernel_size:
                    kernel_size = kernel_size['value']
            if isinstance(kernel_size, int):
                kernel_size = (kernel_size, kernel_size)
            if isinstance(kernel_size, tuple) and len(input_shape) >= 3:
                # Check if kernel size exceeds input dimensions
                if data_format := params.get('data_format'):
                    if data_format == 'channels_first':
                        spatial_dims = input_shape[2:4]
                    else:
                        spatial_dims = input_shape[1:3]
                else:
                    spatial_dims = input_shape[1:3]  # Default to channels_last

                if len(spatial_dims) >= 2 and len(kernel_size) >= 2:
                    if kernel_size[0] > spatial_dims[0] or kernel_size[1] > spatial_dims[1]:
                        raise ValueError(f"Conv2D kernel size {kernel_size} exceeds input dimensions {spatial_dims}")

            # Check if stride is positive
            stride = params.get('stride')
            if isinstance(stride, dict):
                if 'value' in stride:
                    stride = stride['value']
            if stride is not None and isinstance(stride, (int, float)) and stride <= 0:
                raise ValueError(f"Conv2D stride must be a positive integer, got {stride}")

        elif layer_type == 'Dense':
            # Check if units parameter exists and is positive
            if 'units' not in params:
                raise ValueError(f"Dense layer requires units parameter")

            units = params.get('units')
            if isinstance(units, dict):
                if 'value' in units:
                    units = units['value']
            if units is not None and isinstance(units, (int, float)) and units <= 0:
                raise ValueError(f"Dense units must be a positive integer, got {units}")

            # Check if input shape is valid for Dense layer (2D)
            if len(input_shape) > 2:
                raise ValueError(f"Dense layer expects 2D input (batch, features), got {len(input_shape)}D: {input_shape}")

        elif layer_type == 'MaxPooling2D':
            # Check if pool_size parameter exists
            if 'pool_size' not in params:
                raise ValueError(f"MaxPooling2D layer requires pool_size parameter")

            # Check if pool_size is valid
            pool_size = params.get('pool_size')
            if isinstance(pool_size, dict):
                if 'value' in pool_size:
                    pool_size = pool_size['value']
            if isinstance(pool_size, int):
                pool_size = (pool_size, pool_size)
            if isinstance(pool_size, tuple) and len(input_shape) >= 3:
                # Check if pool_size exceeds input dimensions
                if data_format := params.get('data_format'):
                    if data_format == 'channels_first':
                        spatial_dims = input_shape[2:4]
                    else:
                        spatial_dims = input_shape[1:3]
                else:
                    spatial_dims = input_shape[1:3]  # Default to channels_last

                if len(spatial_dims) >= 2 and len(pool_size) >= 2:
                    if pool_size[0] > spatial_dims[0] or pool_size[1] > spatial_dims[1]:
                        raise ValueError(f"MaxPooling2D pool_size {pool_size} exceeds input dimensions {spatial_dims}")

            # Check if stride is positive
            stride = params.get('stride')
            if isinstance(stride, dict):
                if 'value' in stride:
                    stride = stride['value']
            if stride is not None and isinstance(stride, (int, float)) and stride <= 0:
                raise ValueError(f"MaxPooling2D stride must be a positive integer, got {stride}")

        elif layer_type == 'Output':
            # Check if units parameter exists and is positive
            if 'units' not in params:
                raise ValueError(f"Output layer requires units parameter")

            units = params.get('units')
            if isinstance(units, dict):
                if 'value' in units:
                    units = units['value']
            if units is not None and isinstance(units, (int, float)) and units <= 0:
                raise ValueError(f"Output units must be a positive integer, got {units}")

            # Check if input shape is valid for Output layer (2D)
            if len(input_shape) > 2:
                raise ValueError(f"Output layer expects 2D input (batch, features), got {len(input_shape)}D: {input_shape}")

####################################################################
### Shape propagation through 2 Dimensional Convolutional Layers ###
####################################################################

    def _handle_conv2d(self, input_shape, params):
        print(f"DEBUG: _handle_conv2d - input_shape: {input_shape}, params: {params}")
        data_format = params['data_format']  # 'channels_first' for PyTorch
        if data_format == 'channels_first':
            spatial_dims = input_shape[2:]  # Should be (28, 28)
        else:
            spatial_dims = input_shape[1:3]

        print(f"DEBUG: _handle_conv2d - spatial_dims: {spatial_dims}")

        kernel = params['kernel_size']
        if isinstance(kernel, int):
            kernel = (kernel, kernel)
        elif isinstance(kernel, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in kernel:
                kernel_value = kernel['value']
                if isinstance(kernel_value, int):
                    kernel = (kernel_value, kernel_value)
                else:
                    kernel = (3, 3)  # Default value
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_conv2d - kernel is a dict without 'value' key: {kernel}, using default")
                kernel = (3, 3)  # Default value
        elif not isinstance(kernel, tuple):
            print(f"DEBUG: _handle_conv2d - Invalid kernel_size type: {type(kernel)}, value: {kernel}, using default")
            kernel = (3, 3)  # Default value

        stride = params.get('stride', 1)
        # Handle dictionary values in stride
        if isinstance(stride, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in stride:
                stride = stride['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_conv2d - stride is a dict without 'value' key: {stride}, using default")
                stride = 1  # Default value

        padding = self._calculate_padding(params, input_shape[2] if data_format == 'channels_first' else input_shape[1])

        if isinstance(padding, int):
            padding = (padding,) * len(spatial_dims)
        elif isinstance(padding, (list, tuple)):
            padding = tuple(padding)
        elif isinstance(padding, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in padding:
                padding_value = padding['value']
                if isinstance(padding_value, int):
                    padding = (padding_value,) * len(spatial_dims)
                else:
                    padding = (0,) * len(spatial_dims)  # Default value
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_conv2d - padding is a dict without 'value' key: {padding}, using default")
                padding = (0,) * len(spatial_dims)  # Default value

        print(f"DEBUG: _handle_conv2d - kernel: {kernel}, stride: {stride}, padding: {padding}")

        output_spatial = [
            (dim + 2*pad - k) // stride + 1
            for dim, k, pad in zip(spatial_dims, kernel, padding)
        ]
        if any(dim <= 0 for dim in output_spatial):
            print(f"DEBUG: _handle_conv2d - Invalid Conv2D output dimensions: {output_spatial}, using default")
            output_spatial = [1, 1]  # Default value to avoid errors

        filters = params['filters']
        # Handle dictionary values in filters
        if isinstance(filters, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in filters:
                filters = filters['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_conv2d - filters is a dict without 'value' key: {filters}, using default")
                filters = 32  # Default value

        print(f"DEBUG: _handle_conv2d - output_spatial: {output_spatial}, filters: {filters}")

        if data_format == 'channels_first':
            return (input_shape[0], filters, *output_spatial)
        else:
            return (input_shape[0], *output_spatial, filters)

    def _handle_maxpooling2d(self, input_shape, params):
        print(f"DEBUG: _handle_maxpooling2d - input_shape: {input_shape}, params: {params}")
        data_format = params.get('data_format', 'channels_last')
        pool_size = params['pool_size']

        # Handle dictionary values in pool_size
        if isinstance(pool_size, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in pool_size:
                pool_value = pool_size['value']
                if isinstance(pool_value, int):
                    pool_size = pool_value
                else:
                    pool_size = 2  # Default value
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_maxpooling2d - pool_size is a dict without 'value' key: {pool_size}, using default")
                pool_size = 2  # Default value

        stride = params.get('stride', pool_size)

        # Handle dictionary values in stride
        if isinstance(stride, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in stride:
                stride = stride['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_maxpooling2d - stride is a dict without 'value' key: {stride}, using default")
                stride = pool_size  # Default to pool_size

        # Handle stride as tuple or integer
        if isinstance(stride, (tuple, list)):
            stride_h, stride_w = stride
        else:
            stride_h = stride_w = stride

        print(f"DEBUG: _handle_maxpooling2d - pool_size: {pool_size}, stride_h: {stride_h}, stride_w: {stride_w}")

        # Calculate spatial dimensions based on data format
        if data_format == 'channels_last':
            # TensorFlow: input_shape = (batch, height, width, channels)
            if len(input_shape) >= 4:  # Ensure we have enough dimensions
                new_height = input_shape[1] // stride_h
                new_width = input_shape[2] // stride_w
                return (input_shape[0], new_height, new_width, input_shape[3])
            else:
                print(f"DEBUG: _handle_maxpooling2d - Invalid input shape: {input_shape}, using default")
                return (input_shape[0], 1, 1, input_shape[-1] if len(input_shape) > 1 else 1)
        else:
            # PyTorch: input_shape = (batch, channels, height, width)
            if len(input_shape) >= 4:  # Ensure we have enough dimensions
                new_height = input_shape[2] // stride_h
                new_width = input_shape[3] // stride_w
                return (input_shape[0], input_shape[1], new_height, new_width)
            else:
                print(f"DEBUG: _handle_maxpooling2d - Invalid input shape: {input_shape}, using default")
                return (input_shape[0], input_shape[1] if len(input_shape) > 1 else 1, 1, 1)

    def _handle_flatten(self, input_shape, params):
        # If there is a batch dimension, keep it.
        if len(input_shape) >= 1:
            batch = input_shape[0]
            # Multiply all dimensions after the batch dimension
            flattened = np.prod(input_shape[1:])
            return (batch, flattened)
        else:
            return (np.prod(input_shape),)


    def _handle_dense(self, input_shape, params):
        print(f"DEBUG: _handle_dense - input_shape: {input_shape}, params: {params}")

        # Get units parameter with proper handling of dictionary values
        units = params.get('units', 64)  # Default to 64 if not provided

        # Handle dictionary values in units
        if isinstance(units, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in units:
                units = units['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_dense - units is a dict without 'value' key: {units}, using default")
                units = 64  # Default value

        print(f"DEBUG: _handle_dense - units after processing: {units}")

        # If input_shape has two or more dimensions, preserve the batch dimension.
        if len(input_shape) >= 2:
            return (input_shape[0], units)
        else:
            return (units,)

    def _handle_output(self, input_shape, params):
        print(f"DEBUG: _handle_output - input_shape: {input_shape}, params: {params}")

        # Get units parameter with proper handling of dictionary values
        units = params.get('units', 10)  # Default to 10 if not provided

        # Handle dictionary values in units
        if isinstance(units, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in units:
                units = units['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_output - units is a dict without 'value' key: {units}, using default")
                units = 10  # Default value

        print(f"DEBUG: _handle_output - units after processing: {units}")

        # Preserves the batch dimension and converts the feature dimension to the number of output units.
        if len(input_shape) >= 2:
            return (input_shape[0], units)
        else:
            return (units,)

    def _handle_globalaveragepooling2d(self, input_shape, params):
        print(f"DEBUG: _handle_globalaveragepooling2d - input_shape: {input_shape}, params: {params}")
        data_format = params.get('data_format', 'channels_last')

        # For GlobalAveragePooling2D, we reduce the spatial dimensions and keep only batch and channels
        if data_format == 'channels_last':
            # TensorFlow: input_shape = (batch, height, width, channels)
            if len(input_shape) >= 4:
                return (input_shape[0], input_shape[3])
            else:
                print(f"DEBUG: _handle_globalaveragepooling2d - Invalid input shape: {input_shape}, using default")
                return (input_shape[0], input_shape[-1] if len(input_shape) > 1 else 1)
        else:
            # PyTorch: input_shape = (batch, channels, height, width)
            if len(input_shape) >= 4:
                return (input_shape[0], input_shape[1])
            else:
                print(f"DEBUG: _handle_globalaveragepooling2d - Invalid input shape: {input_shape}, using default")
                return (input_shape[0], input_shape[1] if len(input_shape) > 1 else 1)

    def _handle_upsampling2d(self, input_shape, params):
        print(f"DEBUG: _handle_upsampling2d - input_shape: {input_shape}, params: {params}")
        data_format = params.get('data_format', 'channels_last')
        size = params.get('size', (2, 2))

        # Handle size parameter
        if isinstance(size, int):
            size = (size, size)
        elif isinstance(size, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in size:
                size_value = size['value']
                if isinstance(size_value, int):
                    size = (size_value, size_value)
                else:
                    size = (2, 2)  # Default value
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _handle_upsampling2d - size is a dict without 'value' key: {size}, using default")
                size = (2, 2)  # Default value

        print(f"DEBUG: _handle_upsampling2d - size after processing: {size}")

        # Calculate new spatial dimensions
        if data_format == 'channels_last':
            # TensorFlow: input_shape = (batch, height, width, channels)
            if len(input_shape) >= 4:
                new_height = input_shape[1] * size[0]
                new_width = input_shape[2] * size[1]
                return (input_shape[0], new_height, new_width, input_shape[3])
            else:
                print(f"DEBUG: _handle_upsampling2d - Invalid input shape: {input_shape}, using default")
                return input_shape
        else:
            # PyTorch: input_shape = (batch, channels, height, width)
            if len(input_shape) >= 4:
                new_height = input_shape[2] * size[0]
                new_width = input_shape[3] * size[1]
                return (input_shape[0], input_shape[1], new_height, new_width)
            else:
                print(f"DEBUG: _handle_upsampling2d - Invalid input shape: {input_shape}, using default")
                return input_shape

    # Handle default helper
    def _handle_default(self, input_shape, params):
        # Default handler for unsupported layers
        return input_shape

    ### Padding detection, extraction and calculation ###
    def _calculate_padding(self, params, input_dim):
        """Calculates padding based on provided parameters and input dimension.

        This method handles different padding types: integer, list, or string.
        It returns the appropriate padding value based on the input.

        Args:
            params (dict): Layer parameters containing padding information.
            input_dim (int): Input dimension.

        Returns:
            int or tuple or list: Calculated padding value.
        """
        print(f"DEBUG: _calculate_padding - params: {params}, input_dim: {input_dim}")
        padding = params.get('padding', 0)

        # Handle dictionary values in padding
        if isinstance(padding, dict):
            # If it's a dictionary with a 'value' key, use that value
            if 'value' in padding:
                padding = padding['value']
            # Otherwise, use a default value
            else:
                print(f"DEBUG: _calculate_padding - padding is a dict without 'value' key: {padding}, using default")
                padding = 0  # Default value

        if isinstance(padding, int):
            return padding
        elif isinstance(padding, (list, tuple)):
            return tuple(padding)
        elif padding == 'same':
            # Handle kernel_size as tuple or integer
            kernel = params['kernel_size']
            if isinstance(kernel, int):
                return (kernel - 1) // 2
            elif isinstance(kernel, dict):
                # If it's a dictionary with a 'value' key, use that value
                if 'value' in kernel:
                    kernel_value = kernel['value']
                    if isinstance(kernel_value, int):
                        return (kernel_value - 1) // 2
                    else:
                        return 1  # Default value
                # Otherwise, use a default value
                else:
                    print(f"DEBUG: _calculate_padding - kernel is a dict without 'value' key: {kernel}, using default")
                    return 1  # Default value
            elif isinstance(kernel, tuple):
                # Process each dimension
                return tuple((k - 1) // 2 for k in kernel)
            else:
                print(f"DEBUG: _calculate_padding - Invalid kernel type: {type(kernel)}, value: {kernel}, using default")
                return 1  # Default value
        elif padding == 'valid':
            return 0
        else:
            return [padding] * (input_dim - 2)

    ### Layers Shape Propagation Visualization ###
    def _visualize_layer(self, layer_name, shape):
        label = f"{layer_name}\n{shape}"
        self.dot.node(str(self.current_layer), label)
        self.shape_history.append((layer_name, shape))
        self.current_layer += 1

    def _create_connection(self, from_id, to_id):
        self.layer_connections.append((from_id, to_id))
        self.dot.edge(str(from_id), str(to_id))

    def generate_report(self):
        """Generate interactive visualization and shape report"""
        # Plotly visualization
        fig = go.Figure()

        # Add shape dimensions as bar chart
        shapes = [str(s[1]) for s in self.shape_history]
        fig.add_trace(go.Bar(
            x=[s[0] for s in self.shape_history],
            y=[np.prod(s[1]) for s in self.shape_history],
            text=shapes,
            name='Parameter Count'
        ))

        fig.update_layout(
            title='Network Shape Propagation',
            xaxis_title='Layer',
            yaxis_title='Parameters',
            template='plotly_white'
        )

        # Detect shape issues and optimization opportunities
        self.issues = detect_shape_issues(self.shape_history)
        self.optimizations = suggest_optimizations(self.shape_history)

        return {
            'dot_graph': self.dot,
            'plotly_chart': fig,
            'shape_history': self.shape_history,
            'issues': self.issues,
            'optimizations': self.optimizations
        }

    def get_shape_data(self):
        """Returns shape history as JSON."""
        import json
        return json.dumps([
            {"layer": layer[0], "output_shape": layer[1]}
            for layer in self.shape_history
        ])

    def get_layer_documentation(self, layer_type):
        """Get documentation for a specific layer type.

        Args:
            layer_type: Type of layer to get documentation for

        Returns:
            Dictionary with layer documentation
        """
        return get_layer_documentation(layer_type)

    def format_layer_documentation(self, layer_type):
        """Format documentation for a specific layer type as a readable string.

        Args:
            layer_type: Type of layer to format documentation for

        Returns:
            Formatted documentation string
        """
        return format_layer_documentation(layer_type)

    def detect_issues(self):
        """Detect potential issues in the model architecture.

        Returns:
            List of detected issues
        """
        self.issues = detect_shape_issues(self.shape_history)
        return self.issues

    def suggest_optimizations(self):
        """Suggest optimizations for the model architecture.

        Returns:
            List of optimization suggestions
        """
        self.optimizations = suggest_optimizations(self.shape_history)
        return self.optimizations

    def generate_interactive_visualization(self):
        """Generate an interactive HTML visualization of the model architecture.

        Returns:
            Plotly figure object
        """
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Create figure with subplots
        fig = make_subplots(rows=2, cols=1,
                            subplot_titles=("Tensor Dimensions", "Memory Usage"),
                            specs=[[{"type": "scatter"}], [{"type": "bar"}]])

        # Add tensor dimension trace
        layer_names = [layer[0] for layer in self.shape_history]
        tensor_sizes = [np.prod([dim for dim in shape if dim is not None])
                       for _, shape in self.shape_history]

        fig.add_trace(
            go.Scatter(x=layer_names, y=tensor_sizes, mode='lines+markers', name='Tensor Size'),
            row=1, col=1
        )

        # Add memory usage trace
        memory_usage = [calculate_memory_usage(shape) / (1024 * 1024)
                       for _, shape in self.shape_history]

        fig.add_trace(
            go.Bar(x=layer_names, y=memory_usage, name='Memory (MB)'),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(height=800, title_text="Model Shape Analysis")

        return fig

    def export_visualization(self, format='html'):
        """Export visualization to various formats.

        Args:
            format: Output format ('html', 'png', or 'mermaid')

        Returns:
            Visualization in the specified format
        """
        if format == 'html':
            fig = self.generate_interactive_visualization()
            return fig.to_html()
        elif format == 'png':
            fig = self.generate_interactive_visualization()
            return fig.to_image(format='png')
        elif format == 'mermaid':
            # Generate mermaid.js flowchart
            mermaid = "graph TD\n"
            for i, (layer_name, shape) in enumerate(self.shape_history):
                mermaid += f"  L{i}[{layer_name}<br>{shape}]\n"

            for from_id, to_id in self.layer_connections:
                mermaid += f"  L{from_id} --> L{to_id}\n"

            return mermaid
        else:
            raise ValueError(f"Unsupported format: {format}")

    def propagate_model(self, input_shapes, model_def):
        """Propagate shapes through a complete model with multiple inputs/outputs.

        Args:
            input_shapes: Dictionary mapping input names to shapes
            model_def: Model definition with layers, inputs, and outputs

        Returns:
            Dictionary mapping output names to shapes
        """
        # Track shapes by layer name for reference by other layers
        shape_map = {input_name: shape for input_name, shape in input_shapes.items()}

        # Process each layer in topological order
        for layer in model_def.get('layers', []):
            layer_name = layer.get('name')
            if not layer_name:
                continue

            # Get input shapes (could be multiple)
            layer_input = layer.get('input')
            if isinstance(layer_input, list):
                input_shapes = [shape_map[input_name] for input_name in layer_input
                              if input_name in shape_map]

                # Handle merging of inputs based on layer type
                if layer['type'] == 'Concatenate':
                    input_shape = handle_concatenate(input_shapes, layer.get('params', {}))
                elif layer['type'] == 'Add':
                    input_shape = handle_add(input_shapes, layer.get('params', {}))
                else:
                    # Default to first input shape if we don't know how to merge
                    input_shape = input_shapes[0] if input_shapes else None
            else:
                input_shape = shape_map.get(layer_input)

            if input_shape is None:
                continue

            # Propagate through this layer
            output_shape = self.propagate(input_shape, layer, model_def.get('framework', 'tensorflow'))

            # Store output shape
            shape_map[layer_name] = output_shape

            # Add to shape history
            self._visualize_layer(layer['type'], output_shape)

            # Add connection if we have previous layers
            if isinstance(layer_input, list):
                for input_name in layer_input:
                    if input_name in shape_map:
                        # Find the index of the input layer in shape_history
                        for i, (hist_name, _) in enumerate(self.shape_history):
                            if hist_name == input_name:
                                self._create_connection(i, len(self.shape_history) - 1)
                                break
            elif layer_input in shape_map:
                # Find the index of the input layer in shape_history
                for i, (hist_name, _) in enumerate(self.shape_history):
                    if hist_name == layer_input:
                        self._create_connection(i, len(self.shape_history) - 1)
                        break

        # Return shapes for all output layers
        return {output: shape_map[output] for output in model_def.get('outputs', [])
               if output in shape_map}

    def _log_shape(self, shape, stage):
        if self.debug:
            logging.info(f"{stage.upper()} SHAPE: {shape}")
            logging.debug(f"Shape details: {self._shape_analysis(shape)}")

    def _shape_analysis(self, shape):
        return {
            'total_parameters': np.prod([d for d in shape if d]),
            'spatial_dims': shape[2:-1] if len(shape) > 2 else None,
            'channel_dim': shape[1] if len(shape) > 1 else None
        }

    ### Loading Pretrained Models ####

    def load_pretrained(self, model_name, pretrained=True):
        model = self.hub.load(model_name, pretrained)
        # Propagate shapes through pretrained model
        input_shape = (1, 3, 224, 224)  # Default for ResNet50
        for layer in model.layers:
            input_shape = self.propagate(input_shape, layer, "pytorch")

### Shape Validation for Error Handling ###

class ShapeValidator:
    @staticmethod
    def validate_layer(layer_type, input_shape, params):
        validators = {
            'Conv2D': lambda: ShapeValidator._validate_conv(input_shape, params),
            'Dense': lambda: ShapeValidator._validate_dense(input_shape, params)
        }

        if validator := validators.get(layer_type):
            validator()

    @staticmethod
    def _validate_conv(input_shape, params):
        if len(input_shape) != 4:
            raise ValueError(f"Conv layers need 4D input. Got {len(input_shape)}D")
        if params['kernel_size'] > input_shape[2]:
            raise ValueError(f"Kernel size {params['kernel_size']} "
                           f"exceeds input dimension {input_shape[2]}")

    @staticmethod
    def _validate_dense(input_shape, params):
        if len(input_shape) > 2:
            raise ValueError(
                f"Dense layer expects 2D input (batch, features). "
                f"Got {len(input_shape)}D: {input_shape}"
            )
# Unified parameter handling for TF/PyTorch
FRAMEWORK_DEFAULTS = {
    'tensorflow': {
        'data_format': 'channels_last',
        'padding': 'same'
    },
    'pytorch': {
        'data_format': 'channels_first',
        'padding': 0
    }
}

def get_framework_params(framework):
    return FRAMEWORK_DEFAULTS.get(framework.lower(), FRAMEWORK_DEFAULTS['tensorflow'])

### Real-Time Shape Visualization ###

def _calculate_shape(self, input_shape, layer):
    if layer["type"] == "Dense":
        return (input_shape[0], layer["params"]["units"])
    elif layer["type"] == "Conv2D":
        return (input_shape[0], input_shape[1], input_shape[2], layer["params"]["filters"])
    elif layer["type"] == "Flatten":
        return (input_shape[0], np.prod(input_shape[1:]))
    return input_shape

### Compute FLOPs and memory usage for visualization ###
def compute_flops_params(layer, input_shape):
    """Estimate FLOPs and parameter counts for a given layer."""
    if layer["type"] == "Dense":
        units = layer["params"]["units"]
        params = input_shape[1] * units + units  # Weights + biases
        flops = 2 * params  # Two operations per weight (multiply + add)

    elif layer["type"] == "Conv2D":
        filters = layer["params"]["filters"]
        kernel_size = layer["params"]["kernel_size"]
        stride = layer["params"].get("stride", 1)
        params = (kernel_size[0] * kernel_size[1] * input_shape[-1] + 1) * filters
        output_height = (input_shape[1] - kernel_size[0]) // stride + 1
        output_width = (input_shape[2] - kernel_size[1]) // stride + 1
        flops = params * output_height * output_width

    return params, flops

#######################################
### Gradient Flow Visualization #######
#######################################
def register_gradient_hooks(model):
    """Attaches hooks to capture gradient magnitudes during backprop."""
    gradient_trace = []

    def hook(module, grad_input, grad_output):
        if grad_output[0] is not None:
            grad_norm = grad_output[0].detach().abs().mean().item()
            gradient_trace.append({"layer": module.__class__.__name__, "grad_norm": grad_norm})

    for layer in model.children():
        layer.register_backward_hook(hook)

    return gradient_trace

#####################################
### Dead Neurons Detection ##########
#####################################
def detect_dead_neurons(layer, input, output):
    """Detects inactive neurons (dead neurons)."""
    dead_neurons = (output.detach() == 0).sum().item()
    total_neurons = output.numel()
    dead_ratio = dead_neurons / total_neurons

    return {"layer": layer.__class__.__name__, "dead_ratio": dead_ratio}

######################################
### Activation Anomalies Detection ###
######################################
def detect_activation_anomalies(layer, input, output):
    """Flags NaNs, extremely high activations, or overflows."""
    mean_activation = output.detach().abs().mean().item()
    has_nan = torch.isnan(output).sum().item() > 0
    is_exploding = mean_activation > 1000  # Arbitrary threshold for huge activations

    return {
        "layer": layer.__class__.__name__,
        "mean_activation": mean_activation,
        "anomaly": has_nan or is_exploding
    }


######################
### Step Debugging ###
######################
def step_debug_hook(module, input, output):
    """Pauses execution at this layer for manual debugging."""
    print(f"Paused at layer: {module.__class__.__name__}")
    print(f"Input shape: {input[0].shape}, Output shape: {output.shape}")

    # Wait for user input before continuing
    input("Press Enter to continue...")
