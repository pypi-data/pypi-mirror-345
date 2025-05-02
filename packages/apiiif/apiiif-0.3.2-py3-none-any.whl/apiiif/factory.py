from apiiif.resource_properties import (
    LanguageString,
    LabelValue,
    Thumbnail,
    Logo,
    Homepage,
    PartOf,
    Provider,
    Choice,
    ImageService,
    ExternalAuthService,
)
from apiiif.resource_types import (
    Collection,
    Manifest,
    Canvas,
    Annotation,
    IIIFImage,
    AnnotationPage,
)


class SingleLanguageFactory:

    def __init__(self, auto_language: str = "en"):
        self.auto_language = auto_language

    def langugae_string(self, message: str):
        return LanguageString(**{self.auto_language: [message]})

    def label_value(self, label: str, value: str):
        return LabelValue(
            label=self.langugae_string(label), value=self.langugae_string(value)
        )

    def requiredStatement(self, label: str, value: str):
        return self.label_value(label, value)

    def thumbnail(self, url: str, width: int = None, height: int = None):
        return Thumbnail(id=url, width=width, height=height)

    def logo(self, url: str, width: int, height: int):
        return Logo(id=url, width=width, height=height)

    def homepage(self, url: str, label: str):
        return Homepage(
            id=url, label=self.langugae_string(label), language=[self.auto_language]
        )

    def partOf(self, url: str):
        return PartOf(id=url)

    def provider(self, url: str, label: str, homepage: Homepage):
        return Provider(
            id=url,
            label=self.langugae_string(label),
            homepage=[homepage],
            logo=[self.logo(url, 100, 100)],
        )

    def choice(self, items: list):
        return Choice(items=items)

    def imageService(self, url: str):
        return ImageService(id=url)

    def collection(
        self, url: str, label: str, attribution_label: str, attribution_value: str
    ):
        return Collection(
            id=url,
            label=self.langugae_string(label),
            requiredStatement=self.requiredStatement(
                attribution_label, attribution_value
            ),
        )

    def manifest(
        self,
        url: str,
        label: str,
        metadata: list[LabelValue] = [],
        summary: str | None = None,
        thumbnail: Thumbnail | None = None,
        viewingDirection: str = "left-to-right",
        behavior: str = "paged",
        rights: str | None = None,
        attribution: tuple[str, str] | None = None,
        provider: Provider | None = None,
        homepage: Homepage | None = None,
        partOf_url: str | None = None,
    ):
        return Manifest(
            id=url,
            label=self.langugae_string(label),
            metadata=metadata,
            summary=self.langugae_string(summary) if summary else None,
            thumbnail=thumbnail,
            viewingDirection=viewingDirection,
            behavior=[behavior],
            rights=rights,
            requiredStatement=(
                self.requiredStatement(attribution[0], attribution[1])
                if attribution
                else None
            ),
            provider=[provider] if provider else None,
            homepage=homepage,
            partOf=self.partOf(partOf_url) if partOf_url else None,
        )

    def canvas(
        self, url: str, label: str, height: int, width: int, behavior: str = "paged"
    ):
        return Canvas(
            id=url,
            label=self.langugae_string(label),
            height=height,
            width=width,
            behavior=[behavior],
        )

    def IIIF_image(
        self,
        thumbnail_url: str,
        iiif_root_url: str,
        width: int,
        height: int,
        additional_services: list[ImageService | ExternalAuthService] = [],
    ):
        services = [self.imageService(iiif_root_url)]
        services.extend(additional_services)
        return IIIFImage(
            id=thumbnail_url,
            width=width,
            height=height,
            service=services,
        )

    def external_auth_service(
        self,
        label: str,
        failure_header: str,
        failure_description: str,
    ):
        return ExternalAuthService(
            label=self.langugae_string(label),
            failureHeader=self.langugae_string(failure_header),
            failureDescription=self.langugae_string(failure_description),
        )

    def annotation_page(
        self,
        iiif_root_url: str,
        canvas_url: str,
        iiif_image: IIIFImage | list[IIIFImage],
    ):
        """create both an Annotation Page and Annotation, link them,
        then return the Annotation Page"""
        annotation_page = AnnotationPage(id=f"{iiif_root_url}/annotationpage")
        if isinstance(iiif_image, list):
            body = Choice(items=iiif_image)
        else:
            body = iiif_image
        annotation = Annotation(
            id=f"{iiif_root_url}/annotation", body=body, target=canvas_url
        )
        annotation_page.items.append(annotation)
        return annotation_page
