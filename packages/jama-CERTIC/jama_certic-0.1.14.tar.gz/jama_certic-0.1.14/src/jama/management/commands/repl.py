from django.core.management.commands.shell import Command
from django.contrib.auth.models import User
from rich.console import Console
from rich.table import Table
from typing import List
from resources.helpers import make_iiif, make_ocr

# from pick import pick
from resources.models import (
    Resource,
    Collection,
    Project,
    APIKey,
    ProjectAccess,
    Permission,
    File,
    ProjectProperty,
    UserTask,
    Tag,
    FileExtension,
    FileType,
    MetadataSet,
    Metadata,
    MetadataCollectionValue,
    MetadataResourceValue,
    CollectionMembership,
    Role,
)


def _console_table(title: str, headers: List["str"]) -> Table:
    table = Table(title=title)
    for header in headers:
        table.add_column(header)
    return table


def user(*args, **kwargs):
    return User.objects.get(*args, **kwargs)


def project(*args, **kwargs):
    return Project.objects.get(*args, **kwargs)


def projects(*args, **kwargs):
    table = _console_table(
        "Projects",
        [
            "pk",
            "label",
            "description",
            "admin mail",
            "ARK redirect",
            "exiftool",
            "users",
        ],
    )

    for p in Project.objects.filter(*args, **kwargs):
        table.add_row(
            str(p.pk),
            str(p.label),
            str(p.description),
            str(p.admin_mail),
            str(p.ark_redirect),
            str(p.use_exiftool),
            ", ".join(
                f"{a.user.username} ({a.user.pk})"
                for a in ProjectAccess.objects.filter(project=p)
            ),
        )
    Console().print(table)


def users(*args, **kwargs):
    # option, index = pick(["some", "of", "this"], "choose...", multiselect=True)
    table = _console_table(
        "Users", ["pk", "username", "email", "active", "superuser", "projects"]
    )
    for u in User.objects.filter(*args, **kwargs):
        table.add_row(
            str(u.pk),
            str(u.username),
            str(u.email),
            str(u.is_active),
            str(u.is_superuser),
            ", ".join(
                f"{a.project.label} ({a.project.pk})"
                for a in ProjectAccess.objects.filter(user=u)
            ),
        )
    Console().print(table)


def accesses():
    for a in ProjectAccess.objects.order_by("project"):
        print(a.pk, a)


def move_collection_to_project(from_collection_id: int, to_project_id: int):
    from resources.tasks import ocr_task

    from_collection_instance = Collection.objects.get(pk=from_collection_id)
    to_project_instance = Project.objects.get(pk=to_project_id)
    from_collection_instance.parent = to_project_instance.root_collection
    from_collection_instance.project = to_project_instance
    from_collection_instance.save()
    print(f"Collection({from_collection_instance.id})")
    for col in from_collection_instance.descendants():
        col.project = to_project_instance
        col.save()
        print(f"Collection({col.id})")
        for res in col.resources.iterator():
            res.ptr_project = to_project_instance
            res.save()
            print(
                "Metadatas deleted: ",
                MetadataResourceValue.objects.filter(resource=res).delete(),
            )
            print(f"Resource({res.id})")
            if res.file:
                res.file.project = to_project_instance
                res.file.save()
                print(f"File({res.file.id})")
                ocr_task(res.file.id)
    print("Done.")


def bpython(self, options):
    import bpython

    bpython.embed(
        {
            "APIKey": APIKey,
            "Collection": Collection,
            "File": File,
            "Permission": Permission,
            "Project": Project,
            "ProjectAccess": ProjectAccess,
            "Resource": Resource,
            "User": User,
            "ProjectProperty": ProjectProperty,
            "UserTask": UserTask,
            "Tag": Tag,
            "FileExtension": FileExtension,
            "FileType": FileType,
            "MetadataSet": MetadataSet,
            "Metadata": Metadata,
            "MetadataCollectionValue": MetadataCollectionValue,
            "MetadataResourceValue": MetadataResourceValue,
            "CollectionMembership": CollectionMembership,
            "Role": Role,
            "projects": projects,
            "users": users,
            "accesses": accesses,
            "make_iiif": make_iiif,
            "make_ocr": make_ocr,
            # "move_collection_to_project": move_collection_to_project,
        }
    )


Command.bpython = bpython
