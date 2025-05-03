import torch
import numpy as np

from .functions import *
from typing import Union


class PolyHarmInterpolator(torch.nn.Module):
  r"""
  Interpolate batched data using polyharmonic interpolation.

  The interpolant has the form:

  :math:`{f(x) = \sum_{i = 1}^n w_i \phi(||x - c_i||) + v^\text{T}x + b}`.

  This is a sum of two terms: (1) A weighted sum of radial basis function 
  (RBF) terms with centers :math:`{\left(c_1, \ldots, c_n\right)}`. (2) A 
  linear term with a bias. The :math:`{c_i}` vectors are 'training' points. 
  The coefficients :math:`{w}` and :math:`{v}` are estimated such that the 
  interpolant exactly fits the value of the function at the :math:`{c_i}` 
  points, and the vector :math:`{w}` is orthogonal to each :math:`{c_i}`, 
  and the vector :math:`{w}` sums to 0. With these constraints, the 
  coefficients can be obtained by solving a linear system.

  The function :math:`{\phi}` is an RBF, parametrized by an interpolation 
  order. Using `order=2` produces the well-known thin-plate spline.

  We also provide the option to perform regularized interpolation. Here, the
  interpolant is selected to trade off between the squared loss on the
  training data and a certain measure of its curvature
  [`details <https://en.wikipedia.org/wiki/Polyharmonic_spline>`_].
  Using a regularization weight greater than zero has the effect that the
  interpolant will no longer exactly fit the training data. However, it may be
  less vulnerable to overfitting, particularly for high-order interpolation.

  :param c: 3D tensor with shape `[batch_size, n, d]` of `n` `d`-dimensional
            locations. These do not need to be regularly-spaced.
  :type c: torch.Tensor or np.ndarray
  :param f: 3D tensor with shape `[batch_size, n, k]` of `n` `c`-dimensional
            values evaluated at train_points.
  :type f: torch.Tensor or np.ndarray
  :param order: (optional) Order of the interpolation. Common values are
                1 for :math:`{\phi(r)=r}`, 2 for :math:`{\phi(r)=r^2 \log(r)}`
                (thin-plate spline), or 3 for :math:`{\phi(r)=r^3}`.
  :type order: int
  :param smoothing: (optional) Weight placed on the regularization term.
                    This will depend substantially on the problem, and
                    it should always be tuned. For many problems, it is
                    reasonable to use no regularization. If using a non-zero
                    value, we recommend a small value like 0.001.
  :type smoothing: float
  :param device: (optional) Specifies the default device to store tensors
                 and perform interpolation.
  :type device: str
  :param dtype: (optional) Specifies the default precision.
  :type dtype: torch.dtype
  """
  def __init__(
    self,
    c: Union[torch.Tensor, np.ndarray],
    f: Union[torch.Tensor, np.ndarray],
    order: int = 3,
    smoothing: float = 0.0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float,
    *args,
    **kwargs
  ) -> None:
    super(PolyHarmInterpolator, self).__init__(*args, **kwargs)
    self._built = False
    # Set dtype and device
    self.dtype = dtype
    self.device = device
    self.malloc_kwargs = {
      "dtype": self.dtype,
      "device": self.device
    }
    # Set training data
    for (k, x) in (('c',c), ('f',f)):
      if isinstance(x, np.ndarray):
        x = torch.from_numpy(x)
      x = x.to(**self.malloc_kwargs)
      if (x.ndim != 3):
        raise ValueError(f"'{k}' must be a 3-dimensional tensor.")
      self.register_buffer(k, x)
    if (self.c.shape[:2] != self.f.shape[:2]):
      raise ValueError(
        "The first two dimensions of 'c' and 'f' must be the same."
      )
    # Get smoothing and kernel function
    self.smoothing = float(smoothing)
    self.order = int(order)
    self.phi = get_phi(self.order)

  def forward(self, x: Union[torch.Tensor, np.ndarray]) -> torch.Tensor:
    r"""
    Apply polyharmonic interpolation model to new input data.

    Given coefficients :math:`{w}` and :math:`{v}` for the interpolation 
    model, the interpolated function is evaluated at query points :math:`{x}`.

    Note that the interpolation procedure is differentiable with respect 
    to :math:`{x}`.

    :param x: 3D tensor with shape `[batch_size, m, d]`
              to evaluate the interpolation at.
    :type x: torch.Tensor

    :return: Polyharmonic interpolation evaluated at query points `x`.
    :rtype: torch.Tensor

    :raises ValueError: If the input tensor `x` is not 3-dimensional.
    """
    if (not self._built):
      # Fit the interpolant to the observed data
      self.build()
    if (x.ndim != 3):
      raise ValueError("'x' must be a 3-dimensional tensor.")
    if isinstance(x, np.ndarray):
      x = torch.from_numpy(x).to(**self.malloc_kwargs)
    if (x.device != self.device):
      x = x.to(**self.malloc_kwargs)
    # Compute the contribution from the rbf term
    d = cross_squared_distance_matrix(x, self.c)
    d_phi = self.phi(d)
    rbf_term = torch.matmul(d_phi, self.w)
    # Compute the contribution from the linear term
    ones = torch.ones_like(x[..., :1], **self.malloc_kwargs)
    x_pad = torch.concat([x, ones], dim=2)
    linear_term = torch.matmul(x_pad, self.v)
    return rbf_term + linear_term

  def build(self) -> None:
    r"""
    Solve for interpolation coefficients.

    Computes the coefficients :math:`{w}` and :math:`{v}` of the 
    polyharmonic interpolant for the training data defined by 
    :math:`{\left(c, f\right)}` using the kernel :math:`{\phi}`.
    """
    # Get dimensions
    b, n, d = list(self.c.shape)
    k = self.f.shape[-1]
    # Construct the linear system
    # > Matrix A
    amat = self.phi(pairwise_squared_distance_matrix(self.c))
    if (self.smoothing > 0):
      imat = torch.unsqueeze(torch.eye(n, **self.malloc_kwargs), dim=0)
      amat += self.smoothing * imat
    # > Matrix B
    ones = torch.ones_like(self.c[..., :1], **self.malloc_kwargs)
    bmat = torch.cat([self.c, ones], dim=2)
    bmat_ncols = bmat.shape[2]
    # > Left hand side
    lhs_zeros = torch.zeros([b, bmat_ncols, bmat_ncols], **self.malloc_kwargs)
    block_right = torch.cat([bmat, lhs_zeros], dim=1)
    block_left = torch.cat([amat, torch.permute(bmat, dims=(0,2,1))], dim=1)
    lhs = torch.cat([block_left, block_right], dim=2)
    # > Right hand side
    rhs_zeros = torch.zeros([b, d + 1, k], **self.malloc_kwargs)
    rhs = torch.cat([self.f, rhs_zeros], dim=1)
    # Solve the linear system
    w_v = torch.linalg.solve(lhs, rhs)
    w, v = w_v[:, :n, :], w_v[:, n:, :]
    self.register_buffer("w", w)
    self.register_buffer("v", v)
    self._built = True
