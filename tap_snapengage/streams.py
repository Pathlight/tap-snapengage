import datetime
import pytz
import singer

from singer.utils import strftime as singer_strftime


LOGGER = singer.get_logger()


class Stream():
    name = None
    replication_method = None
    key_properties = None
    stream = None
    view_id_key = None
    datetime_fields = None
    url = None
    results_key = None

    def __init__(self, client=None, start_date=None):
        self.client = client
        if start_date:
            self.start_date = start_date
        else:
            self.start_date = datetime.datetime.min.strftime('%Y-%m-%d')

    def is_selected(self):
        return self.stream is not None

    def update_bookmark(self, state, value):
        current_bookmark = singer.get_bookmark(state, self.name, self.replication_key)
        if value and value > current_bookmark:
            singer.write_bookmark(state, self.name, self.replication_key, value)

    def transform_value(self, key, value):
        if key in self.datetime_fields and value:
            value = datetime.datetime.utcfromtimestamp(value/1000.0).replace(tzinfo=pytz.utc)
            # reformat to use RFC3339 format
            value = singer_strftime(value)

        return value

    def sync(self, state):
        try:
            sync_thru = singer.get_bookmark(state, self.name, self.replication_key)
        except TypeError:
            sync_thru = self.start_date

        curr_synced_thru = sync_thru

        params = {
                'start': sync_thru,
                'end': datetime.datetime.utcnow().strftime('%Y-%m-%d')
            }

        for row in self.client.paging_get(self.url, self.results_key, params):
            record = {k: self.transform_value(k, v) for (k, v) in row.items()}
            yield(self.stream, record)

            bookmark_timestamp = row.get(self.replication_key)
            bookmark_date = datetime.datetime.utcfromtimestamp(bookmark_timestamp/1000.0).replace(tzinfo=pytz.utc)
            date_for_bookmark = bookmark_date.strftime('%Y-%m-%d')
            curr_synced_thru = max(curr_synced_thru, date_for_bookmark)

        self.update_bookmark(state, curr_synced_thru)


class Logs(Stream):
    name = 'logs'
    replication_method = 'INCREMENTAL'
    key_properties = ['id']
    replication_key = 'created_at_date'
    datetime_fields = set(['created_at_date'])
    url = 'logs'
    results_key = 'cases'


STREAMS = {
    'logs': Logs
}
