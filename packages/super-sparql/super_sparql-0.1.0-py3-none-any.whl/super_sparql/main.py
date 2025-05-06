import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from collections import OrderedDict

@dataclass
class SPARQLPrefix:
    prefix: str
    uri: str

@dataclass
class SPARQLTriplePattern:
    subject: str
    predicate: str
    object: str

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"

@dataclass
class SPARQLFilter:
    expression: str

    def __str__(self):
        return f"FILTER({self.expression})"

@dataclass
class SPARQLOrderBy:
    variables: List[str]
    direction: str = "ASC"  # ASC or DESC

    def __str__(self):
        direction_str = f" {self.direction}" if self.direction != "ASC" else ""
        return f"ORDER BY{direction_str} {' '.join(self.variables)}"

@dataclass
class SPARQLLimit:
    value: int

    def __str__(self):
        return f"LIMIT {self.value}"

@dataclass
class SPARQLOffset:
    value: int

    def __str__(self):
        return f"OFFSET {self.value}"

@dataclass
class SPARQLQuery:
    query_type: str  # SELECT, CONSTRUCT, ASK, DESCRIBE
    variables: List[str]
    prefixes: Dict[str, SPARQLPrefix] = field(default_factory=dict)
    triple_patterns: List[SPARQLTriplePattern] = field(default_factory=list)
    filters: List[SPARQLFilter] = field(default_factory=list)
    order_by: Optional[SPARQLOrderBy] = None
    limit: Optional[SPARQLLimit] = None
    offset: Optional[SPARQLOffset] = None

    def __str__(self):
        # Reconstruct the SPARQL query string
        query_str = ""

        # Add prefixes
        for prefix in self.prefixes.values():
            query_str += f"PREFIX {prefix.prefix}: <{prefix.uri}>\n"

        # Add query type and variables
        query_str += f"{self.query_type} {' '.join(self.variables)}\n"

        # Add WHERE clause
        query_str += "WHERE {\n"

        # Add triple patterns
        for triple in self.triple_patterns:
            query_str += f"  {triple}.\n"

        # Add filters
        for filter_expr in self.filters:
            query_str += f"  {filter_expr}\n"

        query_str += "}\n"

        # Add ORDER BY, LIMIT, OFFSET
        if self.order_by:
            query_str += f"{self.order_by}\n"
        if self.limit:
            query_str += f"{self.limit}\n"
        if self.offset:
            query_str += f"{self.offset}\n"

        return query_str

