import scrapy

class JobItem(scrapy.Item):
    job_title = scrapy.Field()
    job_detail_url = scrapy.Field()
    job_listed = scrapy.Field()
    company_name = scrapy.Field()
    company_link = scrapy.Field()
    company_location = scrapy.Field()
    publication_start_date = scrapy.Field()
    publication_end_date = scrapy.Field()
    post_offered = scrapy.Field()
    sector_activity = scrapy.Field()
    function = scrapy.Field()
    experience_required = scrapy.Field()
    study_level_required = scrapy.Field()
    contract_type_offered = scrapy.Field()
    Employable = scrapy.Field()
