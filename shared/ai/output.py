from pydantic import BaseModel, Field


class PostItem(BaseModel):
    url: str = Field(description="The url of the post")
    title: str = Field(description="The title of the post")
    text: str = Field(description="A text of the post")
    domains: list[str] = Field(default=[], description="A list of domains of the post")
    categories: list[str] = Field(
        default=[], description="A list of categories of the post"
    )
    tags: list[str] = Field(default=[], description="A list of tags of the post")
    newTags: list[str] = Field(default=[], description="A list of new tags of the post")


class ResponseFormatter(BaseModel):
    posts: list[PostItem] = Field(description="A list of posts")
