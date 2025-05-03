from abc import ABC, abstractmethod
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from .Util import T


class Agent(ABC):

    @abstractmethod
    def train_actions(self, observations, action_mask=None, step=False):
        return 0, 0, 0  # Action 0, log_prob 0, value

    @abstractmethod
    def ego_actions(self, observations, action_mask=None):
        return 0

    @abstractmethod
    def imitation_learn(self, observations, actions):
        return 0  # loss

    @abstractmethod
    def utility_function(self, observations, actions=None):
        return 0  # Returns the single-agent critic for a single action.
        # If actions are none then V(s)

    @abstractmethod
    def expected_V(self, obs, legal_action):
        print("expected_V not implemeted")
        return 0

    @abstractmethod
    def reinforcement_learn(self, batch, agent_num=0, critic_only=False, debug=False):
        return 0, 0  # actor loss, critic loss

    @abstractmethod
    def save(self, checkpoint_path):
        print("Save not implemeted")

    @abstractmethod
    def load(self, checkpoint_path):
        print("Load not implemented")


def _orthogonal_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class ffEncoder(nn.Module):
    def __init__(
        self,
        obs_dim,
        hidden_dims,
        activation="relu",
        device="cpu",
        orthogonal_init=False,
        dropout=0.6,
    ):
        super(ffEncoder, self).__init__()
        activations = {
            "relu": F.relu,
            "tanh": torch.tanh,
            "sigmoid": torch.sigmoid,
            "none": lambda x: x,
        }
        assert activation in activations, "Invalid activation function"
        self.activation = activations[activation]
        self.drop = dropout
        self.dropout = nn.Dropout(p=dropout)
        self.encoder = nn.ModuleList()
        print(obs_dim, hidden_dims)
        for i in range(len(hidden_dims)):
            if i == 0:
                self.encoder.append(nn.Linear(obs_dim, hidden_dims[i]))
            else:
                self.encoder.append(nn.Linear(hidden_dims[i - 1], hidden_dims[i]))
            if orthogonal_init:
                _orthogonal_init(self.encoder[-1])
        self.float()
        self.to(device)
        self.device = device
        # self.optimizer = torch.optim.Adam(self.parameters())

    def forward(self, x, debug=False):
        if debug:
            print(f"ffEncoder: x {x}")
        x = T(x, self.device).float()
        if debug:
            print(f"ffEncoder after T: x {x}")
        if debug:
            interlist = []
            interlist.append(x)
        for layer in self.encoder:
            if layer == self.encoder[0] and self.drop > 0:
                x = self.activation(self.dropout(layer(x)))
            else:
                x = self.activation(layer(x))
            if debug:
                interlist.append(x)
        # if x contains nan, print the intermediate list and encoder weights
        if torch.isnan(x).any():
            if debug:
                print(f"Intermediate list: {interlist}")
            for layer in self.encoder:
                print(f"Layer {layer.weight}")
        return x


