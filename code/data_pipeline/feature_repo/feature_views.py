from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float64, String

import pandas as pd

from entities import properties_entity
from data_sources import properties_source

properties_fv = FeatureView(
    name="properties_fv",
    entities=[properties_entity],
    ttl=timedelta(days=36500),
    schema=[
        Field(name="area", dtype=Float64, description="Area of the property"),
        Field(name="width", dtype=Float64, description="Width of the property"),
        Field(name="length", dtype=Float64, description="Length of the property"),
        Field(name="num_bedrooms", dtype=Float64, description="Number of bedrooms in the property"),
        Field(name="num_bathrooms", dtype=Float64, description="Number of bathrooms in the property"),
        Field(name="district", dtype=String, description="The property located district name"),
        Field(name="city", dtype=String, description="The property located city name"),
        Field(name="legal_document", dtype=String, description="The legal document of the property"),
    ],
    source=properties_source,
    tags={},
    owner="phancaothng@gmail.com"
)