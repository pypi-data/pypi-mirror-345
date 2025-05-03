from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from jama import settings
from django.contrib.auth.models import User
from resources.models import Resource, Collection

BASE_PATH = "/" + settings.JAMA_URL_BASE_PATH


def handler404(request, *args, **argv):
    print(request.path)
    return HttpResponse("", status=404)


def homepage(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage.html", {"BASE_PATH": BASE_PATH})


def status(request: HttpRequest) -> HttpResponse:
    # testing database connection
    try:
        User.objects.first()
    except:  # noqa: E722
        return HttpResponse("ko")
    return HttpResponse("ok")


def ark_resource(request: HttpRequest, resource_id: int) -> HttpResponse:
    resource = get_object_or_404(Resource, pk=resource_id, deleted_at__isnull=True)
    if resource.ptr_project.ark_redirect:
        location = (
            resource.ptr_project.ark_redirect.replace("[CLASS]", "resource")
            .replace("[ARK]", str(resource.ark))
            .replace("[PK]", str(resource.pk))
        )
        return redirect(location)
    return HttpResponse("Jama Resource ARK location placeholder")


def ark_collection(request: HttpRequest, collection_id: int) -> HttpResponse:
    collection = get_object_or_404(
        Collection, pk=collection_id, deleted_at__isnull=True, public_access=True
    )
    if collection.project.ark_redirect:
        location = (
            collection.project.ark_redirect.replace("[CLASS]", "collection")
            .replace("[ARK]", str(collection.ark))
            .replace("[PK]", str(collection.pk))
        )
        return redirect(location)
    return HttpResponse("Jama Collection ARK location placeholder")
