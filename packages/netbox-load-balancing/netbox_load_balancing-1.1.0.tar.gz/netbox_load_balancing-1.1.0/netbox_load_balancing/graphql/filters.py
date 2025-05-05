from typing import Annotated
import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from netbox.graphql.filter_lookups import IntegerArrayLookup
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from ipam.graphql.filters import IPAddressFilter
from .enums import (
    NetBoxLoadBalancingHealthMonitorTypeEnum,
    NetBoxLoadBalancingHealthMonitorHTTPVersionEnum,
    NetBoxLoadBalancingPoolAlgorythmEnum,
    NetBoxLoadBalancingPoolSessionPersistenceEnum,
    NetBoxLoadBalancingPoolBackupSessionPersistenceEnum,
    NetBoxLoadBalancingListenerProtocolEnum,
)

from netbox_load_balancing.models import (
    LBService,
    Listener,
    HealthMonitor,
    Pool,
    Member,
    VirtualIPPool,
    VirtualIP,
)


@strawberry_django.filter(LBService, lookups=True)
class NetBoxLoadBalancingLBServiceFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    reference: FilterLookup[str] | None = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(Listener, lookups=True)
class NetBoxLoadBalancingListenerFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    service: (
        Annotated[
            "NetBoxLoadBalancingLBServiceFilter",
            strawberry.lazy("netbox_load_balancing.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    port: FilterLookup[int] | None = strawberry_django.filter_field()
    protocol: (
        Annotated[
            "NetBoxLoadBalancingListenerProtocolEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    source_nat: FilterLookup[bool] | None = strawberry_django.filter_field()
    use_proxy_port: FilterLookup[bool] | None = strawberry_django.filter_field()
    max_clients: FilterLookup[int] | None = strawberry_django.filter_field()
    max_requests: FilterLookup[int] | None = strawberry_django.filter_field()
    client_timeout: FilterLookup[int] | None = strawberry_django.filter_field()
    server_timeout: FilterLookup[int] | None = strawberry_django.filter_field()
    client_keepalive: FilterLookup[bool] | None = strawberry_django.filter_field()
    surge_protection: FilterLookup[bool] | None = strawberry_django.filter_field()
    tcp_buffering: FilterLookup[bool] | None = strawberry_django.filter_field()
    compression: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(HealthMonitor, lookups=True)
class NetBoxLoadBalancingHealthMonitorFilter(
    ContactFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    template: FilterLookup[str] | None = strawberry_django.filter_field()
    type: (
        Annotated[
            "NetBoxLoadBalancingHealthMonitorTypeEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    monitor_url: FilterLookup[str] | None = strawberry_django.filter_field()
    http_response: FilterLookup[str] | None = strawberry_django.filter_field()
    monitor_host: FilterLookup[str] | None = strawberry_django.filter_field()
    monitor_port: FilterLookup[int] | None = strawberry_django.filter_field()
    http_version: (
        Annotated[
            "NetBoxLoadBalancingHealthMonitorHTTPVersionEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    http_secure: FilterLookup[bool] | None = strawberry_django.filter_field()
    http_response_codes: (
        Annotated[
            "IntegerArrayLookup", strawberry.lazy("netbox.graphql.filter_lookups")
        ]
        | None
    ) = strawberry_django.filter_field()
    probe_interval: FilterLookup[int] | None = strawberry_django.filter_field()
    response_timeout: FilterLookup[int] | None = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(Pool, lookups=True)
class NetBoxLoadBalancingPoolFilter(ContactFilterMixin, NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    listeners: (
        Annotated[
            "NetBoxLoadBalancingListenerFilter",
            strawberry.lazy("netbox_load_balancing.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    algorythm: (
        Annotated[
            "NetBoxLoadBalancingPoolAlgorythmEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    session_persistence: (
        Annotated[
            "NetBoxLoadBalancingPoolSessionPersistenceEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    backup_persistence: (
        Annotated[
            "NetBoxLoadBalancingPoolBackupSessionPersistenceEnum",
            strawberry.lazy("netbox_load_balancing.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    persistence_timeout: FilterLookup[int] | None = strawberry_django.filter_field()
    backup_timeout: FilterLookup[int] | None = strawberry_django.filter_field()
    member_port: FilterLookup[int] | None = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(Member, lookups=True)
class NetBoxLoadBalancingMemberFilter(ContactFilterMixin, NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    reference: FilterLookup[str] | None = strawberry_django.filter_field()
    ip_address: (
        Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(VirtualIPPool, lookups=True)
class NetBoxLoadBalancingVirtualIPPoolFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(VirtualIP, lookups=True)
class NetBoxLoadBalancingVirtualIPFilter(ContactFilterMixin, NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    dns_name: FilterLookup[str] | None = strawberry_django.filter_field()
    disabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    virtual_pool: (
        Annotated[
            "NetBoxLoadBalancingVirtualIPPoolFilter",
            strawberry.lazy("netbox_load_balancing.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    address: (
        Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    route_health_injection: FilterLookup[bool] | None = strawberry_django.filter_field()
