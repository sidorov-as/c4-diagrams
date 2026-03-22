from c4 import (
    Container,
    ContainerDb,
    ContainerExt,
    ContainerQueue,
    DeploymentDiagram,
    DeploymentNode,
    DeploymentNodeLeft,
    DeploymentNodeRight,
    LayD,
    LayR,
    Node,
    NodeLeft,
    NodeRight,
    Person,
    Rel,
)
from c4.renderers import RenderOptions
from c4.renderers.plantuml import LayoutOptions

with DeploymentDiagram(title="Online Shop - Production Deployment") as diagram:
    customer = Person(
        "Customer",
        "Uses the online shop through a browser.",
        tags=["person"],
        alias="customer",
    )
    payment_gateway = ContainerExt(
        "Payment Gateway",
        "External service that processes card payments.",
        tags=["external_service"],
        technology="HTTPS API",
        alias="payment_gateway",
    )
    with Node(
        "AWS Production Account",
        "Production cloud account for the online shop.",
        type_="Cloud Account",
        tags=["cloud_account"],
        alias="aws_prod",
    ):
        with NodeLeft(
            "Public Subnet",
            "Internet-facing network segment.",
            type_="Network Segment",
            tags=["public_network"],
            alias="public_subnet",
        ):
            with DeploymentNodeLeft(
                "Application Load Balancer",
                "Terminates TLS and routes requests to the web tier.",
                type_="Ingress",
                tags=["edge_node"],
                alias="alb",
            ) as alb:
                web_app = Container(
                    "Web Application",
                    "Serves the storefront UI.",
                    tags=["frontend"],
                    technology="Next.js",
                    alias="web_app",
                )

        with NodeRight(
            "Private Subnet",
            "Internal network segment for application and data services.",
            type_="Network Segment",
            tags=["private_network"],
            alias="private_subnet",
        ):
            with DeploymentNode(
                "Kubernetes Cluster",
                "Runs backend services and asynchronous workers.",
                type_="Runtime Environment",
                tags=["runtime_node"],
                alias="app_cluster",
            ) as app_cluster:
                backend_api = Container(
                    "Backend API",
                    "Handles catalog, checkout, and order processing.",
                    tags=["backend"],
                    technology="Python / FastAPI",
                    alias="backend_api",
                )
                order_events = ContainerQueue(
                    "Order Events",
                    "Internal asynchronous event stream.",
                    tags=["message_bus"],
                    technology="Kafka",
                    alias="order_events",
                )

            with DeploymentNodeRight(
                "Managed PostgreSQL",
                "Managed relational database service.",
                type_="Data Platform",
                tags=["data_node"],
                alias="db_service",
            ) as db_service:
                orders_db = ContainerDb(
                    "Orders Database",
                    "Stores orders, payments, and fulfillment data.",
                    tags=["database"],
                    technology="PostgreSQL",
                    alias="orders_db",
                )

    (
        customer
        >> Rel("Uses", technology="HTTPS", tags=["encrypted_traffic"])
        >> alb
    )
    (
        alb
        >> Rel(
            "Routes traffic to", technology="HTTPS", tags=["encrypted_traffic"]
        )
        >> app_cluster
    )
    (
        app_cluster
        >> Rel(
            "Reads and writes",
            technology="TLS / SQL",
            tags=["encrypted_traffic"],
        )
        >> db_service
    )
    (
        app_cluster
        >> Rel("Calls", technology="HTTPS/JSON", tags=["encrypted_traffic"])
        >> payment_gateway
    )
    (
        backend_api
        >> Rel("Publishes events to", technology="Kafka", tags=["async_flow"])
        >> order_events
    )
    LayR(customer, alb)
    LayR(alb, app_cluster)
    LayD(app_cluster, db_service)
    LayR(app_cluster, payment_gateway)


