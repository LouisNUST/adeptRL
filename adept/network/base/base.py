# Copyright (C) 2018 Heron Systems, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import abc

import torch
from torch import distributed as dist


class BaseNetwork(torch.nn.Module):
    @classmethod
    @abc.abstractmethod
    def from_args(
        cls,
        args,
        observation_space,
        output_space,
        gpu_preprocessor,
        net_reg
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def new_internals(self, device):
        """
        :return: Dict[InternalKey, torch.Tensor (ND)]
        """
        raise NotImplementedError

    @abc.abstractmethod
    def forward(self, observation, internals):
        raise NotImplementedError

    def internal_space(self):
        return {k: t.shape for k, t in self.new_internals('cpu').items()}

    def sync(self, src, grp, async_op=False):
        handles = []
        for t in self.state_dict().values():
            handles.append(
                dist.broadcast(t, src, grp, True)
            )

        if not async_op:
            handles = [h.wait() for h in handles]

        return handles
