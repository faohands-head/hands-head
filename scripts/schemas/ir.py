"""
IR Schema v1.0 — Intermediate Representation for Mini-Base44
Total: ~200 tokens serializado (vs ~8K tokens de código bruto = 97% menos)
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Field:
    name: str
    type: str = "string"
    required: bool = False
    unique: bool = False
    default: any = None
    relation: Optional[str] = None


@dataclass
class Entity:
    name: str
    fields: list[Field] = field(default_factory=list)
    timestamps: bool = True


@dataclass
class Component:
    type: str = "hero"
    props: dict = field(default_factory=dict)


@dataclass
class Section:
    id: str = "main"
    components: list[Component] = field(default_factory=list)


@dataclass
class Page:
    route: str = "/"
    title: str = "Home"
    layout: str = "public"
    sections: list[Section] = field(default_factory=list)


@dataclass
class DataSource:
    type: str = "static"
    config: dict = field(default_factory=dict)


@dataclass
class Auth:
    provider: str = "none"
    pages: list[str] = field(default_factory=lambda: ["/login", "/register"])
    entities: list[str] = field(default_factory=list)


DEFAULT_NAV = [
    {"icon": "Home", "label": "Inicio", "route": "/"},
    {"icon": "Briefcase", "label": "Servicos", "route": "/servicos"},
    {"icon": "CreditCard", "label": "Planos", "route": "/planos"},
    {"icon": "Headphones", "label": "Suporte", "route": "/suporte"},
    {"icon": "User", "label": "Conta", "route": "/conta"},
]


@dataclass
class AppIR:
    name: str = "App"
    description: str = ""
    pages: list[Page] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    datasource: DataSource = field(default_factory=DataSource)
    auth: Auth = field(default_factory=Auth)
    theme: dict = field(default_factory=lambda: {"primary": "#3b82f6", "radius": "0.5rem"})
    # WebsiteApp / FAO HANDS extensions (IR v1.0.0)
    ir_version: str = "1.0.0"
    app_type: str = "websiteapp"
    url: str = ""
    client: str = ""
    navigation: list = field(default_factory=list)
    source_texts: list = field(default_factory=list)
    websiteapp_sections: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict):
        def _dict_to_field(f: dict) -> Field:
            return Field(**{k: v for k, v in f.items() if k in Field.__dataclass_fields__})

        def _dict_to_component(c: dict) -> Component:
            return Component(type=c.get("type", "hero"), props=c.get("props", {}))

        def _dict_to_section(s: dict) -> Section:
            return Section(
                id=s.get("id", "main"),
                components=[_dict_to_component(c) for c in s.get("components", [])]
            )

        def _dict_to_page(p: dict) -> Page:
            return Page(
                route=p.get("route", "/"),
                title=p.get("title", "Page"),
                layout=p.get("layout", "public"),
                sections=[_dict_to_section(s) for s in p.get("sections", [])]
            )

        def _dict_to_entity(e: dict) -> Entity:
            return Entity(
                name=e.get("name", ""),
                fields=[_dict_to_field(f) for f in e.get("fields", [])],
                timestamps=e.get("timestamps", True)
            )

        return cls(
            name=d.get("name", "App"),
            description=d.get("description", ""),
            pages=[_dict_to_page(p) for p in d.get("pages", [])],
            entities=[_dict_to_entity(e) for e in d.get("entities", [])],
            datasource=DataSource(**d.get("datasource", {"type": "static"})),
            auth=Auth(**{k: v for k, v in d.get("auth", {}).items() if k in Auth.__dataclass_fields__}),
            theme={**{"primary": "#3b82f6", "radius": "0.5rem"}, **d.get("theme", {})},
            ir_version=d.get("ir_version", "1.0.0"),
            app_type=d.get("app_type", "websiteapp"),
            url=d.get("url", ""),
            client=d.get("client", ""),
            navigation=d.get("navigation", list(DEFAULT_NAV)),
            source_texts=d.get("source_texts", []),
            websiteapp_sections=d.get("websiteapp_sections", {}),
        )