class MixedActor(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=None,  # number of continuouis action dimensions =5
        discrete_action_dims=None,  # list of discrete action dimensions =[2, 3, 4]
        max_actions: np.array = np.array([1.0], dtype=np.float32),
        min_actions: np.array = np.array([-1.0], dtype=np.float32),
        hidden_dims: np.array = np.array([256, 256], dtype=np.int32),
        encoder=None,  # ffEncoder if hidden dims are provided and encoder is not provided
        device="cpu",
        tau=1.0,
        hard=False,
        orthogonal_init=False,
        activation="relu",
    ):
        super(MixedActor, self).__init__()
        self.device = device

        self.tau = tau
        self.hard = hard
        print(hidden_dims)
        if encoder is None and len(hidden_dims) > 0:
            self.encoder = ffEncoder(
                obs_dim, hidden_dims, device=device, activation=activation, dropout=0
            )

        assert not (
            continuous_action_dim is None and discrete_action_dims is None
        ), "At least one action dim should be provided"
        if continuous_action_dim is not None and continuous_action_dim > 0:
            assert (
                len(max_actions) == continuous_action_dim
                and len(min_actions) == continuous_action_dim
            ), f"max_actions should be provided for each continuous action dim {len(max_actions)},{continuous_action_dim}"

        # print(
        #    f"Min actions: {min_actions}, max actions: {max_actions}, torch {torch.from_numpy(max_actions - min_actions)}"
        # )
        if max_actions is not None and min_actions is not None:
            self.action_scales = (
                torch.from_numpy(max_actions - min_actions).float().to(device) / 2
            )
            # doesn't track grad by default in from_numpy
            self.action_biases = (
                torch.from_numpy(max_actions + min_actions).float().to(device) / 2
            )
            self.max_actions = max_actions
            self.min_actions = min_actions

        self.continuous_actions_head = None
        if continuous_action_dim is not None and continuous_action_dim > 0:
            self.continuous_actions_head = nn.Linear(
                hidden_dims[-1], continuous_action_dim
            )
            if orthogonal_init:
                _orthogonal_init(self.continuous_actions_head)

        self.discrete_action_heads = nn.ModuleList()
        if discrete_action_dims is not None and len(discrete_action_dims) > 0:
            for dim in discrete_action_dims:
                self.discrete_action_heads.append(nn.Linear(hidden_dims[-1], dim))
                if orthogonal_init:
                    _orthogonal_init(self.discrete_action_heads[-1])
        self.to(device)

    def forward(self, x, action_mask=None, gumbel=False, debug=False):
        ogx = x
        if debug:
            print(f"MixedActor: x {x}, action_mask {action_mask}, gumbel {gumbel}")
        if self.encoder is not None:
            x = self.encoder(x=x, debug=debug)
        else:
            x = T(a=x, device=self.device, debug=debug)

        continuous_actions = None
        discrete_actions = None
        if self.continuous_actions_head is not None:
            continuous_actions = (
                F.tanh(self.continuous_actions_head(x)) * self.action_scales
                + self.action_biases
            )
            # If continuous action contains nan, print x and the continuous actions
            if torch.isnan(continuous_actions).any():
                print(f"Continuous actions: {continuous_actions}")
                print(f"X: {x}, ogx: {ogx}")
                # raise ValueError("Continuous actions contain nan")

        # TODO: Put this into it's own function and implement the ppo way of sampling
        if self.discrete_action_heads is not None:
            discrete_actions = []
            for i, head in enumerate(self.discrete_action_heads):
                logits = head(x)

                if gumbel:
                    if action_mask is not None:
                        logits[action_mask == 0] = -1e8
                    probs = F.gumbel_softmax(
                        logits, dim=-1, tau=self.tau, hard=self.hard
                    )
                    # activations = activations / activations.sum(dim=-1, keepdim=True)
                    discrete_actions.append(probs)
                else:
                    if action_mask is not None:
                        logits[action_mask == 0] = -1e8
                    discrete_actions.append(F.softmax(logits, dim=-1))

        return continuous_actions, discrete_actions


