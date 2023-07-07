# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PreprocessingPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()
            if isinstance(value, list) and field_name == 'content':
                adapter[field_name] = '\n'.join(value)

        return item
