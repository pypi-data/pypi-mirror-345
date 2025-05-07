import torch

class SignSGD(torch.optim.Optimizer):
  def __init__(self, params, lr=1e-3):
    defaults = dict(lr=lr)
    super().__init__(params, defaults)

  @torch.no_grad()
  def step(self, closure=None): # type: ignore
    loss = None
    if closure is not None:
      with torch.enable_grad():
        loss = closure()
    for group in self.param_groups:
      lr = group['lr']
      for p in group['params']:
        if p.grad is None:
          continue
        g = p.grad
        p -= lr * g.sign()
    return loss