class StochasticActor(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim: int = 0,  # number of continuouis action dimensions =5
        discrete_action_dims: (
            list[int] | None
        ) = None,  # list of discrete action dimensions =[2, 3, 4]
        max_actions: np.array = np.array([1.0], dtype=np.float32),
        min_actions: np.array = np.array([-1.0], dtype=np.float32),
        hidden_dims: np.array = np.array(
            [64, 64], dtype=np.int32
        ),  # Last dim will be used to specify encoder output dim if one is supplied
        encoder=None,  # ffEncoder if hidden dims are provided and encoder is not provided
        device="cpu",
        gumbel_tau=1.0,  # for gumbel soft
        gumbel_tau_decay=0.9999,
        gumbel_tau_min=0.1,
        hard=False,
        orthogonal_init=False,
        activation="relu",  # activation function for the encoder
        action_head_hidden_dims=[32],  # iterable of hidden dims for action heads
        log_std_clamp_range=(-10, 2),
    ):
        super(MixedActor, self).__init__()
        self.device = device
        self.gumbel_tau = gumbel_tau
        self.gumbel_tau_decay = gumbel_tau_decay
        self.gumbel_tau_min = gumbel_tau_min
        self.hard = hard
        self.continuous_action_dim = continuous_action_dim
        self.discrete_action_dims = discrete_action_dims
        self.log_std_clamp_range = log_std_clamp_range
        acts = {"relu": F.relu, "tanh": torch.tanh, "sigmoid": torch.sigmoid}
        if activation in acts:
            self.activation = acts[activation]
        else:
            self.activation = activation
        if encoder is None and len(hidden_dims) > 0:
            self.encoder = ffEncoder(
                obs_dim, hidden_dims, device=device, activation=activation, dropout=0
            )

        assert not (
            continuous_action_dim == 0 and discrete_action_dims is None
        ), "At least one action dim should be provided"
        if continuous_action_dim > 0:
            assert (
                len(max_actions) == continuous_action_dim
                and len(min_actions) == continuous_action_dim
            ), f"max_actions should be provided for each continuous action dim {len(max_actions)},{continuous_action_dim}"

        # print(
        #    f"Min actions: {min_actions}, max actions: {max_actions}, torch {torch.from_numpy(max_actions - min_actions)}"
        # )
        if max_actions is not None and min_actions is not None:
            self.action_scales = (
                torch.from_numpy(max_actions - min_actions).float().to(device) / 2
            )
            # doesn't track grad by default in from_numpy
            self.action_biases = (
                torch.from_numpy(max_actions + min_actions).float().to(device) / 2
            )
            self.max_actions = max_actions
            self.min_actions = min_actions

        # Initialize the action head which outputs shape (continuous_action_dim * 2 + sum(discrete_action_dims))
        self._init_action_heads(
            hidden_dims,
            orthogonal_init,
            action_head_hidden_dims,
        )
        self.to(device)

    def _init_action_heads(
        self,
        hidden_dims,
        orthogonal_init,
        action_head_hidden_dims,
    ):
        self.action_layers = nn.ModuleList()
        last_hidden_dim = hidden_dims[-1]
        output_dim = self.continuous_action_dim * 2
        if self.discrete_action_dims is not None and len(self.discrete_action_dims) > 0:
            output_dim += sum(self.discrete_action_dims)

        if action_head_hidden_dims is not None and len(action_head_hidden_dims) > 0:
            last_hidden_dim = action_head_hidden_dims[-1]
            for i, dim in enumerate(action_head_hidden_dims):
                if i == 0:
                    self.action_layers.append(nn.Linear(hidden_dims[-1], dim))
                else:
                    self.action_layers.append(
                        nn.Linear(action_head_hidden_dims[i - 1], dim)
                    )

                if orthogonal_init:
                    _orthogonal_init(self.action_layers[-1])
            self.action_layers.append(nn.Linear(last_hidden_dim, output_dim))
            if orthogonal_init:
                _orthogonal_init(self.action_layers[-1])

    def forward(self, x, action_mask=None, gumbel=False, debug=False):
        embedding = self.encoder(x=x, debug=debug) if self.encoder is not None else x
        if debug:
            print(
                f"  MixedActor: x shape {x.shape}, action_mask {action_mask}, gumbel {gumbel}"
            )
        for i, layer in self.action_layers:
            if i != len(self.action_layers) - 1:
                embedding = F.relu(layer(embedding))
            else:
                embedding = layer(embedding)
            if debug:
                print(f"  MixedActor: embedding shape {embedding.shape}")
        continuous_means = None
        continuous_log_std_logits = None
        discrete_logits = None
        if self.continuous_action_dim > 0:
            continuous_means = embedding[:, : self.continuous_action_dim]
            continuous_log_std_logits = embedding[
                :, self.continuous_action_dim : 2 * self.continuous_action_dim
            ]
        if self.discrete_action_dims is not None and len(self.discrete_action_dims) > 0:
            discrete_logits = []
            start = 2 * self.continuous_action_dim
            for i, dim in enumerate(self.discrete_action_dims):
                end = start + dim
                logits = embedding[:, start:end]
                discrete_logits.append(logits)

        return continuous_means, continuous_log_std_logits, discrete_logits

    def action_from_logits(
        self, continuous_means, continuous_log_std_logits, discrete_logits
    ):
        """
        Produces actions from logits with gradient maintained always for continuous and if gumbel is True for discrete
        Args:
            continuous_means: (batch_size, continuous_action_dim)
            continuous_log_std_logits: (batch_size, continuous_action_dim)
            discrete_logits: list of (batch_size, discrete_action_dim[i]) for each discrete action dim
        Returns:
            continuous_actions: (batch_size, continuous_action_dim)
                Continuous actions are sampled from a normal distribution with means and std parameterized before
                passing through tanh and scaled to the action space
            discrete_actions:
                If Gumbel: list of len n [(batch_size, discrete_action_dim[i])] for each discrete action dim 'i' in 'n'
                Else: torch.Long shape = (batch_size, len(discrete_action_dims))

                Gumbel softmax is to retain the gradient through reparameterization trick so it is like returning
                a soft one-hot coding with a tensor for each discrete action dim
                If not gumbel, then it is a long tensor of the sampled actions where each action is sampled from
                the categorical distribution
        """
        if self.continuous_action_dim > 0:
            if self.log_std_clamp_range is not None:
                continuous_log_std_logits = torch.clamp(
                    continuous_log_std_logits,
                    min=self.log_std_clamp_range[0],
                    max=self.log_std_clamp_range[1],
                )
            continuous_actions = continuous_means + torch.exp(
                continuous_log_std_logits
            ) * torch.randn(continuous_means.shape)
            continuous_actions = (
                torch.tanh(continuous_actions) * self.action_scales + self.action_biases
            )
        else:
            continuous_actions = None

        if self.discrete_action_dims is not None and len(self.discrete_action_dims) > 0:

            if self.gumbel_tau > self.gumbel_tau_min:
                discrete_actions = []
                for i, logits in enumerate(discrete_logits):
                    probs = F.gumbel_softmax(
                        logits, dim=-1, tau=self.gumbel_tau, hard=self.hard
                    )
                    discrete_actions.append(probs)
            else:
                discrete_actions = torch.zeros(
                    discrete_logits[0].shape[0], len(self.discrete_action_dims)
                )
                for i, logits in enumerate(discrete_logits):
                    discrete_actions[:, i] = torch.distributions.Categorical(
                        logits=logits
                    ).sample()

        return continuous_actions, discrete_actions


