from pydantic.v1 import AnyUrl, Field

from apiiif.resource_properties import (
    LanguageString,
    LabelValue,
    Provider,
    Thumbnail,
    Homepage,
    PartOf,
    Image,
    Choice,
    ImageService,
    ExternalAuthService,
    BaseID,
)


class IIIFImage(Image):
    format: str = "image/jpeg"
    # as other services are defined, add them as options.
    service: list[ImageService | ExternalAuthService] = []


class Annotation(BaseID):
    context: str = Field(
        default="http://iiif.io/api/presentation/3/context.json", alias="@context"
    )
    type: str = "Annotation"
    motivation: str = "painting"
    target: AnyUrl
    body: IIIFImage | Choice | None = None

    def add_image(self, image: IIIFImage):
        if self.body is None:
            self.body = image
        elif isinstance(self.body, Choice):
            self.body.items.append(image)
        else:
            self.body = Choice(items=[self.body, image])


class AnnotationPage(BaseID):
    context: str = Field(
        default="http://iiif.io/api/presentation/3/context.json", alias="@context"
    )
    type: str = "AnnotationPage"
    items: list[Annotation] = []

    def add_annotation(self, annotation: Annotation):
        self.items.append(annotation)


class Canvas(BaseID):
    type: str = "Canvas"
    label: LanguageString
    height: int
    width: int
    behavior: list[str] | None  # ['paged'], ['facing-pages'], ['non-paged']
    items: list = []

    def add_annotation_page(self, annotation_page: AnnotationPage):
        self.items.append(annotation_page)


# Range should be defined here, but the collections site does not yet support it.
# Use a range for creating a table of contents within the client (Mirador viewer).
# For example, printed books could be broken into chapters, and manuscripts could
# be devided into books or major sections since many manuscripts have non-biblical texts


class Manifest(BaseID):
    context: str = Field(
        default="http://iiif.io/api/presentation/3/context.json", alias="@context"
    )
    type: str = "Manifest"
    label: LanguageString
    metadata: list[LabelValue] = []
    summary: LanguageString | None
    thumbnail: Thumbnail | None
    viewingDirection: str = "left-to-right"
    behavior: list[str] = ["paged"]
    rights: AnyUrl | str | None
    requiredStatement: LabelValue | None
    provider: list[Provider] | None
    homepage: Homepage | None
    partOf: PartOf | None
    items: list = []

    def add_canvas(self, canvas: Canvas):
        self.items.append(canvas)


class Collection(BaseID):
    context: str = Field(
        default="http://iiif.io/api/presentation/3/context.json", alias="@context"
    )
    type: str = "Collection"
    label: LanguageString
    requiredStatement: LabelValue | None
    items: list = []

    def add_manifest(self, manifest: Manifest):
        self.items.append(manifest)
