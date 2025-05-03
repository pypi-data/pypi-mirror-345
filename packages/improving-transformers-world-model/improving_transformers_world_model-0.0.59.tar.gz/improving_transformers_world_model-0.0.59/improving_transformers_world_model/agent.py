from __future__ import annotations
from typing import NamedTuple, Deque
from collections import deque

import torch
from torch import nn, cat, stack, is_tensor, tensor, Tensor
from torch.nn import Module, ModuleList, GRU

import torch.nn.functional as F
from torch.utils.data import TensorDataset, ConcatDataset, DataLoader

from einops import rearrange, pack, unpack
from einops.layers.torch import Reduce, Rearrange

from assoc_scan import AssocScan

from improving_transformers_world_model.world_model import (
    WorldModel,
    inputs_to_model_device,
    outputs_to_device
)

from improving_transformers_world_model.tensor_typing import (
    Float,
    Int,
    Bool
)

from hl_gauss_pytorch import HLGaussLayer

from adam_atan2_pytorch import AdoptAtan2

from ema_pytorch import EMA

# helper functions

def exists(v):
    return v is not None

def default(v, d):
    return v if exists(v) else d

def divisible_by(num, den):
    return (num % den) == 0

def is_odd(num):
    return not divisible_by(num, 2)

# tensor helpers

def is_empty(t):
    return t.numel() == 0

def log(t, eps = 1e-20):
    return torch.log(t.clamp(min = eps))

def gumbel_noise(t):
    noise = torch.zeros_like(t).uniform_(0, 1)
    return -log(-log(noise))

def gumbel_sample(t, temperature = 1., dim = -1):
    return ((t / max(temperature, 1e-10)) + gumbel_noise(t)).argmax(dim = dim)

def get_log_prob(logits, indices):
    log_probs = logits.log_softmax(dim = -1)
    indices = rearrange(indices, '... -> ... 1')
    sel_log_probs = log_probs.gather(-1, indices)
    return rearrange(sel_log_probs, '... 1 -> ...')

def calc_entropy(prob, eps = 1e-20, dim = -1):
    return -(prob * log(prob, eps)).sum(dim = dim)

def pack_one(t, pattern):
    packed, ps = pack([t], pattern)

    def inverse(out, inv_pattern = None):
        inv_pattern = default(inv_pattern, pattern)
        return unpack(out, ps, inv_pattern)[0]

    return packed, inverse

# generalized advantage estimate

def calc_target_and_gae(
    rewards: Float['... n'],
    values: Float['... n+1'],
    masks: Bool['... n'],
    gamma = 0.99,
    lam = 0.95,
    use_accelerated = None

) -> tuple[
    Float['... n'],
    Float['... n']
]:

    use_accelerated = default(use_accelerated, rewards.is_cuda)
    device = rewards.device

    rewards, inverse_pack = pack_one(rewards, '* n')
    values, _ = pack_one(values, '* n')
    masks, _ = pack_one(masks, '* n')

    values, values_next = values[:, :-1], values[:, 1:]

    delta = rewards + gamma * values_next * masks - values
    gates = gamma * lam * masks

    scan = AssocScan(reverse = True, use_accelerated = use_accelerated)
    gae = scan(gates, delta)

    returns = gae + values

    gae, returns = tuple(inverse_pack(t) for t in (gae, returns))

    return returns, gae

# FiLM for conditioning policy network on world model embed - suggested for follow up research in the paper

class FiLM(Module):
    def __init__(
        self,
        dim,
        dim_out
    ):
        super().__init__()
        self.to_gamma = nn.Linear(dim, dim_out, bias = False)
        self.to_beta = nn.Linear(dim, dim_out, bias = False)

        nn.init.zeros_(self.to_gamma.weight)
        nn.init.zeros_(self.to_beta.weight)

    def forward(
        self,
        x: Float['... d'],
        cond: Float['... d']
    ):
        gamma, beta = self.to_gamma(cond), self.to_beta(cond)

        return x * (gamma + 1.) + beta

# symbol extractor
# detailed in section C.3

