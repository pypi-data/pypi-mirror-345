from octodns.processor.base import BaseProcessor, ProcessorException

class CloudflareException(ProcessorException):
    pass

class CloudflareProcessor(BaseProcessor):
    def __init__(self, name):
        # TODO: name is DEPRECATED, remove in 2.0
        self.id = self.name = name

    def process_target_zone(self, existing, target):
        for record in existing.records:
          record = record.copy()
          record._type = "CNAME"
          record.values = ["www.example.com.cdn.cloudflare.net."]
          self._owned.add(record)
          existing.add_record(record, replace=True)
        return existing
