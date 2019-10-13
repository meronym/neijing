from os.path import basename, splitext
import re
from urllib.parse import urlsplit, urljoin

from lxml import html
import requests
import requests_cache

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from core.models import Condition, Manifestation, Disharmony


requests_cache.install_cache()


class Command(BaseCommand):
    help = 'Sync with americandragon.com'

    def handle(self, *args, **options):
        index_url = 'https://www.americandragon.com/ConditionsIndex2.html'
        page = requests.get(index_url)
        tree = html.fromstring(page.content)

        conditions = tree.cssselect('table.contentmedium td.rightcolslevel3 > a')
        for c in conditions[:5]:
            url = urljoin(index_url, c.attrib['href'])
            if 'conditions' in url:
                self.parse_condition(url)

    def parse_condition(self, url):
        print(url)
        id = slugify(splitext(basename(urlsplit(url).path))[0])
        page = requests.get(url)
        tree = html.fromstring(page.content)        
        name = tree.cssselect('div#mainbox h1')[0].text
        condition, created = Condition.objects.get_or_create(
            id=id, 
            defaults={'name': name, 'url': url}
        )

        content = tree.cssselect('div#maincontent > div')[0]
        content_class = content.attrib['class']
        divs = tree.cssselect('div#maincontent > div > div')
        for title_div, content_div in self.make_pairs(divs):
            # parse the title
            assert title_div.attrib.get('class', '') == content_class + 'trig'
            dh_title = self.normalize(title_div.cssselect('a')[0].text_content())
            dh_id = slugify(dh_title)
            print(dh_title)
            if dh_title == 'GENERAL':
                obj = condition
            else:
                disharmony, created = Disharmony.objects.get_or_create(
                    id=dh_id,
                    defaults={'name': dh_title}
                )
                obj = disharmony

            # parse the content
            for row in content_div.cssselect('tr'):
                category = self.normalize(row.cssselect('td.leftcollevel3')[0].text_content())
                if category == 'Clinical Manifestations':
                    for item in row.cssselect('td.rightcolslevel3 li'):
                        cm_name = self.normalize(item.text_content())
                        cm_id = Manifestation.get_id(cm_name)
                        cm, created = Manifestation.objects.get_or_create(
                            id=cm_id,
                            defaults={'name': cm_name}
                        )
                        getattr(obj, 'manifestations').add(cm)
                    obj.save()

    def normalize(self, s):
        return re.sub(r'\s+', ' ', s).strip()

    def make_pairs(self, l):
        assert len(l) % 2 == 0
        for i in range(0, len(l) - 1, 2):
            yield l[i:i + 2]
