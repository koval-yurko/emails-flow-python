from pyairtable import Api, Table

import os
from typing import Dict, List, Optional, Any
from ai import PostItem


class AirtableClient:
    """Client for interacting with Airtable API"""

    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None):
        """
        Initialize Airtable client

        Args:
            api_key: Airtable API key (if not provided, will use AIRTABLE_API_KEY env var)
            base_id: Airtable base ID (if not provided, will use AIRTABLE_BASE_ID env var)
        """
        self.__api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.__base_id = base_id or os.getenv("AIRTABLE_BASE_ID")

        self.__api = Api(self.__api_key)
        self.__base = self.__api.base(self.__base_id)

        # Local caches for IDs
        self.__tags_cache: Dict[str, str] = {}
        self.__new_tags_cache: Dict[str, str] = {}
        self.__domains_cache: Dict[str, str] = {}
        self.__categories_cache: Dict[str, str] = {}

    def __get_records(
        self,
        table_name: str,
        view: Optional[str] = None,
        formula: Optional[str] = None,
        max_records: Optional[int] = None,
        fields: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records from an Airtable table

        Args:
            table_name: Name of the table to query
            view: Name of the view to use (optional)
            formula: Filter formula (optional)
            max_records: Maximum number of records to return (optional)
            fields: List of field names to return (optional)
            sort: List of sort field (name, desc)

        Returns:
            List of records with their data
        """
        table: Table = self.__base.table(table_name)

        kwargs = {}
        if view:
            kwargs["view"] = view
        if formula:
            kwargs["formula"] = formula
        if max_records:
            kwargs["max_records"] = max_records
        if fields:
            kwargs["fields"] = fields
        if sort:
            kwargs["sort"] = sort

        try:
            records = table.all(**kwargs)
            return [
                {"id": record["id"], "fields": record["fields"]} for record in records
            ]
        except Exception as e:
            raise Exception(
                f"Error retrieving records from table '{table_name}': {str(e)}"
            )

    def __create_record(
        self, table_name: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record in an Airtable table

        Args:
            table_name: Name of the table to create record in
            fields: Dictionary of field names and values

        Returns:
            Created record with ID and fields
        """
        table = self.__base.table(table_name)

        try:
            record = table.create(fields)
            return {"id": record["id"], "fields": record["fields"]}
        except Exception as e:
            raise Exception(f"Error creating record in table '{table_name}': {str(e)}")

    def __create_records(
        self, table_name: str, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple records in an Airtable table

        Args:
            table_name: Name of the table to create records in
            records: List of dictionaries with field names and values

        Returns:
            List of created records with IDs and fields
        """
        table = self.__base.table(table_name)

        try:
            created_records = table.batch_create(records)
            return [
                {"id": record["id"], "fields": record["fields"]}
                for record in created_records
            ]
        except Exception as e:
            raise Exception(f"Error creating records in table '{table_name}': {str(e)}")

    def __update_record(
        self, table_name: str, record_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing record in an Airtable table

        Args:
            table_name: Name of the table containing the record
            record_id: ID of the record to update
            fields: Dictionary of field names and values to update

        Returns:
            Updated record with ID and fields
        """
        table = self.__base.table(table_name)

        try:
            record = table.update(record_id, fields)
            return {"id": record["id"], "fields": record["fields"]}
        except Exception as e:
            raise Exception(
                f"Error updating record '{record_id}' in table '{table_name}': {str(e)}"
            )

    def __delete_record(self, table_name: str, record_id: str) -> str:
        """
        Delete a record from an Airtable table

        Args:
            table_name: Name of the table containing the record
            record_id: ID of the record to delete

        Returns:
            ID of the deleted record
        """
        table = self.__base.table(table_name)

        try:
            deleted_record = table.delete(record_id)
            return deleted_record["id"]
        except Exception as e:
            raise Exception(
                f"Error deleting record '{record_id}' from table '{table_name}': {str(e)}"
            )

    def get_unprocessed_items(self, max_records: Optional[int] = 5):
        unprocessed_items = self.__get_records(
            "TLDR Emails",
            formula="AND({Processed} != TRUE())",
            sort=["Date"],
            max_records=max_records,
        )

        return unprocessed_items

    def mark_email_item_as_processed(self, record_id: str):
        self.__update_record("TLDR Emails", record_id, {"Processed": True})

    def get_or_create_domain(self, domain_name: str) -> str:
        """
        Get an existing domain or create a new one if it doesn't exist

        Args:
            domain_name: Name of the domain to get or create

        Returns:
            Domain record ID
        """
        # Normalize domain name to lowercase
        normalized_name = domain_name.lower().strip()

        # Check cache first
        if normalized_name in self.__domains_cache:
            return self.__domains_cache[normalized_name]

        # First, try to find existing domain
        existing_domains = self.__get_records(
            "Domains", formula=f"LOWER({{Name}}) = '{normalized_name}'"
        )

        if existing_domains:
            domain_id = existing_domains[0]["id"]
            self.__domains_cache[normalized_name] = domain_id
            return domain_id

        # If not found, create new domain
        new_domain = self.__create_record("Domains", {"Name": normalized_name})
        domain_id = new_domain["id"]
        self.__domains_cache[normalized_name] = domain_id
        return domain_id

    def get_or_create_category(self, category_name: str) -> str:
        """
        Get an existing category or create a new one if it doesn't exist

        Args:
            category_name: Name of the category to get or create

        Returns:
            Category record ID
        """
        # Normalize category name to lowercase
        normalized_name = category_name.lower().strip()

        # Check cache first
        if normalized_name in self.__categories_cache:
            return self.__categories_cache[normalized_name]

        # First, try to find existing category
        existing_categories = self.__get_records(
            "Categories", formula=f"LOWER({{Name}}) = '{normalized_name}'"
        )

        if existing_categories:
            category_id = existing_categories[0]["id"]
            self.__categories_cache[normalized_name] = category_id
            return category_id

        # If not found, create new category
        new_category = self.__create_record("Categories", {"Name": normalized_name})
        category_id = new_category["id"]
        self.__categories_cache[normalized_name] = category_id
        return category_id

    def get_or_create_tag(self, tag_name: str) -> str:
        """
        Get an existing tag or create a new one if it doesn't exist

        Args:
            tag_name: Name of the tag to get or create

        Returns:
            Tag record ID
        """
        # Normalize tag name to lowercase
        normalized_name = tag_name.lower().strip()

        # Check cache first
        if normalized_name in self.__tags_cache:
            return self.__tags_cache[normalized_name]

        # First, try to find existing tag
        existing_tags = self.__get_records(
            "Tags", formula=f"LOWER({{Name}}) = '{normalized_name}'"
        )

        if existing_tags:
            tag_id = existing_tags[0]["id"]
            self.__tags_cache[normalized_name] = tag_id
            return tag_id

        # If not found, create new tag
        new_tag = self.__create_record("Tags", {"Name": normalized_name})
        tag_id = new_tag["id"]
        self.__tags_cache[normalized_name] = tag_id
        return tag_id

    def get_or_create_new_tag(self, tag_name: str) -> str:
        """
        Get an existing tag or create a new one if it doesn't exist

        Args:
            tag_name: Name of the tag to get or create

        Returns:
            Tag record ID
        """
        # Normalize tag name to lowercase
        normalized_name = tag_name.lower().strip()

        # Check cache first
        if normalized_name in self.__new_tags_cache:
            return self.__new_tags_cache[normalized_name]

        # First, try to find existing tag
        existing_tags = self.__get_records(
            "New Tags", formula=f"LOWER({{Name}}) = '{normalized_name}'"
        )

        if existing_tags:
            tag_id = existing_tags[0]["id"]
            self.__new_tags_cache[normalized_name] = tag_id
            return tag_id

        # If not found, create new tag
        new_tag = self.__create_record("New Tags", {"Name": normalized_name})
        tag_id = new_tag["id"]
        self.__new_tags_cache[normalized_name] = tag_id
        return tag_id

    def create_result_item(self, email_id: str, post: PostItem, date: str):
        # if post.tags exists - iterate through it and get or create tags:
        tag_ids = []
        if post.tags:
            for tag in post.tags:
                tag_id = self.get_or_create_tag(tag)
                tag_ids.append(tag_id)

        domain_ids = []
        if post.domains:
            for domain in post.domains:
                domain_id = self.get_or_create_domain(domain)
                domain_ids.append(domain_id)

        category_ids = []
        if post.categories:
            for category in post.categories:
                category_id = self.get_or_create_category(category)
                category_ids.append(category_id)

        new_tags_ids = []
        if post.newTags:
            for tag in post.newTags:
                tag_id = self.get_or_create_new_tag(tag)
                new_tags_ids.append(tag_id)

        record_data = {
            "Email ID": [email_id],
            "Title": post.title,
            "URL": post.url,
            "Date": date,
        }

        if domain_ids:
            record_data["Domain"] = domain_ids
        if category_ids:
            record_data["Category"] = category_ids
        if tag_ids:
            record_data["Tags"] = tag_ids
        if new_tags_ids:
            record_data["New Tags"] = new_tags_ids

        self.__create_record("TLDR Results", record_data)