class SymbolExtractor(Module):
    def __init__(
        self,
        *,
        patch_size = 7,
        channels = 3,
        dim = 128,
        dim_output = 145 * 17 # 145 images with 17 symbols per image (i think)
    ):
        super().__init__()
        assert is_odd(patch_size)

        self.net = nn.Sequential(
            nn.Conv2d(channels, dim, patch_size, stride = patch_size, padding = patch_size // 2),
            nn.ReLU(),
            nn.Conv2d(dim, dim, 1),
            nn.ReLU(),
            nn.Conv2d(dim, dim_output, 1)
        )

    def forward(
        self,
        images: Float['b c h w'],
        labels: Int['b ph pw'] | Int['b phw'] | None = None
    ):
        logits = self.net(images)

        return_loss = exists(labels)

        if not return_loss:
            return logits

        loss = F.cross_entropy(
            rearrange(logits, 'b l h w -> b l (h w)'),
            rearrange(labels, 'b ph pw -> b (ph pw)')
        )

        return loss

# classes

class Impala(Module):
    def __init__(
        self,
        *,
        dims = (64, 64, 128),
        image_size = 63,
        channels = 3,
        init_conv_kernel = 7,
        dim_rnn = 32,
        dim_rnn_hidden = 32
    ):
        super().__init__()
        assert is_odd(init_conv_kernel)
        assert len(dims) >= 2

        first_dim, *_, last_dim = dims

        self.init_conv = nn.Conv2d(channels, first_dim, init_conv_kernel, stride = init_conv_kernel)
        self.max_pool = nn.MaxPool2d(kernel_size = 3, stride = 2)

        layers = ModuleList([])

        dim_pairs = zip(dims[:-1], dims[1:])

        for dim_in, dim_out in dim_pairs:

            residual_fn = nn.Conv2d(dim_in, dim_out, 1) if dim_in != dim_out else nn.Identity()

            layer = nn.Sequential(
                nn.InstanceNorm2d(dim_in),
                nn.ReLU(),
                nn.Conv2d(dim_in, dim_out, 3, padding = 1),
            )

            layers.append(ModuleList([residual_fn, layer]))

        self.layers = layers

        # they add a GRU to give the agent memory

        impala_ccn_output_dim = last_dim * (image_size // init_conv_kernel // 2) ** 2

        self.to_rnn = nn.Linear(impala_ccn_output_dim, dim_rnn)

        self.rnn = nn.GRU(dim_rnn, dim_rnn_hidden, batch_first = True)

        self.output_dims = (impala_ccn_output_dim, dim_rnn)

        # device tracking

        self.register_buffer('dummy', tensor(0), persistent = False)

    @property
    def device(self):
        return self.dummy.device

    @inputs_to_model_device
    def forward(
        self,
        state: Float['b c h w'] | Float['b c t h w'],
        gru_hidden = None,
        concat_cnn_rnn_outputs = True
    ):
        is_image = state.ndim == 4

        if is_image:
            state = rearrange(state, 'b c h w -> b c 1 h w')

        state = rearrange(state, 'b c t h w -> b t c h w')
        state, inverse_pack_time = pack_one(state, '* c h w')

        # impala cnn network

        x = self.init_conv(state)
        x = self.max_pool(x)

        for residual_fn, layer_fn in self.layers:
            x = layer_fn(x) + residual_fn(x)

        # fold height and width into feature dimension

        cnn_out = rearrange(x, 'b d h w -> b (h w d)')

        # get back the time dimension for rnn

        cnn_out = inverse_pack_time(cnn_out, '* d')

        rnn_input = self.to_rnn(cnn_out)

        rnn_out, next_gru_hidden = self.rnn(rnn_input, gru_hidden)

        # remove the time dimension if single image frame passed in

        if is_image:
            rnn_out = rearrange(rnn_out, 'b 1 d -> b d')
            cnn_out = rearrange(cnn_out, 'b 1 d -> b d')

        if not concat_cnn_rnn_outputs:
            return cnn_out, rnn_out, next_gru_hidden

        return cat((cnn_out, rnn_out), dim = -1), next_gru_hidden

# actor and critic mlps

class Actor(Module):
    def __init__(
        self,
        dim_input,
        dim,
        *,
        num_actions,
        dim_world_model_embed = None,
        num_layers = 3,
        expansion_factor = 2.,
    ):
        super().__init__()
        self.num_actions = num_actions

        dim_hidden = int(expansion_factor * dim)

        self.proj_in = nn.Linear(dim_input, dim)

        layers = []

        for _ in range(num_layers):
            layer = nn.Sequential(
                nn.Linear(dim, dim_hidden),
                nn.ReLU(),
                nn.Linear(dim_hidden, dim),
            )

            layers.append(layer)

        self.layers = ModuleList(layers)

        self.to_actions_pred = nn.Linear(dim, num_actions)

        # able to condition on world model embed when predicting action - using classic film

        self.can_cond_on_world_model = exists(dim_world_model_embed)

        if self.can_cond_on_world_model:
            self.world_model_film = FiLM(dim_world_model_embed, dim)

    def forward(
        self,
        state: Float['b c h w'],
        world_model_embed: Float['b d'] | None = None,
        sample_action = False
    ) -> (
        Float['b'] |
        tuple[Int['b'], Float['b']]
    ):

        embed = self.proj_in(state)

        if exists(world_model_embed):
            assert self.can_cond_on_world_model, f'`dim_world_model_embed` must be set on `Actor` to utilize world model for prediction'

            embed = self.world_model_film(embed, world_model_embed)

        for layer in self.layers:
            embed = layer(embed) + embed

        action_logits = self.to_actions_pred(embed)

        if not sample_action:
            return action_logits

        actions = gumbel_sample(action_logits, dim = -1)

        log_probs = get_log_prob(action_logits, actions)

        return (actions, log_probs)

class Critic(Module):
    def __init__(
        self,
        dim_input,
        dim,
        *,
        num_layers = 4,
        expansion_factor = 2.,
        use_regression = False,
        hl_gauss_loss_kwargs = dict(
            min_value = 0.,
            max_value = 5.,
            num_bins = 32,
            sigma = 0.5,
        )
    ):
        super().__init__()
        dim_hidden = int(expansion_factor * dim)

        self.proj_in = nn.Linear(dim_input, dim)

        layers = []

        for _ in range(num_layers):
            layer = nn.Sequential(
                nn.Linear(dim, dim_hidden),
                nn.ReLU(),
                nn.Linear(dim_hidden, dim),
            )

            layers.append(layer)

        self.layers = ModuleList(layers)

        self.to_value_pred = HLGaussLayer(
            dim = dim,
            hl_gauss_loss = hl_gauss_loss_kwargs,
            use_regression = use_regression
        )

    def forward(
        self,
        state: Float['b n d'],
        return_value_and_logits = False
    ) -> Float['b'] | Float['']:

        embed = self.proj_in(state)

        for layer in self.layers:
            embed = layer(embed) + embed

        return self.to_value_pred(embed, return_value_and_logits = return_value_and_logits)

# memory

FrameState = Float['c h w']
Scalar = Float['']
Loss = Scalar

class Memory(NamedTuple):
    state:           FrameState
    action:          Int['a']
    action_log_prob: Scalar
    reward:          Scalar
    value:           Scalar
    done:            Bool['']
    world_embed:     Float['d'] | None

class MemoriesWithNextState(NamedTuple):
    memories:               Deque[Memory]
    next_state:             FrameState
    from_real_env:          bool
    has_world_model_embed:  bool

# actor critic agent

class Agent(Module):
    def __init__(
        self,
        impala: Impala | dict,
        actor: Actor | dict,
        critic: Critic | dict,
        actor_eps_clip = 0.2,  # clipping
        actor_beta_s = .01,    # entropy weight
        critic_eps_clip = 0.4, # value clipping
        optim_klass = AdoptAtan2,
        actor_lr = 1e-4,
        critic_lr = 1e-4,
        actor_weight_decay = 1e-3,
        critic_weight_decay = 1e-3,
        max_grad_norm = 0.5,
        actor_optim_kwargs: dict = dict(),
        critic_optim_kwargs: dict = dict(),
        critic_ema_kwargs: dict = dict(),
        max_memories = 128_000,
        standardize_target_momentum = 0.95
    ):
        super().__init__()

        if isinstance(impala, dict):
            impala = Impala(**impala)

        dim_state = sum(impala.output_dims)

        if isinstance(actor, dict):
            actor.update(dim_input = dim_state)
            actor = Actor(**actor)

        if isinstance(critic, dict):
            critic.update(dim_input = dim_state)
            critic = Critic(**critic)

        self.impala = impala
        self.actor = actor
        self.critic = critic

        self.critic_ema = EMA(critic, **critic_ema_kwargs)

        self.actor_eps_clip = actor_eps_clip
        self.actor_beta_s = actor_beta_s

        self.critic_eps_clip = critic_eps_clip

        self.max_grad_norm = max_grad_norm

        self.actor_optim = optim_klass((*actor.parameters(), *impala.parameters()), lr = actor_lr, weight_decay = actor_weight_decay, **actor_optim_kwargs)
        self.critic_optim = optim_klass((*critic.parameters(), *impala.parameters()), lr = critic_lr, weight_decay = critic_weight_decay, **critic_optim_kwargs)

        # use a batch norm for standardizing the target - section A.1.2 in paper

        self.batchnorm_target = nn.Sequential(
            Rearrange('b -> b 1 1'),
            nn.BatchNorm1d(1, momentum = standardize_target_momentum, affine = False),
            Rearrange('b 1 1 -> b'),
        )

        # memories

        self.max_memories = max_memories

        self.register_buffer('dummy', tensor(0))

    @property
    def device(self):
        return self.dummy.device

    def policy_loss(
        self,
        states: Float['b c h w'],
        actions: Int['b'],
        old_log_probs: Float['b'],
        values: Float['b'],
        returns: Float['b'],
        world_model_embeds: Float['b d'] | None = None
    ) -> Loss:

        self.actor.train()

        batch = values.shape[0]
        advantages = F.layer_norm(returns - values, (batch,))

        actor_critic_input, _ = self.impala(states)
        action_logits = self.actor(actor_critic_input, world_model_embed = world_model_embeds)

        prob = action_logits.softmax(dim = -1)

        log_probs = get_log_prob(action_logits, actions)

        ratios = (log_probs - old_log_probs).exp()

        # ppo clipped surrogate objective

        clip = self.actor_eps_clip

        surr1 = ratios * advantages
        surr2 = ratios.clamp(1. - clip, 1. + clip) * advantages

        action_entropy = calc_entropy(prob) # encourage exploration
        policy_loss = torch.min(surr1, surr2) - self.actor_beta_s * action_entropy

        return policy_loss

    def critic_loss(
        self,
        states: Float['b c h w'],
        old_values: Float['b'],
        returns: Float['b']
    ) -> Loss:

        eps = self.critic_eps_clip
        loss_fn = self.critic.to_value_pred.loss_fn

        self.critic.train()

        actor_critic_input, _ = self.impala(states)

        critic_value, critic_logits = self.critic(actor_critic_input, return_value_and_logits = True)

        # value clipping

        clipped_value = old_values + (critic_value - old_values).clamp(-eps, eps)

        clipped_loss = loss_fn(clipped_value, returns, reduction = 'none')
        loss = loss_fn(critic_logits, returns, reduction = 'none')

        return torch.max(clipped_loss, loss).mean()

    def learn(
        self,
        memories: MemoriesWithNextState | list[MemoriesWithNextState],
        lam = 0.95,
        gamma = 0.99,
        batch_size = 16,
        epochs = 2

    ) -> tuple[Loss, ...]:

        if isinstance(memories, MemoriesWithNextState):
            memories = [memories]

        assert len({one_memory.has_world_model_embed for one_memory in memories}) == 1, 'memories must either all use world embed or not'

        datasets = []

        for one_memories, next_state, from_real_env, _ in memories:

            with torch.no_grad():
                self.critic.eval()

                next_state = rearrange(next_state, 'c 1 h w -> 1 c h w')
                next_state = next_state.to(self.device)

                actor_critic_input, _ = self.impala(next_state)
                next_value = self.critic(actor_critic_input)

                next_value = next_value.cpu()

            (
                states,
                actions,
                action_log_probs,
                rewards,
                values,
                dones,
                world_model_embeds
            ) = map(stack, zip(*list(one_memories)))

            values_with_next = cat((values, next_value), dim = 0)

            # generalized advantage estimate

            mask = 1. - dones.float()

            returns, gae = calc_target_and_gae(rewards, values_with_next, mask, lam = lam, gamma = gamma)

            # memories dataset for updating actor and critic learning

            dataset = TensorDataset(states, actions, action_log_probs, returns, values, dones, world_model_embeds)

            datasets.append(dataset)

        # dataset and dataloader

        datasets = ConcatDataset(datasets)

        dataloader = DataLoader(datasets, batch_size = batch_size, shuffle = True)

        # training

        self.train()

        for epoch in range(epochs):

            for batched_data in dataloader:

                (
                    states,
                    actions,
                    action_log_probs,
                    returns,
                    values,
                    dones,
                    world_model_embeds
                ) = tuple(t.to(self.device) for t in batched_data)

                returns = self.batchnorm_target(returns)

                # update actor

                actor_loss = self.policy_loss(
                    states = states,
                    actions = actions,
                    old_log_probs = action_log_probs,
                    values = values,
                    returns = returns,
                    world_model_embeds = world_model_embeds if not is_empty(world_model_embeds) else None
                )

                actor_loss.mean().backward()

                nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)

                self.actor_optim.step()
                self.actor_optim.zero_grad()

                # update critic

                critic_loss = self.critic_loss(
                    states = states,
                    old_values = values,
                    returns = returns
                )

                critic_loss.mean().backward()

                nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)

                self.critic_optim.step()
                self.critic_optim.zero_grad()

                self.critic_ema.update()

    @torch.no_grad()
    def interact_with_env(
        self,
        env,
        memories: Memories | None = None,
        world_model: WorldModel | None = None,
        max_steps = float('inf')

    ) -> MemoriesWithNextState:

        device = self.device

        memories = default(memories, [])

        to_device_decorator = outputs_to_device(self.device)

        next_state = to_device_decorator(env.reset)()

        # prepare for looping with world model
        # gathering up all the memories of states, actions, rewards for training

        actions = torch.empty((1, 0, 1), device = device, dtype = torch.long)
        action_log_probs = torch.empty((1, 0), device = device, dtype = torch.float32)

        states = rearrange(next_state, 'c h w -> 1 c 1 h w')

        rewards = torch.zeros((1, 1), device = device, dtype = torch.float32)
        dones = tensor([[False]], device = device)

        last_done = dones[0, -1]
        time_step = states.shape[2] + 1

        # maybe conditioning actor with learned world model embed

        world_model_dim = world_model.dim if exists(world_model) else 0
        world_model_embeds = torch.empty((1, 0, world_model_dim), device = device, dtype = torch.float32)

        if exists(world_model):
            world_model_cache = None

        while time_step < max_steps and not last_done:

            world_model_embed = None

            if exists(world_model):
                with torch.no_grad():
                    world_model.eval()

                    world_model_embed, world_model_cache = world_model(
                        state_or_token_ids = states[:, :, -1:],
                        actions = actions[:, -1:],
                        rewards = rewards[:, -1:],
                        cache = world_model_cache,
                        remove_cache_len_from_time = False,
                        return_embed = True,
                        return_cache = True,
                        return_loss = False
                    )

                    world_model_embed = rearrange(world_model_embed, '1 1 d -> 1 d')

            # impala + actor - todo: cleanup the noisy tensor (un)squeezing ops

            next_state = rearrange(next_state, 'c h w -> 1 c h w')

            actor_critic_input, rnn_hidden = self.impala(next_state)

            action, action_log_prob = self.actor(actor_critic_input, world_model_embed = world_model_embed, sample_action = True)

            next_state, next_reward, next_done = to_device_decorator(env)(action)

            action = rearrange(action, '1 -> 1 1 1')
            action_log_prob = rearrange(action_log_prob, '1 -> 1 1')

            actions = cat((actions, action), dim = 1)
            action_log_probs = cat((action_log_probs, action_log_prob), dim = 1)

            next_state_to_append = rearrange(next_state, 'c h w -> 1 c 1 h w')
            states = cat((states, next_state_to_append), dim = 2)

            next_reward = rearrange(next_reward, '1 -> 1 1')
            rewards = cat((rewards, next_reward), dim = -1)

            next_done = rearrange(next_done, '1 -> 1 1')
            dones = cat((dones, next_done), dim = -1)

            if exists(world_model_embed):
                next_embed = rearrange(world_model_embed, '... -> 1 ...')
                world_model_embeds = cat((world_model_embeds, next_embed), dim = 1)
            else:
                world_model_embeds = world_model_embeds.reshape(1, time_step + 1, 0)

            time_step += 1
            last_done = dones[0, -1]

        # calculate value from critic all at once before storing to memory

        actor_critic_input, _ = self.impala(states)

        values = self.critic(actor_critic_input)

        # move all intermediates to cpu and detach and store into memory for learning actor and critic

        states, actions, action_log_probs, rewards, values, dones, world_model_embeds = tuple(rearrange(t, '1 ... -> ...').cpu() for t in (states, actions, action_log_probs, rewards, values, dones, world_model_embeds))

        states, next_state = states[:, :-1], states[:, -1:]

        rewards = rewards[:-1]
        values = values[:-1]
        dones = dones[:-1]

        episode_memories = tuple(Memory(*timestep_tensors) for timestep_tensors in zip(
            rearrange(states, 'c t h w -> t c h w'),
            rearrange(actions, '... 1 -> ...'), # fix for multi-actions later
            action_log_probs,
            rewards,
            values,
            dones,
            world_model_embeds
        ))

        memories.extend(episode_memories)

        return MemoriesWithNextState(memories, next_state, from_real_env = True, has_world_model_embed = exists(world_model))

    @torch.no_grad()
    @inputs_to_model_device
    def forward(
        self,
        world_model: WorldModel,
        init_state: FrameState,
        memories: Memories | None = None,
        max_steps = float('inf'),
        use_world_model_embed = False
    ) -> MemoriesWithNextState:

        device = init_state.device

        assert world_model.num_actions == self.actor.num_actions

        memories = default(memories, deque([], maxlen = self.max_memories))

        next_state = rearrange(init_state, 'c h w -> 1 c h w')

        # prepare for looping with world model
        # gathering up all the memories of states, actions, rewards for training

        actions = torch.empty((1, 0, 1), device = device, dtype = torch.long)
        action_log_probs = torch.empty((1, 0), device = device, dtype = torch.float32)

        states = rearrange(next_state, '1 c h w -> 1 c 1 h w')

        rewards = torch.zeros((1, 1), device = device, dtype = torch.float32)
        dones = tensor([[False]], device = device)

        last_done = dones[0, -1]
        time_step = states.shape[2] + 1

        world_model_dim = world_model.dim if use_world_model_embed else 0
        world_model_embeds = torch.empty((1, 0, world_model_dim), device = device, dtype = torch.float32)

        world_model_cache = None

        while time_step < max_steps and not last_done:

            world_model_embed = None

            if use_world_model_embed:
                with torch.no_grad():
                    world_model.eval()

                    world_model_embed, _ = world_model(
                        state_or_token_ids = states[:, :, -1:],
                        actions = actions[:, -1:],
                        rewards = rewards[:, -1:],
                        cache = world_model_cache,
                        remove_cache_len_from_time = False,
                        return_embed = True,
                        return_cache = True,
                        return_loss = False
                    )

                    world_model_embed = rearrange(world_model_embed, '1 1 d -> 1 d')

            actor_critic_input, rnn_hiddens = self.impala(next_state)

            action, action_log_prob = self.actor(actor_critic_input, world_model_embed = world_model_embed, sample_action = True)

            action = rearrange(action, 'b -> b 1 1')
            action_log_prob = rearrange(action_log_prob, 'b -> b 1')

            actions = cat((actions, action), dim = 1)
            action_log_probs = cat((action_log_probs, action_log_prob), dim = 1)

            if exists(world_model_embed):
                next_embed = rearrange(world_model_embed, '... -> 1 ...')
                world_model_embeds = cat((world_model_embeds, next_embed), dim = 1)
            else:
                world_model_embeds = world_model_embeds.reshape(1, time_step + 1, 0)

            (states, rewards, dones), world_model_cache = world_model.sample(
                prompt = states,
                actions = actions,
                rewards = rewards,
                time_steps = time_step,
                return_rewards_and_done = True,
                return_cache = True,
                cache = world_model_cache
            )

            time_step += 1
            last_done = dones[0, -1]

        # calculate value from critic all at once before storing to memory

        actor_critic_input, _ = self.impala(states)

        values = self.critic_ema(actor_critic_input)

        # move all intermediates to cpu and detach and store into memory for learning actor and critic

        states, actions, action_log_probs, rewards, values, dones, world_model_embeds = tuple(rearrange(t, '1 ... -> ...').cpu() for t in (states, actions, action_log_probs, rewards, values, dones, world_model_embeds))

        states, next_state = states[:, :-1], states[:, -1:]

        rewards = rewards[:-1]
        values = values[:-1]
        dones = dones[:-1]

        episode_memories = tuple(Memory(*timestep_tensors) for timestep_tensors in zip(
            rearrange(states, 'c t h w -> t c h w'),
            rearrange(actions, '... 1 -> ...'), # fix for multi-actions later
            action_log_probs,
            rewards,
            values,
            dones,
            world_model_embeds
        ))

        memories.extend(episode_memories)

        return MemoriesWithNextState(memories, next_state, from_real_env = False, has_world_model_embed = use_world_model_embed)