plantuml_layout_options = (
    LayoutOptions()
    .layout_left_right(
        with_legend=True,
    )
    .show_legend(
        hide_stereotype=False,
        details="Normal",
    )
    .update_legend_title(
        "Deployment Legend",
    )
    .show_person_outline()
    .show_person_sprite(
        "person",
    )
    .add_person_tag(
        tag_stereo="person",
        bg_color="#e8f5e9",
        font_color="#1b5e20",
        border_color="#66bb6a",
        shadowing=False,
        legend_text="End user",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_external_container_tag(
        tag_stereo="external_service",
        bg_color="#f3e5f5",
        font_color="#4a148c",
        border_color="#ab47bc",
        shadowing=False,
        legend_text="External service",
        border_style="DashedLine",
        border_thickness="2",
    )
    .add_container_tag(
        tag_stereo="frontend",
        bg_color="#e3f2fd",
        font_color="#0d47a1",
        border_color="#42a5f5",
        shadowing=False,
        legend_text="Frontend container",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_container_tag(
        tag_stereo="backend",
        bg_color="#ede7f6",
        font_color="#311b92",
        border_color="#7e57c2",
        shadowing=False,
        legend_text="Backend container",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_container_tag(
        tag_stereo="database",
        bg_color="#fff3e0",
        font_color="#e65100",
        border_color="#fb8c00",
        shadowing=False,
        legend_text="Database container",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_container_tag(
        tag_stereo="message_bus",
        bg_color="#fce4ec",
        font_color="#880e4f",
        border_color="#ec407a",
        shadowing=False,
        legend_text="Message queue / stream",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_node_tag(
        tag_stereo="cloud_account",
        bg_color="#eef6ff",
        font_color="#0d47a1",
        border_color="#64b5f6",
        shadowing=True,
        shape="RoundedBoxShape",
        technology="Infrastructure",
        legend_text="Cloud account boundary",
        legend_sprite="cloud",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_node_tag(
        tag_stereo="public_network",
        bg_color="#f1f8e9",
        font_color="#33691e",
        border_color="#8bc34a",
        shadowing=False,
        shape="RoundedBoxShape",
        technology="DMZ",
        legend_text="Public network zone",
        legend_sprite="network",
        border_style="SolidLine",
        border_thickness="1",
    )
    .add_node_tag(
        tag_stereo="private_network",
        bg_color="#fbe9e7",
        font_color="#bf360c",
        border_color="#ff8a65",
        shadowing=False,
        shape="RoundedBoxShape",
        technology="Internal",
        legend_text="Private network zone",
        legend_sprite="network",
        border_style="SolidLine",
        border_thickness="1",
    )
    .add_node_tag(
        tag_stereo="edge_node",
        bg_color="#e1f5fe",
        font_color="#01579b",
        border_color="#29b6f6",
        shadowing=False,
        shape="RoundedBoxShape",
        technology="Ingress",
        legend_text="Ingress deployment node",
        legend_sprite="router",
        border_style="BoldLine",
        border_thickness="2",
    )
    .add_node_tag(
        tag_stereo="runtime_node",
        bg_color="#e8f5e9",
        font_color="#1b5e20",
        border_color="#66bb6a",
        shadowing=True,
        shape="RoundedBoxShape",
        technology="Runtime",
        legend_text="Runtime deployment node",
        legend_sprite="server",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_node_tag(
        tag_stereo="data_node",
        bg_color="#fff8e1",
        font_color="#ff6f00",
        border_color="#ffb300",
        shadowing=False,
        shape="RoundedBoxShape",
        technology="Data Platform",
        legend_text="Data deployment node",
        legend_sprite="database",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_rel_tag(
        tag_stereo="encrypted_traffic",
        text_color="#0d47a1",
        line_color="#1976d2",
        technology="TLS",
        legend_text="Encrypted communication",
        legend_sprite="lock",
        line_style="SolidLine",
        line_thickness="2",
    )
    .add_rel_tag(
        tag_stereo="async_flow",
        text_color="#4a148c",
        line_color="#8e24aa",
        technology="Kafka",
        legend_text="Asynchronous event flow",
        legend_sprite="queue",
        line_style="DashedLine",
        line_thickness="2",
    )
    .update_rel_style(
        text_color="#37474f",
        line_color="#546e7a",
    )
    .build()
)

render_options = RenderOptions(
    plantuml=plantuml_layout_options,
)

diagram.render_options = render_options
