from polyfactory.factories.pydantic_factory import ModelFactory

from c4.converters.json.schemas.diagrams.system_context import (
    EnterpriseBoundarySchema,
    PersonExtSchema,
    PersonSchema,
    SystemBoundarySchema,
    SystemDbExtSchema,
    SystemDbSchema,
    SystemExtSchema,
    SystemQueueExtSchema,
    SystemQueueSchema,
    SystemSchema,
)


class PersonSchemaFactory(ModelFactory[PersonSchema]):
    __model__ = PersonSchema

    type = "Person"
    label = "Customer"
    alias = "customer"
    stereotype = "External user"
    description = "Uses the system to place orders."
    sprite = "person"
    tags = ["external"]
    link = "https://example.com/customer"
    properties = {
        "properties": [["Role", "Customer"]],
    }


class PersonExtSchemaFactory(ModelFactory[PersonExtSchema]):
    __model__ = PersonExtSchema

    type = "PersonExt"
    label = "Customer"
    alias = "customer"
    stereotype = "External user"
    description = "Uses the system to place orders."
    sprite = "person"
    tags = ["external"]
    link = "https://example.com/customer"
    properties = {
        "properties": [["Role", "Customer"]],
    }


class SystemSchemaFactory(ModelFactory[SystemSchema]):
    __model__ = SystemSchema

    type = "System"
    label = "Online Shop"
    alias = "shop"
    description = (
        "Allows customers to browse products, manage carts, and place orders."
    )
    stereotype = "Software System"
    base_shape = "RoundedBox"
    technology = "Python + PostgreSQL"
    tags = ["system", "core"]
    link = "https://shop.example.com"
    properties = {
        "properties": [
            ["Domain", "Commerce"],
            ["Criticality", "High"],
        ],
    }


class SystemExtSchemaFactory(ModelFactory[SystemExtSchema]):
    __model__ = SystemExtSchema

    type = "SystemExt"
    label = "Payment Provider"
    alias = "payment_provider"
    description = "Processes card payments and sends payment webhooks."
    stereotype = "External System"
    base_shape = "RoundedBox"
    technology = "REST API + Webhooks"
    tags = ["system", "external"]
    link = "https://payments.example.com"
    properties = {
        "properties": [
            ["Role", "Payments"],
            ["Ownership", "Vendor"],
        ],
    }


class SystemDbSchemaFactory(ModelFactory[SystemDbSchema]):
    __model__ = SystemDbSchema

    type = "SystemDb"
    label = "Orders DB"
    alias = "orders_db"
    description = "Stores orders, payments, and shipment state."
    stereotype = "Database"
    technology = "PostgreSQL"
    tags = ["database", "internal"]
    link = "https://dbadmin.example.com/orders"
    properties = {
        "properties": [
            ["Engine", "PostgreSQL"],
            ["Contains", "Orders"],
        ],
    }


class SystemDbExtSchemaFactory(ModelFactory[SystemDbExtSchema]):
    __model__ = SystemDbExtSchema

    type = "SystemDbExt"
    label = "Fraud Signals DB"
    alias = "fraud_db"
    description = (
        "External repository with fraud signals and device fingerprints."
    )
    stereotype = "External Database"
    technology = "Vendor DB"
    tags = ["database", "external"]
    link = "https://fraud.example.com"
    properties = {
        "properties": [
            ["Engine", "Vendor DB"],
            ["Contains", "Fraud Signals"],
        ],
    }


class SystemQueueSchemaFactory(ModelFactory[SystemQueueSchema]):
    __model__ = SystemQueueSchema

    type = "SystemQueue"
    label = "Order Events"
    alias = "order_events"
    description = "Event stream for order lifecycle events."
    stereotype = "Queue"
    technology = "Kafka"
    tags = ["queue", "internal"]
    link = "https://kafka.example.com/topics/order-events"
    properties = {
        "properties": [
            ["Broker", "Kafka"],
            ["Topic", "order-events"],
        ],
    }


class SystemQueueExtSchemaFactory(ModelFactory[SystemQueueExtSchema]):
    __model__ = SystemQueueExtSchema

    type = "SystemQueueExt"
    label = "Partner Topic"
    alias = "partner_topic"
    description = "External event topic provided by a logistics partner."
    stereotype = "External Queue"
    technology = "Kafka"
    tags = ["queue", "external"]
    link = "https://partner.example.com/topics"
    properties = {
        "properties": [
            ["Broker", "Kafka"],
            ["Owner", "Logistics Partner"],
        ],
    }


class EnterpriseBoundarySchemaFactory(ModelFactory[EnterpriseBoundarySchema]):
    __model__ = EnterpriseBoundarySchema

    type = "EnterpriseBoundary"
    label = "ACME Corp"
    alias = "acme"
    description = "Internal enterprise boundary."
    stereotype = "Enterprise Boundary"
    tags = ["enterprise"]
    elements = [
        PersonSchemaFactory.build(),
        SystemSchemaFactory.build(),
        SystemDbSchemaFactory.build(),
        SystemQueueSchemaFactory.build(),
    ]
    boundaries = []
    relationships = []


class SystemBoundarySchemaFactory(ModelFactory[SystemBoundarySchema]):
    __model__ = SystemBoundarySchema

    type = "SystemBoundary"
    label = "Online Shop Platform"
    stereotype = "System Boundary"
    alias = "shop_boundary"
    description = "Boundary around the shop system and its components."
    tags = ["system_boundary"]
    elements = [
        SystemSchemaFactory.build(),
        SystemDbSchemaFactory.build(),
        SystemQueueSchemaFactory.build(),
    ]
    boundaries = []
    relationships = []
