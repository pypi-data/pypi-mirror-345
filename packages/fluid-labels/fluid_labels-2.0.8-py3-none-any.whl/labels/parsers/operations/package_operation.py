import logging
import multiprocessing
import traceback
from collections.abc import Callable
from typing import (
    cast,
)

import reactivex
from reactivex import (
    Observable,
)
from reactivex import operators as ops
from reactivex.abc import (
    ObserverBase,
    SchedulerBase,
)
from reactivex.scheduler import (
    ThreadPoolScheduler,
)

from labels.model.package import Package
from labels.model.relationship import (
    Relationship,
    RelationshipType,
)
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.generic.cataloger import (
    Request,
    Task,
    execute_parsers,
)
from labels.parsers.cataloger.generic.parser import (
    Environment,
)
from labels.parsers.cataloger.handle import (
    handle_parser,
)
from labels.parsers.cataloger.python.model import (
    PythonPackage,
)
from labels.parsers.operations.utils import identify_release

LOGGER = logging.getLogger(__name__)


def strip_version_specifier(item: str) -> str:
    # Define the characters that indicate the start of a version specifier
    specifiers = "[(<>="

    # Find the index of the first occurrence of any specifier character
    index = next((i for i, char in enumerate(item) if char in specifiers), None)

    # If no specifier character is found, return the original string
    if index is None:
        return item.strip()

    # Return the substring up to the first specifier character, stripped of
    # leading/trailing whitespace
    return item[:index].strip()


def handle_relationships(packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    for package in packages:
        match package.found_by:
            case "python-installed-package-cataloger":
                python_package: PythonPackage = cast(PythonPackage, package.metadata)
                for dep in python_package.dependencies if python_package.dependencies else []:
                    dep_name = strip_version_specifier(dep)
                    if dep_package := next((x for x in packages if x.name == dep_name), None):
                        relationships.append(
                            Relationship(
                                from_=dep_package,
                                to_=package,
                                type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                            ),
                        )
    return relationships


def gen_location(
    resolver: Resolver,
) -> Callable[[Observable[Request]], Observable]:
    def _handle(source: Observable[Request]) -> Observable:
        def subscribe(
            observer: ObserverBase[Task],
            scheduler: SchedulerBase | None = None,
        ) -> reactivex.abc.DisposableBase:
            def on_next(value: Request) -> None:
                try:
                    locations = resolver.files_by_path(value.real_path)
                    for location in locations:
                        observer.on_next(
                            Task(
                                location=location,
                                parser=value.parser,
                                parser_name=value.parser_name,
                            ),
                        )
                except (
                    Exception  # noqa: BLE001
                ) as ex:
                    observer.on_error(ex)

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler,
            )

        return reactivex.create(subscribe)

    return _handle


def log_and_continue(e: Exception, file_item: str) -> Observable[None]:
    LOGGER.error(
        "Error found while resolving packages of %s: %s: %s",
        file_item,
        str(e),
        traceback.format_exc(),
    )
    return reactivex.empty()


def process_file_item(
    file_item: str,
    resolver: Resolver,
    pool_scheduler: ThreadPoolScheduler,
) -> Observable[tuple[list[Package], list[Relationship]]]:
    def factory(_: SchedulerBase | None = None) -> Observable[str]:
        return reactivex.just(file_item)

    return reactivex.defer(factory).pipe(
        handle_parser(scheduler=pool_scheduler),
        gen_location(resolver),
        execute_parsers(resolver, Environment(linux_release=identify_release(resolver))),
        ops.catch(lambda e, _: log_and_continue(e, file_item)),
    )


def package_operations_factory(
    resolver: Resolver,
) -> tuple[list[Package], list[Relationship]]:
    observer: Observable[str] = reactivex.from_iterable(resolver.walk_file())
    result_packages: list[Package] = []
    result_relations: list[Relationship] = []
    completed_event = multiprocessing.Event()
    errors = []

    def on_completed() -> None:
        completed_event.set()

    def on_error(error: Exception) -> None:
        errors.append(error)
        on_completed()

    def on_next(value: tuple[list[Package], list[Relationship]]) -> None:
        packages, relations = value
        result_packages.extend(packages)
        result_relations.extend(relations)

    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    final_obs: Observable[tuple[list[Package], list[Relationship]]] = observer.pipe(
        ops.map(
            lambda file_item: process_file_item(file_item, resolver, pool_scheduler),  # type: ignore[arg-type]
        ),
        ops.merge(max_concurrent=optimal_thread_count),
    )
    final_obs.subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed)

    completed_event.wait()
    result_relations.extend(handle_relationships(result_packages))

    return result_packages, result_relations
