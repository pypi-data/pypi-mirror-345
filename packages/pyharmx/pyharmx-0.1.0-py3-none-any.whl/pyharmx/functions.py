import torch

_EPSILON = 1e-10


# Nonlinear kernel function
# ====================================
def get_phi(order: int) -> callable:
  r"""
  Coordinate-wise nonlinear function used to 
  define the order of the interpolation. See 
  `here <https://en.wikipedia.org/wiki/Polyharmonic_spline>`_ 
  for the definition.

  :param order: Interpolation order.
  :type order: int

  :return: Coordinate-wise nonlinear kernel :math:`{\phi}`.
  :rtype: callable
  """
  if (order == 1):
    return _phi_1
  elif (order == 2):
    return _phi_2
  elif (order == 4):
    return _phi_4
  elif (order % 2 == 0):
    return lambda r: _phi_even(r, order)
  else:
    return lambda r: _phi_odd(r, order)

def _phi_1(r: torch.Tensor) -> torch.Tensor:
  r_eps = torch.clamp(r, min=_EPSILON)
  return torch.sqrt(r_eps)

def _phi_2(r: torch.Tensor) -> torch.Tensor:
  r_eps = torch.clamp(r, min=_EPSILON)
  return 0.5 * r * torch.log(r_eps)

def _phi_4(r: torch.Tensor) -> torch.Tensor:
  r_eps = torch.clamp(r, min=_EPSILON)
  return 0.5 * torch.square(r) * torch.log(r_eps)

def _phi_even(r: torch.Tensor, order: int) -> torch.Tensor:
  r_eps = torch.clamp(r, min=_EPSILON)
  return 0.5 * torch.pow(r_eps, 0.5 * order) * torch.log(r_eps)

def _phi_odd(r: torch.Tensor, order: int) -> torch.Tensor:
  r_eps = torch.clamp(r, min=_EPSILON)
  return torch.pow(r_eps, 0.5 * order)


# Tensor operation - Distance matrix
# ====================================
def cross_squared_distance_matrix(
  x: torch.Tensor,
  y: torch.Tensor
) -> torch.Tensor:
  """
  Pairwise squared distance between two (batch) 
  matrices' rows (2nd dimension). Computes the 
  pairwise distances between rows of `x` and rows of `y`.

  :param x: 3D tensor with shape `[batch_size, n, d]`.
  :type x: torch.Tensor
  :param y: 3D tensor with shape `[batch_size, m, d]`.
  :type y: torch.Tensor

  :return: 3D tensor with shape `[batch_size, n, m]`. Each
           element represents the squared Euclidean distance
           between vectors `x[b, i, :]` and `y[b, j, :]`.
  :rtype: torch.Tensor
  """
  # Compute quadratic norm
  x_sq_norm = torch.sum(torch.square(x), dim=2, keepdim=False)
  y_sq_norm = torch.sum(torch.square(y), dim=2, keepdim=False)
  # Increase rank
  x_sq_norm = torch.unsqueeze(x_sq_norm, dim=2)
  y_sq_norm = torch.unsqueeze(y_sq_norm, dim=1)
  # Perform matrix multiplication
  x_yt = torch.matmul(x, torch.permute(y, dims=(0,2,1)))
  # Compute squared distance
  return x_sq_norm - 2 * x_yt + y_sq_norm

def pairwise_squared_distance_matrix(
  x: torch.Tensor
) -> torch.Tensor:
  """
  Compute pairwise squared distance among a (batch) matrix's 
  rows (2nd dimension). It is faster than `cross_squared_distance_matrix`.

  :param x: 3D tensor with shape `[batch_size, n, d]`.
  :type x: torch.Tensor

  :return: 3D tensor with shape `[batch_size, n, n]`. Each
           element represents the squared Euclidean distance
           between vectors `x[b, i, :]` and `x[b, j, :]`.
  :rtype: torch.Tensor
  """
  # Compute quadratic values
  x_xt = torch.matmul(x, torch.permute(x, dims=(0,2,1)))
  # Extract batch diagonal
  x_xt_diag = torch.diagonal(x_xt, offset=0, dim1=-2, dim2=-1)
  # Increase rank
  x_xt_diag = torch.unsqueeze(x_xt_diag, dim=2)
  # Compute squared distance
  return x_xt_diag - 2 * x_xt + torch.permute(x_xt_diag, dims=(0,2,1))
