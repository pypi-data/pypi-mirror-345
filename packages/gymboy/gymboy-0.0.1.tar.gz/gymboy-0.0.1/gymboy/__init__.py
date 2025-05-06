"""GymBoy: A library for creating and registering PyBoy environments as Gym environments."""

from gymboy.registration import make, make_vec, registered_envs


__all__ = ["make", "make_vec", "registered_envs"]