class parse_my_SPARQL:
    """
    A parser for SPARQL queries that extracts key components and allows manipulation.
    """
    def __init__(self, query_str: str):
        self.original_query = query_str
        self.parsed_query = None

        # Default namespaces if not provided
        self.default_namespaces = {
            'rdf': '<http://www.w3.org/1999/02/22-rdf-syntax-ns#>',
            'xsd': '<http://www.w3.org/2001/XMLSchema#>',
            'dcm': '<http://example.org/ns/dcm#>'
        }

    def parse(self) -> SPARQLQuery:
        """Parse the SPARQL query and return a structured representation."""
        # Clean and prepare the query
        query_str = self._prepare_query_string()

        # Extract query components
        query_type = self._extract_query_type(query_str)
        variables = self._extract_variables(query_str)
        prefixes = self._extract_prefixes(query_str)
        triple_patterns = self._extract_triple_patterns(query_str)
        filters = self._extract_filters(query_str)
        order_by = self._extract_order_by(query_str)
        limit = self._extract_limit(query_str)
        offset = self._extract_offset(query_str)

        # Create and return the query object
        self.parsed_query = SPARQLQuery(
            query_type=query_type,
            variables=variables,
            prefixes=prefixes,
            triple_patterns=triple_patterns,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )

        return self.parsed_query

    def get_select_variables(self) -> List[str]:
        """
        Returns the variables in the SELECT clause.
        If the query hasn't been parsed yet, it will parse it first.
        """
        if not self.parsed_query:
            self.parse()

        if self.parsed_query.query_type.upper() == "SELECT":
            return self.parsed_query.variables
        else:
            return []

    def get_triple_patterns(self) -> List[SPARQLTriplePattern]:
        """
        Returns the triple patterns found in the WHERE clause.
        If the query hasn't been parsed yet, it will parse it first.
        """
        if not self.parsed_query:
            self.parse()

        return self.parsed_query.triple_patterns

    def get_select_variable_types(self) -> Dict[str, List[str]]:
        """
        Analyzes the query and returns a dictionary mapping SELECT variables to
        their potential types based on predicate usage in triple patterns.

        For example, if ?x appears in "?x rdf:type dcm:Image", ?x will be associated with dcm:Image.
        """
        if not self.parsed_query:
            self.parse()

        variable_types = OrderedDict()

        # Initialize with all SELECT variables
        for var in self.parsed_query.variables:
            if var != "*":  # Skip wildcard
                variable_types[var] = []

        # Look for type declarations in triple patterns
        for triple in self.parsed_query.triple_patterns:
            # Check for explicit rdf:type statements
            if triple.predicate.lower() == "rdf:type" and triple.subject.startswith("?"):
                var = triple.subject
                if var in variable_types:
                    variable_types[var].append(triple.object)

            # Check all triple positions for the SELECT variables
            for var in variable_types.keys():
                if triple.subject == var:
                    # Subject position
                    pass  # No type information directly available

                if triple.predicate == var:
                    # Predicate position - rare in practice but theoretically possible
                    variable_types[var].append("rdf:Property")

                if triple.object == var and triple.predicate != "rdf:type":
                    # Object position
                    # Here we might infer the range of the predicate
                    variable_types[var].append(f"Range of {triple.predicate}")

        return variable_types

    def _prepare_query_string(self) -> str:
        """Clean and prepare the query string for parsing."""
        query_str = self.original_query

        # Complete incomplete PREFIX statements
        for prefix, uri in self.default_namespaces.items():
            if f"PREFIX {prefix}:" in query_str and f"PREFIX {prefix}: {uri}" not in query_str:
                query_str = re.sub(
                    f"PREFIX {prefix}:\\s*",
                    f"PREFIX {prefix}: {uri} ",
                    query_str
                )

        # Add missing prefixes that are used in the query
        for prefix in self.default_namespaces:
            if f"{prefix}:" in query_str and f"PREFIX {prefix}:" not in query_str:
                query_str = f"PREFIX {prefix}: {self.default_namespaces[prefix]} " + query_str

        return query_str

    def _extract_query_type(self, query_str: str) -> str:
        """Extract the query type (SELECT, CONSTRUCT, ASK, DESCRIBE)."""
        for query_type in ["SELECT", "CONSTRUCT", "ASK", "DESCRIBE"]:
            if re.search(f"\\b{query_type}\\b", query_str, re.IGNORECASE):
                return query_type
        return "SELECT"  # Default

    def _extract_variables(self, query_str: str) -> List[str]:
        """Extract the variables in the query projection."""
        match = re.search(r"\b(?:SELECT|CONSTRUCT|DESCRIBE)\b\s+(.*?)\s*\bWHERE\b",
                          query_str, re.IGNORECASE | re.DOTALL)
        if match:
            vars_str = match.group(1).strip()
            if vars_str == "*":
                return ["*"]
            return [var.strip() for var in re.findall(r'\?[a-zA-Z0-9_]+', vars_str)]
        return []

    def _extract_prefixes(self, query_str: str) -> Dict[str, SPARQLPrefix]:
        """Extract all PREFIX declarations."""
        prefixes = {}
        for match in re.finditer(r"PREFIX\s+([a-zA-Z0-9_]+):\s+(<[^>]+>)", query_str, re.IGNORECASE):
            prefix = match.group(1)
            uri = match.group(2)
            prefixes[prefix] = SPARQLPrefix(prefix=prefix, uri=uri)
        return prefixes

    def _extract_triple_patterns(self, query_str: str) -> List[SPARQLTriplePattern]:
        """Extract triple patterns from the WHERE clause."""
        # Find the WHERE clause
        where_match = re.search(r"\bWHERE\b\s*\{(.*)\}", query_str, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []

        where_content = where_match.group(1)

        # Remove FILTER expressions to simplify parsing
        where_content = re.sub(r"FILTER\s*\([^)]+\)", "", where_content)

        # Find triple patterns
        triple_patterns = []
        for statement in re.finditer(r"([^.]+)\.", where_content):
            triple_str = statement.group(1).strip()
            if triple_str and not triple_str.startswith("FILTER"):
                parts = triple_str.split(maxsplit=2)
                if len(parts) == 3:
                    triple_patterns.append(SPARQLTriplePattern(
                        subject=parts[0].strip(),
                        predicate=parts[1].strip(),
                        object=parts[2].strip()
                    ))

        return triple_patterns

    def _extract_filters(self, query_str: str) -> List[SPARQLFilter]:
        """Extract FILTER expressions from the WHERE clause."""
        # Find the WHERE clause
        where_match = re.search(r"\bWHERE\b\s*\{(.*)\}", query_str, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []

        where_content = where_match.group(1)

        # Find FILTER expressions
        filters = []
        for filter_match in re.finditer(r"FILTER\s*\(([^)]+)\)", where_content, re.IGNORECASE):
            filters.append(SPARQLFilter(expression=filter_match.group(1).strip()))

        return filters

    def _extract_order_by(self, query_str: str) -> Optional[SPARQLOrderBy]:
        """Extract ORDER BY clause."""
        order_match = re.search(r"\bORDER\s+BY\s+(.*?)(?:\bLIMIT\b|\bOFFSET\b|$)",
                                query_str, re.IGNORECASE | re.DOTALL)
        if order_match:
            order_str = order_match.group(1).strip()
            direction = "ASC"
            if order_str.startswith("DESC"):
                direction = "DESC"
                order_str = order_str[4:].strip()
            elif order_str.startswith("ASC"):
                order_str = order_str[3:].strip()

            variables = [var.strip() for var in re.findall(r'\?[a-zA-Z0-9_]+', order_str)]
            return SPARQLOrderBy(variables=variables, direction=direction)
        return None

    def _extract_limit(self, query_str: str) -> Optional[SPARQLLimit]:
        """Extract LIMIT clause."""
        limit_match = re.search(r"\bLIMIT\s+(\d+)", query_str, re.IGNORECASE)
        if limit_match:
            return SPARQLLimit(value=int(limit_match.group(1)))
        return None

    def _extract_offset(self, query_str: str) -> Optional[SPARQLOffset]:
        """Extract OFFSET clause."""
        offset_match = re.search(r"\bOFFSET\s+(\d+)", query_str, re.IGNORECASE)
        if offset_match:
            return SPARQLOffset(value=int(offset_match.group(1)))
        return None

    def analyze_query(self) -> Dict:
        """
        Performs a comprehensive analysis of the query, returning detailed information
        about variables, triple patterns, and structure.
        """
        if not self.parsed_query:
            self.parse()

        # Collect information about each variable
        variables_info = {}

        # First get all variables from the query (both SELECT and WHERE)
        all_vars = set()

        # Add SELECT variables
        for var in self.parsed_query.variables:
            if var != "*":
                all_vars.add(var)

        # Add variables from triple patterns
        for triple in self.parsed_query.triple_patterns:
            for part in [triple.subject, triple.predicate, triple.object]:
                if part.startswith("?"):
                    all_vars.add(part)

        # Analyze each variable
        for var in all_vars:
            var_info = {
                "in_select": var in self.parsed_query.variables,
                "occurrences": {
                    "as_subject": [],
                    "as_predicate": [],
                    "as_object": []
                }
            }

            # Find occurrences in triple patterns
            for i, triple in enumerate(self.parsed_query.triple_patterns):
                if triple.subject == var:
                    var_info["occurrences"]["as_subject"].append({
                        "triple_index": i,
                        "triple": str(triple)
                    })
                if triple.predicate == var:
                    var_info["occurrences"]["as_predicate"].append({
                        "triple_index": i,
                        "triple": str(triple)
                    })
                if triple.object == var:
                    var_info["occurrences"]["as_object"].append({
                        "triple_index": i,
                        "triple": str(triple)
                    })

            variables_info[var] = var_info

        return {
            "query_type": self.parsed_query.query_type,
            "select_variables": self.get_select_variables(),
            "variable_types": self.get_select_variable_types(),
            "variables_details": variables_info,
            "triple_count": len(self.parsed_query.triple_patterns),
            "filter_count": len(self.parsed_query.filters),
            "has_order_by": self.parsed_query.order_by is not None,
            "has_limit": self.parsed_query.limit is not None,
            "has_offset": self.parsed_query.offset is not None
        }