# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import override

from . import resources, _load_client
from ._utils import LazyProxy


class ModelsResourceProxy(LazyProxy[resources.ModelsResource]):
    @override
    def __load__(self) -> resources.ModelsResource:
        return _load_client().models


class AccountResourceProxy(LazyProxy[resources.AccountResource]):
    @override
    def __load__(self) -> resources.AccountResource:
        return _load_client().account


class HardwareResourceProxy(LazyProxy[resources.HardwareResource]):
    @override
    def __load__(self) -> resources.HardwareResource:
        return _load_client().hardware


class WebhooksResourceProxy(LazyProxy[resources.WebhooksResource]):
    @override
    def __load__(self) -> resources.WebhooksResource:
        return _load_client().webhooks


class TrainingsResourceProxy(LazyProxy[resources.TrainingsResource]):
    @override
    def __load__(self) -> resources.TrainingsResource:
        return _load_client().trainings


class CollectionsResourceProxy(LazyProxy[resources.CollectionsResource]):
    @override
    def __load__(self) -> resources.CollectionsResource:
        return _load_client().collections


class DeploymentsResourceProxy(LazyProxy[resources.DeploymentsResource]):
    @override
    def __load__(self) -> resources.DeploymentsResource:
        return _load_client().deployments


class PredictionsResourceProxy(LazyProxy[resources.PredictionsResource]):
    @override
    def __load__(self) -> resources.PredictionsResource:
        return _load_client().predictions


models: resources.ModelsResource = ModelsResourceProxy().__as_proxied__()
account: resources.AccountResource = AccountResourceProxy().__as_proxied__()
hardware: resources.HardwareResource = HardwareResourceProxy().__as_proxied__()
webhooks: resources.WebhooksResource = WebhooksResourceProxy().__as_proxied__()
trainings: resources.TrainingsResource = TrainingsResourceProxy().__as_proxied__()
collections: resources.CollectionsResource = CollectionsResourceProxy().__as_proxied__()
deployments: resources.DeploymentsResource = DeploymentsResourceProxy().__as_proxied__()
predictions: resources.PredictionsResource = PredictionsResourceProxy().__as_proxied__()
