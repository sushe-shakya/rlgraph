# Copyright 2018 The RLgraph authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from rlgraph import get_backend
from rlgraph.components.layers.preprocessing import PreprocessLayer
from rlgraph.utils.ops import flatten_op, unflatten_op

if get_backend() == "tf":
    import tensorflow as tf
#elif get_backend() == "pytorch":
#    import torch


class Transpose(PreprocessLayer):
    """
    """
    def __init__(self, scope="transpose", **kwargs):
        """
        """
        super(Transpose, self).__init__(scope=scope, **kwargs)

        self.output_time_majors = dict()

    def get_preprocessed_space(self, space):
        ret = dict()
        for key, single_space in space.flatten().items():
            class_ = type(single_space)
            # We flip batch and time ranks.
            time_major = not single_space.time_major
            ret[key] = class_(shape=single_space.shape,
                              add_batch_rank=single_space.has_batch_rank,
                              add_time_rank=single_space.has_time_rank, time_major=time_major)
            self.output_time_majors[key] = time_major
        ret = unflatten_op(ret)
        return ret

    def _graph_fn_apply(self, key, preprocessing_inputs):
        """
        Transposes the input by flipping batch and time ranks.
        """
        if get_backend() == "tf":
            transposed = tf.transpose(
                preprocessing_inputs, perm=(1, 0) + tuple(preprocessing_inputs.shape.as_list()[2:]), name="transpose"
            )

            transposed._batch_rank = 0 if self.output_time_majors[key] is False else 1
            transposed._time_rank = 0 if self.output_time_majors[key] is True else 1

            return transposed
