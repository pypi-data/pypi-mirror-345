"""pycui-utils"""

import json
import os
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypedDict

__all__ = ["categories", "special_categories", "basic_categories", "organizations"]


def resource_filename(package: str, resource: str) -> str:
    """Get the path to a resource file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, package, resource)


DATABASE_DIR: str = resource_filename("pycui", "databases")


class CategoryData(TypedDict):
    """Type definition for category data from JSON."""

    name: str
    description: str
    is_specified: bool
    index_group: str
    marking_format: str


class Category:
    """Represents a CUI category."""

    def __init__(self, code: str, data: CategoryData):
        self.code = code
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.is_specified = data.get("is_specified", False)
        self.organization_code = data.get("index_group", "")
        self.marking_format = data.get("marking_format", "")

    def __repr__(self) -> str:
        return f"<Category: {self.code} - {self.name}>"


class Categories:
    """Container for all CUI categories."""

    def __init__(self, database_path: str):
        self._categories: dict[str, Category] = {}
        self._load_database(database_path)

    def _load_database(self, database_path: str) -> None:
        try:
            with open(database_path, encoding="utf-8") as f:
                data = json.load(f)
                for code, cat_data in data.items():
                    self._categories[code] = Category(code, cat_data)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load CUI database: {e}")

    def get_by_marking(self, marking: str) -> Category | None:
        """Get a category by its marking format."""
        value = [
            cat for cat in self.all() if cat.marking_format.lower() == marking.lower()
        ]
        return value[0] if value else None

    def by_organization(self, organization_code: str) -> list[Category]:
        """Get categories belonging to a specific organization."""
        return [
            cat
            for cat in self.all()
            if cat.organization_code.lower() == organization_code.lower()
        ]

    def all(self) -> list[Category]:
        """Get all categories."""
        return list(self._categories.values())

    def __iter__(self) -> Iterator[Category]:
        return iter(self._categories.values())


class CategoryFilter(ABC):
    """Abstract base class for filtered category collections."""

    def __init__(self, categories_obj: Categories):
        self._categories = categories_obj

    @abstractmethod
    def matches_criteria(self, category: Category) -> bool:
        """Determine if a category matches this filter's criteria."""
        pass

    def all(self) -> list[Category]:
        """Get all categories matching this filter's criteria."""
        return [cat for cat in self._categories.all() if self.matches_criteria(cat)]

    def by_organization(self, organization_code: str) -> list[Category]:
        """Get filtered categories by organization."""
        return [cat for cat in self.all() if cat.organization_code == organization_code]

    def get_by_marking(self, marking: str) -> Category | None:
        """Get filtered categories with a specific marking format."""

        value = [
            cat for cat in self.all() if cat.marking_format.lower() == marking.lower()
        ]
        return value[0] if value else None


class BasicCategories(CategoryFilter):
    """Basic CUI categories (is_specified=False)."""

    def matches_criteria(self, category: Category) -> bool:
        return not category.is_specified


class SpecialCategories(CategoryFilter):
    """Special CUI categories (is_specified=True)."""

    def matches_criteria(self, category: Category) -> bool:
        return category.is_specified


class Organizations:
    """Container for organization codes extracted from categories."""

    def __init__(self, categories_obj: Categories):
        self._categories = categories_obj
        self._organization_codes = self._extract_organization_codes()

    def _extract_organization_codes(self) -> list[str]:
        """Extract unique organization codes from categories."""
        org_codes = {cat.organization_code for cat in self._categories.all()}
        return sorted(org_codes)

    def all(self) -> list[str]:
        """Get all organization codes."""
        return self._organization_codes

    def categories(self, organization_code: str) -> list[Category]:
        """Get all categories for a specific organization."""
        return self._categories.by_organization(organization_code)


categories = Categories(os.path.join(DATABASE_DIR, "cui.json"))
organizations = Organizations(categories)
special_categories = SpecialCategories(categories)
basic_categories = BasicCategories(categories)