class ValueSA(nn.Module):
    def __init__(
        self, obs_dim, action_dim, hidden_dim=256, device="cpu", activation="relu"
    ):
        super(ValueSA, self).__init__()
        self.device = device
        if activation not in ["relu", "tanh", "sigmoid"]:
            raise ValueError(
                "Invalid activation function, should be: relu, tanh, sigmoid"
            )
        activations = {"relu": F.relu, "tanh": torch.tanh, "sigmoid": torch.sigmoid}
        self.activation = activations[activation]
        self.l1 = nn.Linear(obs_dim + action_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.l3 = nn.Linear(hidden_dim, 1)
        self.to(device)

    def forward(self, x, u, debug=False):
        if debug:
            print(f"ValueSA: x {x}, u {u}")
        x = self.activation(self.l1(torch.cat([x, u], -1)))
        x = self.activation(self.l2(x))
        x = self.l3(x)
        return x


class ValueS(nn.Module):
    def __init__(
        self,
        obs_dim,
        hidden_dim=256,
        device="cpu",
        activation="relu",
        orthogonal_init=False,
    ):
        super(ValueS, self).__init__()
        self.device = device
        if activation not in ["relu", "tanh", "sigmoid"]:
            raise ValueError(
                "Invalid activation function, should be: relu, tanh, sigmoid"
            )
        activations = {"relu": F.relu, "tanh": torch.tanh, "sigmoid": torch.sigmoid}
        self.activation = activations[activation]
        self.l1 = nn.Linear(obs_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.l3 = nn.Linear(hidden_dim, 1)

        if orthogonal_init:
            _orthogonal_init(self.l1)
            _orthogonal_init(self.l2)
            _orthogonal_init(self.l3)
        self.to(device)

    def forward(self, x):
        x = T(x, self.device)
        x = self.activation(self.l1(x))
        x = self.activation(self.l2(x))
        x = self.l3(x)
        return x


class QSCA(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=0,
        discrete_action_dims=[1],
        hidden_dim=256,
        device="cpu",
    ):
        super(QSCA, self).__init__()
        self.device = device
        self.l1 = nn.Linear(obs_dim + continuous_action_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.discrete_Q_heads = nn.ModuleList()
        if discrete_action_dims is not None and len(discrete_action_dims) > 0:
            for dim in discrete_action_dims:
                self.discrete_Q_heads.append(nn.Linear(hidden_dim, dim))
        self.to(device)

    def forward(self, x):
        x = T(x, self.device)
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        Qs = []
        for i, head in enumerate(self.discrete_Q_heads):
            Qi = head(x)
            Qs.append(Qi)
        if len(Qs) == 1:
            Qs = Qs[0]
        return Qs


class QSAA(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=0,
        discrete_action_dims=[1],
        hidden_dim=256,
        device="cpu",
    ):
        super(QSAA, self).__init__()
        self.device = device
        total_discrete_dims = sum(discrete_action_dims)
        input_dim = obs_dim + continuous_action_dim + total_discrete_dims
        self.l1 = nn.Linear(input_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.l3 = nn.Linear(hidden_dim, 1)
        self.to(device)

    def forward(self, s, a_c=None, a_d=None):
        if a_c is None:
            a_c = torch.tensor([]).to(self.device)
        if a_d is None:
            a_d = torch.tensor([]).to(self.device)
        x = torch.cat([s, a_c, a_d], dim=-1)
        x = T(x, self.device)
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        x = self.l3(x)
        return x


class QS(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=0,
        discrete_action_dims=[2],
        hidden_dims=[64, 64],
        encoder=None,
        activation="relu",
        orthogonal=False,
        dropout=0.0,
        dueling=False,
        device="cpu",
        n_c_action_bins=11,
        head_hidden_dim=64,  # adding a layer size gives hidden layers to heads
    ):
        super(QS, self).__init__()

        # guard code
        if head_hidden_dim is None:
            head_hidden_dim = 0
        if continuous_action_dim is None:
            continuous_action_dim = 0
        if encoder is not None:
            self.encoder = encoder
        else:
            self.encoder = ffEncoder(
                obs_dim, hidden_dims, activation, device, orthogonal, dropout
            )
        if discrete_action_dims is not None:
            if isinstance(discrete_action_dims, int):
                discrete_action_dims = [discrete_action_dims]
            if len(discrete_action_dims) == 0:
                ValueError(
                    "discrete_action_dims should not be empty, use [x] for a single discrete action with cardonality 'x'"
                )
            if min(discrete_action_dims) < 1:
                ValueError(
                    "discrete_action_dims should not contain values less than 1, use [x] for a single discrete action with cardonality 'x'"
                )
        # setting needed self variables
        self.disc_action_dims = discrete_action_dims
        self.cont_action_dims = continuous_action_dim
        self.device = device
        self.dueling = dueling
        self.last_hidden_dim = head_hidden_dim
        if head_hidden_dim == 0:
            self.last_hidden_dim = hidden_dims[-1]
        self.joint_heads_hidden_layer = None
        self.advantage_heads = None
        self.tot_adv_size = continuous_action_dim * n_c_action_bins
        if discrete_action_dims is not None:
            self.tot_adv_size += sum(discrete_action_dims)

        # set up hidden layer for the adv and V heads
        if head_hidden_dim != 0:
            self.joint_heads_hidden_layer = nn.Linear(
                hidden_dims[-1], head_hidden_dim * (2 if self.dueling else 1)
            )
            if orthogonal:
                _orthogonal_init(self.joint_heads_hidden_layer)
        # set up the adv heads if this isn't just a V network
        if self.cont_action_dims > 0 or self.disc_action_dims is not None:
            self.advantage_heads = nn.Linear(
                self.last_hidden_dim,
                self.tot_adv_size,
            )

        # set up the value head if dueling is True
        self.value_head = nn.Linear(self.last_hidden_dim, 1) if self.dueling else None
        print(
            f"initialized QS with: {self.joint_heads_hidden_layer}, {self.value_head}, {self.advantage_heads}\n  d_dim: {discrete_action_dims}, c_dim: {continuous_action_dim}, h_dim: {hidden_dims}, head_hidden_dim: {head_hidden_dim}"
        )
        self.to(device)

    def forward(self, x, action_mask=None):
        # TODO: action mask implementation
        x = T(x, self.device)
        x = self.encoder(x)
        values = 0

        # If the heads have their own hidden layer for a 2 layer dueling network
        if self.joint_heads_hidden_layer is not None:
            x = F.relu(self.joint_heads_hidden_layer(x))
        if self.dueling:
            values = self.value_head(x[:, : self.last_hidden_dim])

        if self.advantage_heads is not None:
            advantages = self.advantage_heads(x[:, -self.last_hidden_dim :])

        tot_disc_dims = 0
        disc_advantages = None
        cont_advantages = None
        if self.disc_action_dims is not None:
            tot_disc_dims = sum(self.disc_action_dims)
            disc_advantages = []
            start = 0
            for i, dim in enumerate(self.disc_action_dims):
                end = start + dim
                disc_advantages.append(advantages[:, start:end])
                if (
                    self.dueling
                ):  # These are mean zero when dueling or Q values when not
                    disc_advantages[-1] = disc_advantages[-1] - disc_advantages[
                        -1
                    ].mean(dim=-1, keepdim=True)
                start = end

        if self.cont_action_dims > 0:
            cont_advantages = (
                advantages[:, tot_disc_dims:]
                .view(advantages.shape[0], self.cont_action_dims, -1)
                .transpose(0, 1)  # TODO: figure out if it is worth it to transpose
            )  # transposed because then discrete and continuous output same dim order
            if self.dueling:  # These are mean zero when dueling or Q values when not
                cont_advantages = cont_advantages - cont_advantages.mean(
                    dim=-1, keepdim=True
                )

        return values, disc_advantages, cont_advantages


# TODO: Try Dueling heads 2 layers and add activation functions for nonlinearities


class DuelingQSCA(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=0,
        discrete_action_dims=[1],
        hidden_dim=256,
        device="cpu",
    ):
        super(DuelingQSCA, self).__init__()
        self.device = device
        self.l1 = nn.Linear(obs_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.value_head = nn.Linear(hidden_dim, 1)
        self.advantage_heads = nn.ModuleList()
        if discrete_action_dims is not None and len(discrete_action_dims) > 0:
            for dim in discrete_action_dims:
                self.advantage_heads.append(
                    nn.Linear(hidden_dim + continuous_action_dim, dim)
                )
        self.to(device)

    def forward(self, x, u):
        x = T(x, self.device)
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        values = self.value_head(x)
        advantages = []
        xu = torch.cat([x, u], dim=-1)
        for i, head in enumerate(self.advantage_heads):
            Adv = head(xu)
            Adv = Adv - Adv.mean(dim=-1, keepdim=True)
            advantages.append(Adv)
        return values, advantages


class DuelingQSAA(nn.Module):
    def __init__(
        self,
        obs_dim,
        continuous_action_dim=0,
        discrete_action_dims=[1],
        hidden_dim=256,
        device="cpu",
    ):
        super(DuelingQSAA, self).__init__()
        self.device = device
        total_discrete_dims = sum(discrete_action_dims)
        input_dim = obs_dim
        self.l1 = nn.Linear(input_dim, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim)
        self.value_head = nn.Linear(hidden_dim, 1)
        self.advantage_head = nn.Linear(
            hidden_dim + continuous_action_dim + total_discrete_dims, 1
        )

        self.to(device)

    def forward(self, x, a_c=None, a_d=None):
        if a_c is None:
            a_c = torch.tensor([]).to(self.device)
        if a_d is None:
            a_d = torch.tensor([]).to(self.device)

        x = T(x, self.device)
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        values = self.value_head(x)
        advantages = []
        xu = torch.cat([x, a_c, a_d], dim=-1)
        for i, head in enumerate(self.advantage_heads):
            Adv = head(xu)
            # Adv = Adv - Adv.mean(dim=-1, keepdim=True)
            # Sample some kind of action space and then calculate the advantage
            advantages.append(Adv)
        return values, advantages


# Q(s) -> R^n
# Q(s,a) -> R

# Q(s,a_c)     = R^n
# Q(s,a_c,a_d) = R

# Q(s) ->   V(s)+A(s,a)      A - mean(A)
# Q(s,a) -> V(s)+A(s,a)      Posisibilities to adapt


if __name__ == "__main__":
    device = "cuda"
    # Example instantiations
    c_dim = 2
    d_dims = [3, 4]
    actor = MixedActor(
        obs_dim=10,
        continuous_action_dim=c_dim,
        discrete_action_dims=d_dims,
        max_actions=np.array([1.0, 1.0]),
        min_actions=np.array([-1.0, -1.0]),
        hidden_dims=np.array([256, 256]),
        device=device,
    )

    value_sa = ValueSA(
        obs_dim=10, action_dim=c_dim + np.sum(d_dims), hidden_dim=256, device=device
    )

    value_s = ValueS(obs_dim=10, hidden_dim=256, device=device)

    q_net = QSCA(
        obs_dim=10,
        hidden_dim=256,
        discrete_action_dims=d_dims,
        continuous_action_dim=c_dim,
        device=device,
    )
    qsaa_net = QSAA(
        obs_dim=10,
        continuous_action_dim=c_dim,
        discrete_action_dims=d_dims,
        hidden_dim=256,
        device=device,
    )
    state = torch.rand(size=(10,)).to(device)
    states = torch.rand(size=(5, 10)).to(device)

    # Single state through actor
    cont_acts, disc_acts = actor(state, gumbel=True)
    print("\nSingle state through actor:")
    print(
        "Continuous actions:",
        cont_acts,
        "Shape:",
        cont_acts.shape if cont_acts is not None else None,
    )
    for i, da in enumerate(disc_acts):
        print(
            f"Discrete action {i}:", da, "Shape:", da.shape if da is not None else None
        )

    # Batch of states through actor
    cont_acts_batch, disc_acts_batch = actor(states)
    print("\nBatch of states through actor:")
    print(
        "Continuous actions:",
        cont_acts_batch,
        "Shape:",
        cont_acts_batch.shape if cont_acts_batch is not None else None,
    )
    for i, da in enumerate(disc_acts_batch):
        print(
            f"Discrete action {i}:", da, "Shape:", da.shape if da is not None else None
        )

    print("Discrete Actions Concatenated")
    print(torch.cat(disc_acts, dim=0))

    print("All actions concatenated")
    print(torch.cat((cont_acts, torch.cat(disc_acts, dim=-1)), dim=-1))
    # Test value functions
    # Single state
    val_sa_out = value_sa(
        state, torch.cat((cont_acts, torch.cat(disc_acts, dim=-1)), dim=-1)
    )
    val_s_out = value_s(state)
    q_out = q_net(torch.cat((state, cont_acts), dim=-1))
    # Test single state through QSAA
    qsaa_out = qsaa_net(state, cont_acts, torch.cat(disc_acts, dim=-1))

    print("\nSingle state through value networks:")
    print("ValueSA output:", val_sa_out, "Shape:", val_sa_out.shape)
    print("ValueS output:", val_s_out, "Shape:", val_s_out.shape)
    print(
        "Q output:",
        q_out,
        "Shape:",
        (
            [q.shape if isinstance(q, torch.Tensor) else None for q in q_out]
            if isinstance(q_out, list)
            else q_out.shape
        ),
    )
    print("QSAA batch: ", qsaa_out, "Shape: ", qsaa_out.shape)

    print("Discrete Actions Batch Concatenated")
    print(torch.cat(disc_acts_batch, dim=-1))

    print("All actions Batch concatenated")
    print(torch.cat((cont_acts_batch, torch.cat(disc_acts_batch, dim=-1)), dim=-1))
    # Batch of states
    val_sa_batch = value_sa(
        states, torch.cat((cont_acts_batch, torch.cat(disc_acts_batch, dim=-1)), dim=-1)
    )
    val_s_batch = value_s(states)
    q_batch = q_net(torch.cat((states, cont_acts_batch), dim=-1))
    # Test batch of states through QSAA
    qsaa_batch = qsaa_net(states, cont_acts_batch, torch.cat(disc_acts_batch, dim=-1))

    print("\nBatch of states through value networks:")
    print("ValueSA batch output:", val_sa_batch, "Shape:", val_sa_batch.shape)
    print("ValueS batch output:", val_s_batch, "Shape:", val_s_batch.shape)
    print(
        "Q batch output:",
        q_batch,
        "Shape:",
        (
            [q.shape if isinstance(q, torch.Tensor) else None for q in q_batch]
            if isinstance(q_batch, list)
            else q_batch.shape
        ),
    )
    print("QSAA batch: ", qsaa_batch, "Shape: ", qsaa_batch.shape)
