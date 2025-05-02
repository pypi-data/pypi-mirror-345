import pyarrow as pa
import pyarrow.compute as pc
from typing import Optional, List, Union

from SanctionSightPy.filters.base_filter import BaseFilter


class EntityFilter(BaseFilter):
    def __init__(
            self,
            search_terms: Union[str, List[str]],
            columns: Union[str, List[str]],
            match_type: str = "partial",  # "partial", "exact", or "startswith"
            case_sensitive: bool = False
    ):
        """
        Args:
            search_terms: Terms to search for (single string or list)
            columns: Column(s) to search in
            match_type: How to match:
                - "partial": Substring match (default)
                - "exact": Full equality
                - "startswith": Begins with term
            case_sensitive: Whether matching respects case
        """
        self.search_terms = [search_terms] if isinstance(search_terms, str) else search_terms
        self.columns = [columns] if isinstance(columns, str) else columns
        self.match_type = match_type
        self.case_sensitive = case_sensitive

    def apply(self, data: pa.Table) -> pa.Table:
        masks = []

        for term in self.search_terms:
            term_mask = None
            for col in self.columns:
                if col not in data.column_names:
                    continue

                if not self.case_sensitive:
                    col_data = pc.utf8_lower(data[col])
                    search_term = term.lower()
                else:
                    col_data = data[col]
                    search_term = term

                if self.match_type == "exact":
                    mask = pc.equal(col_data, search_term)
                elif self.match_type == "startswith":
                    mask = pc.starts_with(col_data, search_term)
                else:  # partial match (default)
                    mask = pc.match_substring(col_data, search_term)

                term_mask = mask if term_mask is None else pc.or_(term_mask, mask)

            if term_mask is not None:
                masks.append(term_mask)

        if not masks:
            return data

        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = pc.or_(combined_mask, mask)

        return data.filter(combined_mask)
