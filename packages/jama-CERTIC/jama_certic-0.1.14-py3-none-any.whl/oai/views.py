from django.http import (
    HttpRequest,
    HttpResponse,
    Http404,
)
from django.template.loader import render_to_string
from jama import settings
from resources.models import Collection, Project
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

PAGINATION_SIZE = 100


def _set_spec_to_collection(set_spec: str) -> Collection:
    try:
        last_id = int(set_spec.split(":")[-1])
        collection = Collection.objects.get(pk=last_id)
        return collection
    except (ValueError, Collection.DoesNotExist):
        raise ValueError("no such collection")


def _collection_to_set_spec(collection: Collection) -> str:
    return collection.oai_setspec()


def _validate_date(in_date: str) -> bool:
    try:
        res = bool(datetime.strptime(in_date, "%Y-%m-%d"))
    except (ValueError, TypeError):
        res = False
    return res


OAI_VERBS = [
    "Identify",
    "GetRecord",
    "ListIdentifiers",
    "ListMetadataFormats",
    "ListRecords",
    "ListSets",
]


def _oai_error(project: Project, request: HttpRequest, errors: dict) -> HttpResponse:
    return HttpResponse(
        render_to_string(
            "oai/errors.xml",
            {"project": project, "base_url": settings.JAMA_SITE, "errors": errors},
        ),
        content_type="text/xml",
    )


def _get_record(project: Project, request: HttpRequest) -> HttpResponse:
    try:
        identifier = int(request.GET.get("identifier")) or request.POST.get(
            "identifier"
        )
        if not identifier:
            return _oai_error(
                project, request, {"badArgument": "identifier is missing"}
            )
    except ValueError:
        return _oai_error(
            project, request, {"idDoesNotExist": "identifier does not exist"}
        )
    try:
        collection_instance = Collection.objects.get(pk=identifier, project=project)
        return HttpResponse(
            render_to_string(
                "oai/get_record.xml",
                {
                    "project": project,
                    "base_url": settings.JAMA_SITE,
                    "collection": collection_instance,
                },
            ),
            content_type="text/xml",
        )
    except Collection.DoesNotExist:
        return _oai_error(
            project, request, {"idDoesNotExist": "identifier does not exist"}
        )


def _identify(project: Project, request: HttpRequest) -> HttpResponse:
    earliest_record = (
        Collection.objects.filter(project=project, public_access=True)
        .order_by("created_at")
        .first()
    )
    return HttpResponse(
        render_to_string(
            "oai/identify.xml",
            {
                "project": project,
                "base_url": settings.JAMA_SITE,
                "earliest_record": earliest_record,
            },
        ),
        content_type="text/xml",
    )


def _list_identifiers(project: Project, request: HttpRequest) -> HttpResponse:
    return _list_records(project, request, only_headers=True)


def _list_metadata_formats(project: Project, request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        render_to_string(
            "oai/list_metadata_formats.xml",
            {
                "project": project,
                "base_url": settings.JAMA_SITE,
            },
        ),
        content_type="text/xml",
    )


def _list_records(
    project: Project, request: HttpRequest, only_headers=False
) -> HttpResponse:
    page_number = 1
    resumption_token = request.GET.get("resumptionToken") or request.POST.get(
        "resumptionToken"
    )

    #
    # Get page number (ie. resumption token)
    #
    if resumption_token:
        try:
            page_number = abs(int(resumption_token))
        except ValueError:
            pass

    #
    # Get from date
    #
    from_date = request.GET.get("from") or request.POST.get("until")
    if from_date and not _validate_date(from_date):
        return _oai_error(project, request, {"badArgument": "bad from date format"})

    #
    # Get until date
    #
    until_date = request.GET.get("until") or request.POST.get("until")
    if until_date and not _validate_date(until_date):
        return _oai_error(project, request, {"badArgument": "bad until date format"})

    #
    # Get setSpec collection
    #
    spec_collection = None
    set_spec = request.GET.get("set") or request.POST.get("set")
    if set_spec:
        spec_collection = _set_spec_to_collection(set_spec=set_spec)

    #
    # Build query
    #
    all_records = Collection.objects.filter(
        project=project, public_access=True
    ).order_by("created_at")
    if from_date:
        all_records = all_records.filter(created_at__gte=from_date)
    if until_date:
        all_records = all_records.filter(created_at__lte=until_date)
    if spec_collection:
        all_records = all_records.filter(
            parent__in=spec_collection.descendants_and_self_ids()
        )

    #
    # Paginate, render.
    #
    total_count = all_records.count()
    if total_count == 0:
        return _oai_error(project, request, {"noRecordsMatch": "no records match"})
    paginator = Paginator(all_records, PAGINATION_SIZE)
    page = paginator.page(page_number)
    if only_headers:
        xml_template = "oai/list_identifiers.xml"
    else:
        xml_template = "oai/list_records.xml"
    return HttpResponse(
        render_to_string(
            xml_template,
            {
                "project": project,
                "base_url": settings.JAMA_SITE,
                "page": page,
                "from": from_date,
                "until": until_date,
                "total_count": total_count,
                "total_pages": paginator.num_pages,
                "nb_of_already_delivered_identifiers": (page_number - 1)
                * PAGINATION_SIZE,
                "spec_collection": spec_collection,
            },
        ),
        content_type="text/xml",
    )


def _list_sets(project: Project, request: HttpRequest) -> HttpResponse:
    collections = Collection.objects.filter(project=project, public_access=True)
    return HttpResponse(
        render_to_string(
            "oai/list_sets.xml",
            {
                "project": project,
                "base_url": settings.JAMA_SITE,
                "collections": collections,
            },
        ),
        content_type="text/xml",
    )


@csrf_exempt
def oai(request: HttpRequest, project_id: int) -> HttpResponse:
    try:
        project = Project.objects.get(pk=project_id)
        oai_verb = request.GET.get("verb") or request.POST.get("verb")
        if oai_verb not in OAI_VERBS:
            return _oai_error(project, request, {"badVerb": "Illegal OAI verb"})
        metadata_prefix = request.GET.get("metadataPrefix") or request.POST.get(
            "metadataPrefix"
        )
        if metadata_prefix and metadata_prefix != "oai_dc":
            return _oai_error(
                project, request, {"cannotDisseminateFormat": "oai_dc only"}
            )
        if oai_verb == "GetRecord":
            return _get_record(project, request)
        if oai_verb == "Identify":
            return _identify(project, request)
        if oai_verb == "ListIdentifiers":
            return _list_identifiers(project, request)
        if oai_verb == "ListMetadataFormats":
            return _list_metadata_formats(project, request)
        if oai_verb == "ListRecords":
            return _list_records(project, request)
        if oai_verb == "ListSets":
            return _list_sets(project, request)
    # each project has its own endpoint
    except Project.DoesNotExist:
        raise Http404()
