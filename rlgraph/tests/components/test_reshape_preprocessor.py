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

import numpy as np
import unittest

from rlgraph.components.layers import ReShape
from rlgraph.spaces import *
from rlgraph.tests import ComponentTest
from rlgraph.utils.numpy import one_hot


class TestReShapePreprocessors(unittest.TestCase):

    def test_reshape(self):
        reshape = ReShape(new_shape=(3, 2))
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=FloatBox(shape=(6,), add_batch_rank=True)
        ))

        test.test("reset")
        # Batch=2
        inputs = np.array([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]])
        expected = np.array([[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]])
        test.test(("apply", inputs), expected_outputs=expected)

    def test_reshape_with_flatten_option(self):
        # Test flattening while leaving batch and time rank as is.
        in_space = FloatBox(shape=(2, 3, 4), add_batch_rank=True, add_time_rank=True, time_major=True)
        reshape = ReShape(flatten=True)
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=in_space
        ))

        test.test("reset")
        # Time-rank=5, Batch=2
        inputs = in_space.sample(size=(5, 2))
        expected = np.reshape(inputs, newshape=(5, 2, 24))
        test.test(("apply", inputs), expected_outputs=expected)

    def test_reshape_with_flatten_option_with_categories(self):
        # Test flattening while leaving batch and time rank as is, but flattening out int categories.
        in_space = IntBox(2, shape=(2, 3, 4), add_batch_rank=True, add_time_rank=True, time_major=False)
        reshape = ReShape(flatten=True, flatten_categories=True)
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=in_space
        ))

        test.test("reset")
        # Batch=3, time-rank=5
        inputs = in_space.sample(size=(3, 5))
        expected = np.reshape(one_hot(inputs, depth=2), newshape=(3, 5, 48))
        test.test(("apply", inputs), expected_outputs=expected)

    def test_reshape_with_time_rank(self):
        # Test with time-rank instead of batch-rank.
        in_space = FloatBox(shape=(4,), add_batch_rank=False, add_time_rank=True)
        reshape = ReShape(new_shape=(2, 2))
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=in_space
        ))

        test.test("reset")
        inputs = in_space.sample(size=3)
        expected = np.reshape(inputs, newshape=(3, 2, 2))
        test.test(("apply", inputs), expected_outputs=expected)

    def test_reshape_with_time_rank_folding(self):
        # Fold time rank into batch rank.
        in_space = FloatBox(shape=(4, 4), add_batch_rank=True, add_time_rank=True, time_major=True)
        reshape = ReShape(fold_time_rank=True)
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=in_space
        ))

        test.test("reset")
        # seq-len=3, batch-size=2
        inputs = in_space.sample(size=(3, 2))
        expected = np.reshape(inputs, newshape=(6, 4, 4))
        test.test(("apply", inputs), expected_outputs=expected)

    def test_reshape_with_time_rank_unfolding(self):
        # Unfold time rank from batch rank with given time-dimension (2 out of 8 -> batch will be 4 after unfolding).
        in_space = FloatBox(shape=(4, 4), add_batch_rank=True, add_time_rank=False)
        reshape = ReShape(unfold_time_rank=2)
        test = ComponentTest(component=reshape, input_spaces=dict(
            preprocessing_inputs=in_space
        ))

        test.test("reset")
        # seq-len=2, batch-size=4 -> unfold from 8.
        inputs = in_space.sample(size=8)
        expected = np.reshape(inputs, newshape=(4, 2, 4, 4))
        test.test(("apply", inputs), expected_outputs=expected)