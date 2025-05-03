import torch
import unittest
import numpy as np

from pyharmx import PolyHarmInterpolator


class TestInterpolator(unittest.TestCase):

  def setUp(self):
    # Setup common variables for tests
    self.order = 1
    self.smoothing = 0.0
    self.device = 'cpu'
    self.dtype = torch.float
    # Create random input data
    b = 20
    d, k = 3, 4
    nt, nq = 10, 5
    self.train_points = np.random.rand(b, nt, d)
    self.train_values = np.random.rand(b, nt, k)
    self.query_points = np.random.rand(b, nq, d)
    self.query_values_shape = (b, nq, k)

  def test_class_construction(self):
    interpolator = PolyHarmInterpolator(
      c=self.train_points,
      f=self.train_values,
      order=self.order,
      smoothing=self.smoothing,
      device=self.device,
      dtype=self.dtype
    )
    self.assertIsInstance(interpolator, PolyHarmInterpolator)

  def test_forward_pass(self):
    interpolator = PolyHarmInterpolator(
      c=self.train_points,
      f=self.train_values,
      order=self.order,
      smoothing=self.smoothing,
      device=self.device,
      dtype=self.dtype
    )
    result = interpolator.forward(self.query_points)
    self.assertEqual(result.shape, self.query_values_shape)

  def test_interpolation_consistency(self):
    interpolator = PolyHarmInterpolator(
      c=self.train_points,
      f=self.train_values,
      order=self.order,
      smoothing=self.smoothing,
      device=self.device,
      dtype=self.dtype
    )
    result = interpolator.forward(self.train_points)
    np.testing.assert_allclose(
      result.numpy(force=True),
      self.train_values,
      rtol=1e-4,
      atol=1e-5
    )

if __name__ == '__main__':
  unittest.main()
